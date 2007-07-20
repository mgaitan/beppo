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
from WebTemplates import WebTemplates
from twisted.web import static, server
from twisted.internet import defer
from twisted.python import log, failure
from beppo.Constants import TUTOR, ADMIN, CLIENT, PUPIL
from beppo.server.utils import getTranslatorFromSession, dummyTranslator, setSessionLocale
from beppo.server.DBConnect import DBConnect
from psycopg import QuotedString

class WebSettings(Resource):
    _ = dummyTranslator
    def __init__(self):
        _ = dummyTranslator
        self.db = DBConnect()
        self.render_POST = self.render_GET
        self.template = WebTemplates()
        Resource.__init__(self)

    def getChild(self, path, request):
        if path == "":
            return self
        else:
            return static.File.childNotFound

    def render_GET(self, request):
        d = defer.maybeDeferred(getTranslatorFromSession, request)
        d.addCallback(self.doAuthentication, request)
        return server.NOT_DONE_YET

    def doAuthentication(self, trans, request):
        session = request.getSession()
        _ = trans
        d = defer.maybeDeferred(lambda: None)
        if not hasattr(session, 'username'):
            d.addCallback(lambda a: request.write(self.template.notAuthenticated(session)))
        elif session.kind == ADMIN:
            try:
                user_id = int(request.args.get('user_id', None)[0])
            except:
                user_id = session.userId
        else:
            user_id = session.userId
        message = False
        if "submit" in request.args.keys():
            try:
                time = int(request.args.get('fk_timezone')[0])
                lang = int(request.args.get('language')[0])
            except ValueError, TypeError:
                request.write(self.template.unexpectedArguments(session, \
                    _('Argumento no valido')))
            message = True
            query = "select * from language, timezone where \
                language.id = %d and timezone.id = %d"
            d.addCallback(lambda a: self.db.db.runQuery(query, (lang, time)))
            d.addCallback(self.updateDBAndSession, request, user_id)
        d.addCallback(self.printStartPage, request, message)
        d.addCallback(lambda a: self.printContent(request, user_id))
        # 4) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())

        return d

    def printStartPage(self, data, request, message):
        session = request.getSession()
        _ = session._
        request.write(self.template.startPage(session, _('Preferencias')))
        if message:
            request.write("""<div class="message">""" + \
                _('Datos actualizados con exito') + """</div>""")

    def updateDBAndSession(self, rows, request, userId):
        """rows[0..2] -> language[id,name,locale]
           rows[3..5] -> timezone[id,name,gmtoffset]
        """
        session = request.getSession()
        if len(rows) != 1:
            _ = session._
            request.write(self.template.unexpectedArguments(session, \
                    _('Argumento no valido')))
        else:
            time = rows[0][0]
            lang = rows[0][3]
            setSessionLocale(session, rows[0][0], rows[0][2])
            update_person = "update person set language = %d, \
                fk_timezone = %d where id = %s"
            d = self.db.db.runOperation(update_person, (time, lang, userId,))
            return d

    def printContent(self, request, userId):
        # si se estan enviando datos
        session = request.getSession()
        _ = session._
        msg = '<h2>' + _('Preferencias') + '</h2> ' + \
          _('Indica tu preferencia de idioma y zona horaria')
        request.write(msg)
        # consulto los datos del usuario que me piden
        query = "select fk_timezone, language from person where id = %s"
        d = self.db.db.runQuery(query, (userId,))
        d.addErrback(self.printError, request)
        d.addCallback(self.printForm, request, userId)
        return d


    def getEmptyRow(self, data, size):
        """Devuelve una consulta vacia de tamaño size"""
        return [[""] * size]

    def printError(self, failure, request):
        """Imprime el error de failure y genera una fila
        vacia para la consulta de la base de datos
        """
        session = request.getSession()
        d = defer.maybeDeferred(lambda :None)
        d.addCallback(lambda a: request.write("""<div class="error"> %s </div>""" % \
            failure.getErrorMessage()))
        d.addCallback(self.getEmptyRow, 2)
        return d

    def printForm(self, row, request, userId):
        """row[0] -> fk_timezone
           row[1] -> language
        """
        _ = request.getSession()._
        if len(row) == 0:
            request.write(self.template.unexpectedArguments(request.getSession(), \
                _('El usuario solicitado no existe')))
            row = self.getEmptyRow(None, 2)

        page = """<form action="" method="post"><div> """
        request.write(page)
        query = "select id, name, gmtoffset from timezone"
        query2 = "select id, name, locale from language"

        d = self.db.db.runQuery(query)
        d.addCallback(self.printTimezone, row[0][0], request)
        d.addCallback(lambda a: self.db.db.runQuery(query2))
        d.addCallback(self.printLanguage, row[0][1], request)

        page = """<input type="submit" id="submit" name="submit" value=\"""" + _('Guardar') + """\"/>"""
        if userId > 0:
            page += """<input type="hidden" name="user_id" value='%s'/>""" % userId
        page += """</div></form>"""
        d.addCallback(lambda a: request.write(page))
        return d


    def printTimezone(self, rows, selected, request):
        #row tiene i's talque:
        # i[0] id
        # i[1] name
        # i[2] offset
        _ = request.getSession()._
        select = """<label for="fk_timezone">""" + _('Zona Horaria:') + """ <select \
            name="fk_timezone" id="fk_timezone">"""
        for i in rows:
            value = i[0]
            default = (i[0] == selected) and "selected='selected'" or ""
            label = i[1]+" (GMT +" + str(i[2]) + ")"
            select += """<option id="tz_%s" value="%s" %s>%s</option>""" % \
                    (value, value, default, label)
        select += """</select></label><br/>"""
        request.write(select)
        return


    def printLanguage(self, rows, selected, request):
        #row tiene i's talque:
        # i[0] id
        # i[1] name
        # i[2] locale
        _ = request.getSession()._
        select = """<label for="language">""" + _('Idioma:') + """ <select \
            name="language" id="language">"""
        for i in rows:
            value = i[0]
            default = (i[0] == selected) and "selected='selected'" or ""
            label = i[1]
            select += """<option id="l_%s" value="%s" %s>%s</option>""" % \
                    (value, value, default, label)
        select += """</select></label><br/>"""
        request.write(select)
        return
