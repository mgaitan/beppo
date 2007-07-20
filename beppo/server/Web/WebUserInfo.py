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
from twisted.enterprise import adbapi
from twisted.internet import defer
from beppo.server.DBConnect import DBConnect
from WebTemplates import WebTemplates
from WebGetUserInfo import WebGetUserInfo
from psycopg import QuotedString
from beppo.Constants import CLIENT, PUPIL, ADMIN, TUTOR
from beppo.server.utils import getTranslatorFromSession
import cgi

class WebUserInfo(Resource):
    def __init__(self):
        self.db = DBConnect()
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
        info = WebGetUserInfo(self.db, session)
        # 0) Se empieza la página
        request.write(self.template.startPage(session, _('Informacion de usuario')))
        d = defer.maybeDeferred(lambda:None)
        # 1) Verificar que esté autenticado ante el sistema
        if not hasattr(session, 'username'):
            request.write(self.template.notAuthenticated(session))
        # 2) Si es Admin, puede ver todos los usuarios
        elif "user_id" in request.args.keys() and "kind" in request.args.keys():
            try:
                user_id = int(request.args['user_id'][0])
                kind = int(request.args['kind'][0])
                msg = '<h2>' + _('Informacion de usuario') + '</h2>'
                d.addCallback(lambda a: info.getUserInfo(user_id, kind))
            except ValueError:
                request.write(self.template.unexpectedArguments(session, \
                    _('Argumento no valido')))
                user_id = kind = msg = None
                d.addCallback(lambda a: None)
            d.addCallback(self.printContent, request, d, user_id, kind, session, msg)
        else:
            request.write(self.template.unexpectedArguments(session, \
                _('Falta algun argumento')))
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return d


    def printContent(self, data, request, d, userId, kind, session, msg):
        d.addCallback(lambda a: request.write(msg))
        d.addCallback(lambda a: request.write(data))
        return

