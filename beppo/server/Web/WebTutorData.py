# -*- coding: UTF-8 -*-
# This file is part of Beppo.
#
# Beppo is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Beppo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Beppo; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from twisted.web.resource import Resource
from twisted.web import static, server
from twisted.internet import defer
from WebTemplates import WebTemplates
from beppo.server.DBConnect import DBConnect
from twisted.python import log
from mx.DateTime import DateTime
from psycopg import QuotedString
from beppo.server.utils import getTranslatorFromSession, dummyTranslator
from beppo.server.DBConnect import DBConnect
from beppo.Constants import SCH_AI, SCH_PC, HOUR_FORMAT

class WebTutorData(Resource):
    _ = dummyTranslator
    dateToString = {1: _('Domingo'), 2: _('Lunes'), 3: _('Martes'), 4: _('Miercoles'), 5: _('Jueves'), 6: _('Viernes'), 7: _('Sabado'), 8: _('Domingo'), 9: _('Lunes'), 10: _('Martes'), 11: _('Miercoles'), 12: _('Jueves'), 13: _('Viernes'), 14: _('Sabado')}.get
    def __init__(self):
        self.db = DBConnect()
        self.template = WebTemplates()
        Resource.__init__(self)

    def getChild(self, path, request):
        if path == "":
            return self
        else:
            return static.File.childNotFound

    # muestra datos de un tutor (horarios disponibles, nombre, etc.)
    def render_GET(self, request):
        d = defer.maybeDeferred(getTranslatorFromSession, request)
        d.addCallback(self.doAuthentication, request)
        return server.NOT_DONE_YET

    def doAuthentication(self, trans, request):
        session = request.getSession()
        _ = trans
        # 0) Se empieza la página
        request.write(self.template.startPage(session, _('Datos del tutor')))
        d = defer.maybeDeferred(lambda:None)
        # 1) Verificar que esté autenticado ante el sistema
        if not hasattr(session, 'username'):
            request.write(self.template.notAuthenticated(session))
        # 2) debe proveerse el argumento user_id
        elif "user_id" in request.args.keys():
            page = """<h2>""" + _('Informacion del tutor') + """</h2>"""
            d.addCallback(lambda a: request.write(page))
            try:
                user_id = int(request.args['user_id'][0])
        # La función que procesa e imprime el contenido de la pagina
                self.printContent(request, d, user_id)
            except ValueError:
                request.write(self.template.unexpectedArguments(session, \
                  _('user_id deberia ser entero')))
        else:
            request.write(self.template.unexpectedArguments(session, \
              _('falta el parametro user_id')))
        # 5) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return d

    def printContent(self, request, d, userId):
        _ = request.getSession()._
        query = "select p.id, p.first_name, p.last_name from person p, \
            tutor t where t.id = p.id and p.id = %d"
        d.addCallback(lambda a: self.db.db.runQuery(query, (userId,)))
        d.addCallback(self.printData, request)
        query2 = "select name from tutor_subject, subject where \
            fk_subject = subject.id and fk_tutor = %d order by subject.id"
        d.addCallback(lambda a: self.db.db.runQuery(query2, (userId,)))
        d.addCallback(self.printSubject, request)
        query3 = "select t.time_start, t.time_end, t.schedule_type from \
           tutor_schedule t where fk_tutor = %d \
           order by schedule_type, time_start asc"
        d.addCallback(lambda a: self.db.db.runQuery(query3, (userId,)))
        d.addCallback(self.printSchedule, request)
        return d


    def printData(self, rows, request):
        # rows[0]: id
        # rows[1]: first_name
        # rows[2]: last_name
        _ = request.getSession()._
        if len(rows) != 1:
            string = '<div class="error">' + \
               _('El usuario solicitado no existe') + '</div>'
        else:
            last_name = rows[0][2]
            first_name = rows[0][1]

            string = '<table class="table_info" id="tutordata">' + \
                '<tr><th class="header_userinfo">' + _('Nombre:') + \
                '</th><td>%s</td></tr>' % first_name

            string +='<tr><th class="header_userinfo">' + _('Apellido:') + \
                '</th><td>%s</td></tr>' % last_name
        request.write(string)
        return

    def printSubject(self, rows, request):
        # rows contiene una fila por cada materia que ensenha el tutor
        # rows[i][0]: nombre
        _ = request.getSession()._
        string = ''
        if len(rows) != 0:
            string += '<tr><th class="header_userinfo">' + \
                        _('Materias que sabe ensenar:') + '</th><td><ul>'
            for row in rows:
                string += '<li>%s</li>' % row[0]
            string += '</ul>'
        string += '</td></tr>'
        request.write(string)
        return

    def printSchedule(self, rows, request):
        # rows contiene una fila por cada segmento de horairo guardado en
        # tutor_schedule.
        # rows[i][0]: time_start
        # rows[i][1]: time_end
        # rows[i][2]: schedule_type
        _ = request.getSession()._
        ai = ''
        pc = ''
        for row in rows:
            if row[2] == SCH_AI:
                if ai == '':
                    ai += '<tr><th class="header_userinfo">' + \
                        _('Horarios en los que da clases de Acceso Instantaneo:') + \
                           '</th><td><ul>'
                ai += '<li> %s </li>' % self.dateRangeToString(request, row[0], row[1])
            elif row[2] == SCH_PC:
                if pc == '':
                    pc += '<tr><th class="header_userinfo">' + \
                        _('Horarios en los que da clases de Clase Precoordinada:') + \
                           '</th><td><ul>'
                pc += '<li> %s </li>' % self.dateRangeToString(request, row[0], row[1])
        if ai != '':
            ai += '</ul></td></tr>'
        if pc != '':
            pc += '</ul></td></tr>'
        request.write(ai)
        request.write(pc)
        request.write('</table>')
        return

    def dateRangeToString(self, request, date_start, date_end):
        _ = request.getSession()._
        start_day = date_start.day
        end_day = date_end.day

        if self.dateToString(start_day) == self.dateToString(end_day):
            ret = _(self.dateToString(start_day)) + ": " + _('de') + " " + \
                date_start.strftime(HOUR_FORMAT) + " " + _('a') + " " + \
                date_end.strftime(HOUR_FORMAT)
        else:
            ret = _('Desde') + " " + _(self.dateToString(start_day)) + " " + _('a las') + \
                " " + date_start.strftime(HOUR_FORMAT) + " " + _('hasta') + " " + \
                _(self.dateToString(end_day)) + " " + _('a las') + " " + \
                date_end.strftime(HOUR_FORMAT)
        return ret

