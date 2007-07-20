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
from WebGetUserInfo import WebGetUserInfo
from twisted.web import static, server
from twisted.internet import defer
from twisted.python import log
from psycopg import QuotedString
from beppo.server.utils import getTranslatorFromSession
from beppo.server.DBConnect import DBConnect
import gettext

class WebLogin(Resource):
    def __init__(self):
        self.db = DBConnect()
        self.template = WebTemplates()
        self.render_POST = self.render_GET
        Resource.__init__(self)

    def getChild(self, path, request):
        if path == "":
            return self
        else:
            return static.File.childNotFound

    def render_GET(self, request):
        session = request.getSession()
        _ = getTranslatorFromSession(request)

        d = defer.maybeDeferred(lambda: None)
        if hasattr(session, 'username'):
            request.write(self.template.startPage(session, _('Iniciar Sesion')))
            request.write('<div class="message">' + \
                _('La sesion ya estaba iniciada') + '</div>')
        elif "username" in request.args.keys() and "pwd" in request.args.keys():
            query = "select username, id, kind, first_name, \
                last_name from person where username = %s and password = %s"
            username = QuotedString(request.args['username'][0])
            pwd = QuotedString(request.args['pwd'][0])
            d = self.db.db.runQuery(query, (username, pwd))
            d.addCallback(self.authenticateUser, request)
        else:
            request.write(self.template.startPage(session))
            request.write("""<h2>""" + _('Inicio de Sesion') + """</h2> \
            <form action="" method="post"><div>""" + _('Nombre de Usuario') \
            + """: <label for="username"><input type="text" size="5" name="username" \
            id="username"/></label><br/>""" + _('Contrasena') \
            + """: <label for="pwd"><input type="password" size="5" name="pwd" \
            id="pwd"/></label><br/><input id="submit" type="submit" value=\"""" + \
            _('Entrar!') + """\"/></div></form>""")

        d.addCallback(lambda a:request.write(self.template.finishPage(session)))
        d.addCallback(lambda a:request.finish())
        d.addErrback(log.err)
        return server.NOT_DONE_YET

    def authenticateUser(self, rows, request):
        session = request.getSession()
        _ = session._ # Ya sabemos que está

        if len(rows) == 1:
            row = rows[0]
            session.username = row[0]
            session.userId = row[1]
            session.kind = row[2]
            session.name = row[3]
            session.lastname = row[4]
            d = defer.maybeDeferred(getTranslatorFromSession, request, refresh=True)
            d.addCallback(self.welcomeMessage, request, row[3], row[4])
            return d
        elif len(rows) == 0:
            request.write(self.template.startPage(session))
            request.write('<div class="warning"><h2>' + \
                _('Nombre de Usuario o Contrasena incorrecta') + '</h2>' + \
                _('Por favor verifique su nombre de usuario y contrasena.') + '<br/>' + \
                _('Recuerde que su nombre de usuario y contrasena son sensibles a mayusculas y minusculas!') + '</div>')
        else:
            request.write(self.template.startPage(session))
            request.write('<div class="error">' + \
                _('Existen varios usuarios en el sistema con las mismas credenciales. Por favor notifique al administrador del sistema') + '</div>')
        return

    def welcomeMessage(self, trans, request, first, last):
        session = request.getSession()
        _ = trans
        d = defer.maybeDeferred(lambda: None)
        d.addCallback(lambda a: request.write(self.template.startPage(session)))
        d.addCallback(lambda a: request.write('<div class="message">' + \
            _('Bienvenido') + ', %s %s</div>' % (first, last)))
        d.addCallback(lambda a: self.template.homePageContent(session))
        d.addCallback(request.write)
        d.addCallback(lambda a: self.template.commonInfo(trans))
        d.addCallback(request.write)
        return d

class WebLogout(Resource):
    def __init__(self):
        self.template = WebTemplates()
        Resource.__init__(self)

    def getChild(self, path, request):
        if path == "":
            return self
        else:
            return static.File.childNotFound

    def render_GET(self, request):
        session = request.getSession()
        _ = getTranslatorFromSession(request)

        if hasattr(session, 'username'):
            del(session.username)
            del(session.userId)
            del(session.kind)
            del(session.name)
            del(session.lastname)
            del(session.locale)
            request.write(self.template.startPage(session, _('Cerrar Sesion')))
            request.write('<div class="message"><h2>' +
                 _('La sesion ha sido cerrada') +
                 '</h2>' + _('Que tenga un buen dia.') + '</div>')
        else:
            request.write(self.template.startPage(session))
            request.write('<div class="warning"><h2>' +
                _('Sesion inexistente') + '</h2>' +
                _('Debe iniciar una sesion antes de cerrarla!') + '</div>')
        request.write(self.template.finishPage(session))
        del(session._)
        request.finish()
        return server.NOT_DONE_YET

