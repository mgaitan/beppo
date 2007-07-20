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
from beppo.Constants import CLIENT, ADMIN

class WebClientReport(Resource):
    def __init__(self):
        self.db = DBConnect()
        self.template = WebTemplates()
        Resource.__init__(self)

    def getChild(self, path, request):
        if path == "":
            return self
        else:
            return static.File.childNotFound

    # Muestra un acceso a Listado de datos personales de alumnos (para recortar)
    # y Detalle de horas por alumno
    def render_GET(self, request):
        d = defer.maybeDeferred(getTranslatorFromSession, request)
        d.addCallback(self.doAuthentication, request)
        return server.NOT_DONE_YET

    def doAuthentication(self, trans, request):
        session = request.getSession()
        _ = trans
        # 0) Se empieza la página
        request.write(self.template.startPage(session, _('Reportes de alumnos')))
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
        # La función que procesa e imprime el contenido de la pagina
                    self.printContent(request, d, user_id)
                except ValueError:
                    request.write(self.template.unexpectedArguments(session, \
                        _('user_id deberia ser entero')))
            else:
                request.write(self.template.unexpectedArguments(session, \
                    _('falta el parametro user_id')))
        # 3) Si es Cliente, administra sus propios horarios
        elif session.kind == CLIENT:
            user_id = session.userId
        # La función que imprime el contenido, pero con otros argumentos
            self.printContent(request, d, user_id)
        else:
        # 4) Si no es ni ni Admin, ni Cliente, ni nadie, es alguien que no está
        #    autorizado a administrar alumnos
            request.write(self.template.notAuthorized(session))
        # 5) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return d

    def printContent(self, request, d, userId):
        d.addCallback(lambda a: self.requestData(userId))
        d.addCallback(self.printData, request, userId)
        return d

    def requestData(self, userId):
        query = "select p.first_name, p.last_name, c.organization \
                 from person p, client c where c.id = p.id and p.id = %s"
        d = self.db.db.runQuery(query, (str(userId),))
        return d

    def printData(self, data, request, userId):
        session = request.getSession()
        user = (session.kind == ADMIN) and "?user_id=%s" % (str(userId),) or ""
        _ = session._
        if len(data) != 1:
            string = '<div class="error">' + _('El usuario no existe en el sistema') \
                + '</div>'
        else:
            client = "%s %s (%s)" %(data[0][0], data[0][1], data[0][2])
            string = """<h2>""" + _('Reportes de alumnos de %s') % client \
                + """</h2>""" + _('Seguimiento de alumnos')
            string += "<div id='client_menu'><ul>" + \
            '<li> <a href="/my_pupils_info%s">' % user + \
                _('Datos personales:') +  ' </a> ' + \
                _('Listado de datos personales los alumnos a cargo') + \
                '</li><li> <a href="/my_pupils%s">' % user + _('Horas:') + ' </a> ' + \
                _('Detalle de las horas usadas y disponibles por alumno') + \
                '</li></ul></div>' + '<a href="javascript:history.back()" id="back">' + \
                _('Volver') + '</a>'
        request.write(string)
        return
