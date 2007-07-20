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
from beppo.server.utils import getTranslatorFromSession, dummyTranslator
from beppo.Constants import TUTOR, ADMIN, PUPIL, DATETIME_FORMAT, ARCHIVE_DIR
from beppo.server.DBConnect import DBConnect
from mx import DateTime

class WebArchive(Resource):
    _ = dummyTranslator

    def __init__(self):
        self.db = DBConnect()
        self.template = WebTemplates()
        Resource.__init__(self)

    def getChild(self, path, request):
        if path == "":
            return self
        else:
            return static.File.childNotFound

    #muestra las pizarras guardadas en la base de datos
    def render_GET(self, request):
        d = defer.maybeDeferred(getTranslatorFromSession, request)
        d.addCallback(self.doAuthentication, request)
        return server.NOT_DONE_YET

    def doAuthentication(self, trans, request):
        session = request.getSession()
        _ = trans
        # 0) Se empieza la página
        request.write(self.template.startPage(session, \
          _('Archivo de pizarras')))
        d = defer.maybeDeferred(lambda:None)
        # 1) Verificar que esté autenticado ante el sistema
        if not hasattr(session, 'username'):
            request.write(self.template.notAuthenticated(session))
        # 2) Si es Admin, administra todos los usuarios
        else:
            msg = _('Este es el archivo de las pizarras correspondientes a las clases dadas en el sistema. Puedes bajar cualquiera de las pizarras haciendo click en el nombre del archivo. La informacion de la fecha que aparece corresponde a la fecha de finalizacion de la clase')
            msg = '<h2>' + _('Archivo') + '</h2>' + msg + '<br/>'
            d.addCallback(lambda a: request.write(msg))
        # La función que imprime el contenido, pero con otros argumentos
            self.printContent(request, d)
        # 5) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return d


    def printContent(self, request, d):
        """Consulta las sesiones del tutor user_id en la
         base de datos y las manda a imprimir
        """
        query = "select a.filename, s.fk_tutor, p.username, s.fk_pupil, p2.username, \
                 a.comment, s.time_end from archive a left join session s \
                 on (s.id = a.fk_session) left join person p on (p.id = s.fk_tutor) \
                 left join person p2 on (p2.id = s.fk_pupil)"
        d.addCallback(lambda a: self.db.db.runQuery(query))
        d.addCallback(self.printData, request)
        return d

    def printData(self, rows, request):
        # cada row de rows trae:
        # [0]: filename
        # [1],[2]: tutor id, tutor username
        # [3],[4]: pupil id, pupil username
        # [5]: comentario
        # [6]: fecha y hora de fin de esa session
        _ = request.getSession()._
        if len(rows) == 0:
            string = "<div class='client_info'>" + _('El archivo esta vacio') + '</div>'
        else:
            string = _('Se encontraron %d archivos:') % len(rows)
            string += """
<table class="table_list" id="archive">
 <tr>
  <th class="header_list">""" + _('Archivo') + """</th>
  <th class="header_list">""" + _('Tutor') + """</th>
  <th class="header_list">""" + _('Alumno') + """</th>
  <th class="header_list">""" + _('Fecha') + """</th>
  <th class="header_list">""" + _('Comentario') + """</th>
 </tr>
"""
            for row in rows:
                tutor_name = (row[2] is not None) and \
                    "<a href='/userinfo?user_id=%s&amp;kind=%d'>%s</a>" % \
                    (row[1], TUTOR, row[2]) or _('El tutor ya no esta en el sistema')
                pupil_name = (row[4] is not None) and \
                    "<a href='/userinfo?user_id=%s&amp;kind=%d'>%s</a>" % \
                    (row[3], PUPIL, row[4]) or _('El alumno ya no esta en el sistema')
                date = (row[6] is not None) and row[6].Format(DATETIME_FORMAT) or ""
                string += """
<tr class="row_list">
 <td><a href="%s">%s</a></td>
 <td>%s</td>
 <td>%s</td>
 <td>%s</td>
 <td>%s</td>
</tr>""" % ("board_archive/" + row[0], row[0], tutor_name, pupil_name, date, row[5])
            string += """</table>"""
        request.write(string)
        return
