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
from beppo.server.utils import getTranslatorFromSession
from beppo.server.DBConnect import DBConnect
from beppo.Constants import CLIENT, ADMIN, DATETIME_FORMAT

class WebMyPupilsInfo(Resource):
    def __init__(self):
        self.db = DBConnect()
        self.template = WebTemplates()
        Resource.__init__(self)

    def getChild(self, path, request):
        if path == "":
            return self
        else:
            return static.File.childNotFound

    # Si estamos autenticados como admin, sirve para ver los alumnos de cualquier cliente
    # Si somos cliente, sólo podremos ver los propios
    def render_GET(self, request):
        d = defer.maybeDeferred(getTranslatorFromSession, request)
        d.addCallback(self.doAuthentication, request)
        return server.NOT_DONE_YET

        msg = """<h2>""" + _('Cuentas de alumnos') + """</h2>"""

    def doAuthentication(self, trans, request):
        session = request.getSession()
        _ = trans
        # 0) Se empieza la página
        request.write(self.template.startPage(session, \
         _('Informacion de cuentas de usuarios')))
        d = defer.maybeDeferred(lambda:None)
        # 1) Verificar que esté autenticado ante el sistema
        if not hasattr(session, 'username'):
            request.write(self.template.notAuthenticated(session))
        # 2) Si es Admin, administra todos los usuarios
        elif session.kind == ADMIN:
        # 2.1) Admin debe proveer el argumento user_id
            if "user_id" in request.args.keys():
                try:
                    user_id = int(request.args['user_id'][0])
                    d.addCallback(lambda a: self.requestData(user_id))
                    d.addCallback(self.printTitle, request)
                    self.printContent(request, d, user_id)
        # La función que procesa e imprime el contenido de la pagina
                except ValueError:
                    request.write(self.template.unexpectedArguments(session, \
                     _('user_id deberia ser entero')))
            else:
                request.write(self.template.unexpectedArguments(session, \
                 _('falta el parametro user_id')))
        # 3) Si es cliente, muestra la información de alumnos propios
        elif session.kind == CLIENT:
            user_id = session.userId
            d.addCallback(lambda a: self.requestData(user_id))
            d.addCallback(self.printTitle, request)
            self.printContent(request, d, user_id)
        else:
        # 4) Si no, es alguien que no está autorizado
            request.write(self.template.notAuthorized(session))
        # 5) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return d

    def requestData(self, user_id):
        query = "select p.first_name, p.last_name, c.organization from person p, \
                 client c where c.id = p.id and p.id = %s"
        d = self.db.db.runQuery(query, (user_id,))
        return d

    def printTitle(self, data, request):
        _ = request.getSession()._
        if len(data) != 1:
            msg = """<h2>""" + _('Cuentas de alumnos') + """</h2>"""
        else:
            client = "%s %s (%s)" % (data[0][0], data[0][1], data[0][2])
            msg = """<h2>""" + _('Cuentas de alumnos de %s') % client + """</h2>"""
        request.write(msg)



    def printContent(self, request, d, userId):
        # 1) Si se envían datos, se actualiza la base primero
        _ = request.getSession()._
        # 3) Se buscan los datos en la base
        query = "select username, password, first_name, last_name, email, \
          ai_available, pc_available, expires from pupil a, person p \
          where p.id = a.id and fk_client= %d"
        d.addCallback(lambda a: self.db.db.runQuery(query, (userId, )))
        # 4) Se imprime los datos
        d.addCallback(self.printForm, request, userId)
        return d


    def printForm(self, rows, request, userId):
        _ = request.getSession()._
        string = ""
        fields = [{'pos': 0, 'desc': _('Nombre de usuario')},
                  {'pos': 1, 'desc': _('Constrasena')},
                  {'pos': 2, 'desc': _('Nombre')},
                  {'pos': 3, 'desc': _('Apellido')},
                  {'pos': 4, 'desc': _('eMail')},
                  {'pos': 5, 'desc': _('Hs. AI restantes')},
                  {'pos': 6, 'desc': _('Hs. CP restantes')},
                  {'pos': 7, 'desc': _('Vencimiento')}]

        if len(rows) == 0:
            string += '<div class="message"><b>' + \
              _('No se registran alumnos a cargo') + '</b></div>'
        else:
            string += _('Informacion de %d alumnos') % len(rows) + ':<br/>'
            for pupil in rows:
                string += '<div class="pupil_info"><ul>'
                for f in fields:
                    string += '<li><b>' + f['desc'] + ': </b> ' + self.getFormat(pupil[f['pos']], f['pos']) + '</li>'
                string += '</ul></div><br/>'

        request.write(string)
        return

    def getFormat(self, data, pos):
        if pos == 7:
            return data.Format(DATETIME_FORMAT)
        else:
            return str(data)
