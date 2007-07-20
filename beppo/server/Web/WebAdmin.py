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
from twisted.python import log
from beppo.server.utils import getTranslatorFromSession
from beppo.server.DBConnect import DBConnect
from beppo.Constants import TUTOR, CLIENT, PUPIL, ADMIN

class WebAdmin(Resource):
    def __init__(self):
        self.db = DBConnect()
        self.template = WebTemplates()
        Resource.__init__(self)

    def getChild(self, path, request):
        if path == "":
            return self
        else:
            return static.File.childNotFound

    # A esta pagina sólo se podrá acceder si tenemos permisos de administrador.
    # Mostrará un link para ver las listas de: clientes, tutores y alumnos
    def render_GET(self, request):
        d = defer.maybeDeferred(getTranslatorFromSession, request)
        d.addCallback(self.doAuthentication, request)
        return server.NOT_DONE_YET

    def doAuthentication(self, trans, request):
        _ = trans
        session = request.getSession()
        d = defer.maybeDeferred(lambda: None)
        # Se escribe el comienzo de la página
        request.write(self.template.startPage(session, _('Administracion de usuarios')))
        # Si no es admin o no esta loggeado, no seguimos
        if not hasattr(session, 'username') or session.kind != ADMIN:
            d.addCallback(lambda a: request.write(self.template.notAuthenticated(session)))
        else:
            d.addCallback(lambda a: self.sysStatus(request))
            d.addCallback(self.printContent, request)
        # Se escribe el final de la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return server.NOT_DONE_YET


    def sysStatus(self, request):
        """Busca la información acerca de la cantidad de usuarios,
        alumnos y tutores que tiene el sistema.
        """
        query = "select count(*), kind from person group by kind order by kind asc"
        d = self.db.db.runQuery(query)
        return d

    def printContent(self, rows, request):
        _ = request.getSession()._
        subjects = _('Listado de materias disponibles y cantidad de tutores que la tienen como seleccionada para poder dar clases. Tambien se pueden realizar alta y bajas de materias')
        tutors = _('Tiempo que los tutores pasaron en el sistema, dividido por tipos de conexion. Detalle de las sesiones de cada tutor. Se puede elegir un rango de fechas para visualizar')
        rooms = _('Informacion de las aulas del sistema, cantidad de alumnos en el aula, los tutores que se encuentran a cargo y las materias que estan brindando. Listado de aulas que deberian estar abiertas y no lo estan, con la informacion del tutor correspondiente')
        board = _('Archivos en formato PDF (Portable Document Format) que contienen las pizarras de las clases brindadas por los tutores del sistema')
        admin = [{'id': 'subject_admin', 'item': _('Administrar materias'), \
                  'title': _('Materias'), 'alt': _('Materias'), 'desc': subjects, \
                  'link': '/subject_admin', 'image': '/static/graphics/subjects.gif', \
                  'width': '16', 'height': '16'},
         {'id': 'tutor_info', 'item': _('Informacion de tutores'), \
          'title': _('Tutores'), 'alt': _('Tutores'), 'desc': tutors, \
          'link': '/tutor_info', 'image': '/static/graphics/subjects.gif', \
          'width': '16', 'height': '16'},
         {'id': 'roominfo', 'item': _('Informacion de aulas'), \
          'title': _('Aulas'), 'alt': _('Aulas'), 'desc': rooms, \
          'link': '/roominfo', 'image': '/static/graphics/tutor_info.gif', \
          'width': '16', 'height': '16'},
         {'id': 'tutor', 'item': _('Agregar tutores'), 'title': _('Tutores'), \
          'alt': _('Tutores'), 'desc': _('Agregar nuevos tutores al sistema'), \
          'link': '/tutor', 'image': '/static/graphics/mortarboard.gif', \
          'width': '16', 'height': '16'},
         {'id': 'client', 'item': _('Agregar clientes'), 'title': _('Clientes'), \
          'alt': _('Clientes'), 'desc': _('Agregar nuevos clientes al sistema'), \
          'link': '/client', 'image': '/static/graphics/buddy.gif', \
          'width': '16', 'height': '16'},
         {'id': 'archive', 'item': _('Archivo de pizarras'), 'title': _('Archivo'), \
          'alt': _('Archivo'), 'desc': board, 'link': '/archive', \
          'image': '/static/graphics/ps.png', 'width': '16', 'height': '16'}]

        page = ''
        if len(rows) != 0:
            page += '<h2>' + _('Administracion del sistema:') \
                + '</h2><div style="padding-left: 40px"><table id="admin_table" border="0">'
            for item in admin:
                page += """<tr><td><a href='%s' id='%s'><img src='%s' width='%s'
                 height='%s' alt='%s' title='%s'/></a><a href='%s'>%s</a>
                 </td><td>%s</td> </tr>""" \
                 % (item['link'], item['id'], item['image'], item['width'], \
                    item['height'], item['alt'], item['title'], item['link'], \
                    item['item'], item['desc'])
            page += """</table></div><h2>""" + _('Informacion de usuarios en el sistema:') \
                    + """</h2><div style="padding-left: 40px" id='users'>""" \
                    + """<ul id="systemusers">"""

            for i in range(len(rows)):
                # row[0] es la cantidad de row[1] que hay en la base
                if rows[i][1] == TUTOR:
                    page += '<li>%d <a href="/list?kind=%d">' % (rows[i][0], TUTOR) \
                            + _('Tutores') + '</a> ' + _('en el sistema') + '</li>'
                elif rows[i][1] == PUPIL:
                    page += '<li>%d <a href="/list?kind=%d">' % (rows[i][0], PUPIL) \
                            + _('Alumnos') + ' </a> ' + _('en el sistema') + '</li>'
                elif rows[i][1] == CLIENT:
                    page += '<li>%d <a href="/list?kind=%d">' % (rows[i][0], CLIENT) \
                            + _('Clientes') + ' </a> ' + _('en el sistema') + '</li>'
                elif rows[i][1] == ADMIN:
                    page += '<li>%d <a href="/list?kind=%d">' % (rows[i][0], ADMIN) \
                            + _('Administradores') + ' </a> ' + _('en el sistema') + '</li>'
                else:
                    page += '<li>%d' % rows[i][0] + \
                            _('Usuarios no categorizados en el sistema') + '</li>'
            page += '</ul></div>'
        else:
            page += '<h2>' + _('No hay usuarios en el sistema') + '</h2>'
        request.write(page)
        return
