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
from DBDelete import DBDelete
from beppo.Constants import CLIENT, ADMIN, PUPIL
from beppo.Constants import DATETIME_FORMAT

class WebMyPupils(Resource):
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

    def doAuthentication(self, trans, request):
        session = request.getSession()
        _ = trans
        # 0) Se empieza la página
        request.write(self.template.startPage(session, \
         _('Informacion de cuentas de usuarios')))
        d = defer.maybeDeferred(lambda:None)
        # 1) Verificar que esté autenticado ante el sistema
        msg = """<h2>""" + _('Cuentas de alumnos') + """</h2>"""
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
        # 3) Si es cliente, muestra la información de alumnos propios
        elif session.kind == CLIENT:
            user_id = session.userId
        # La función que imprime el contenido, pero con otros argumentos
            self.printContent(request, d, user_id)
        else:
        # 4) Si no, es alguien que no está autorizado
            request.write(self.template.notAuthorized(session))
        # 5) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return d

    def printContent(self, request, d, userId):
        _ = request.getSession()._
        # 2) Si se envían datos, se actualiza la base primero
        d.addCallback(lambda a: self.requestData(userId))
        d.addCallback(self.printTitle, request)
        if "del" in request.args.keys():
            try:
                to_delete = int(request.args["del"][0])
                query3 = "select id from pupil where id = %d and fk_client = %d"
                d.addCallback(lambda a: self.db.db.runQuery(query3, (to_delete, userId)))
                d.addCallback(self.checkUser, userId, request)
            except ValueError:
                d.addCallback(lambda a: \
                 request.write(self.template.unexpectedArguments(session, \
                 _('user_id deberia ser entero'))))
        # 3) Se buscan los datos en la base
        query = "select c.ai_available, c.pc_available, count(p.id) \
          from client c left join pupil p on (p.fk_client = c.id) \
          where c.id = %d group by c.ai_available, c.pc_available"
        d.addCallback(lambda a: self.db.db.runQuery(query, (userId, )))
        d.addCallback(self.printClientInfo, request)
        query2 = "select a.id, last_name, first_name, ai_available, ai_total, \
           pc_available, pc_total, expires from person p, pupil a \
           where p.id = a.id and fk_client = %d"
        d.addCallback(lambda a: self.db.db.runQuery(query2, (userId, )))
        # 4) Se imprime los datos
        d.addCallback(self.printForm, request, userId)
        return d

    def checkUser(self, rows, userId, request):
        session = request.getSession()
        _ = session._
        d = defer.maybeDeferred(lambda: None)
        if len(rows) != 1:
            d.addCallback(lambda a: \
                 request.write(self.template.unexpectedArguments(session, \
                 _('No es alumno del cliente'))))
        else:
            erase = DBDelete(self.db)
            to_delete = str(rows[0][0])
            d.addCallback(lambda a: erase.deletePupil(to_delete))
            d.addCallback(lambda a: request.write('<div class="message">' + \
             _('El usuario ha sido borrado correctamente') + '</div>'))
        return d

    def requestData(self, userId):
        query = "select p.first_name, p.last_name, c.organization \
                 from person p, client c where c.id = p.id and p.id = %s"
        d = self.db.db.runQuery(query, (str(userId),))
        return d

    def printTitle(self, data, request):
        _ = request.getSession()._
        if len(data) == 1:
            client = "%s %s (%s)" % (data[0][0], data[0][1], data[0][2])
            msg = """<h2>""" + _('Cuentas de alumnos de %s') % client + """</h2>"""
        else:
            msg = """<h2>""" + _('Cuentas de alumnos') + """</h2>"""
        request.write(msg)
        return

    def printForm(self, rows, request, userId):
        """ recibimos [(first_name, last_name, ai_total, pc_total,
        ai_available, pc_available, expires)]
        """
        session = request.getSession()
        _ = session._

        string = ""

        if len(rows) != 0:
            taia = tait = tpca = tpct = 0
            string += """
<script type="text/javascript">
function del_confirm(pupil){
    return confirm(\"""" + _('Esta seguro de borrar el alumno') + """ \"+pupil+"?");
}
</script>
"""
            string += """<br/>
<table class="table_list" id="pupil_info">
 <tr>
  <th class="icon_list"></th>
  <th class="icon_list"></th>
  <th class="header_list">""" + _('Alumno') + """</th>
  <th class="header_list">""" + _('Horas AI (restan/total)') + """</th>
  <th class="header_list">""" + _('Horas PC (restan/total)') + """</th>
  <th class="header_list">""" + _('Vencimiento') + """</th>
 </tr>
"""
            for r in rows:
                aia = self.getFloatFormat(r[3])
                ait = self.getFloatFormat(r[4])
                pca = self.getFloatFormat(r[5])
                pct = self.getFloatFormat(r[6])
                taia += aia
                tait += ait
                tpca += pca
                tpct += pct
                link = (session.kind == ADMIN) and "&amp;user_id=%s" % (str(userId),) or ""
                string += """
<tr class="row_list">
 <td><a href="pupil_edit?pupil_id=%s%s" class="link_image"><img src="/static/graphics/modify.gif" width="16" height="16" alt=\"""" % (r[0], link) + \
  _('Modificar') + """\" title=\"""" + _('Modificar') + """\"/></a></td>
 <td><a href="?del=%s%s" class="link_image" onclick="return del_confirm('%s')"><img src="/static/graphics/delete.gif"  width="16" height="16" alt=\"""" % (r[0], link, r[2] + " " + r[1]) + _('Borrar alumno') + """\" title=\"""" + _('Borrar alumno') + """\"/></a></td>

 <td><a href="/userinfo?user_id=%s&amp;kind=%d">%s, %s</a></td>
 <td>%.1f/%.1f</td>
 <td>%.1f/%.1f</td>
 <td>%s</td>
</tr>
""" % (r[0], PUPIL, r[1], r[2], aia, ait, pca, pct, self.getDateFormat(r[7]))
            string += """
<tr>
 <td class="last_row"></td>
 <td class="last_row"></td>
 <td class="last_row">Total</td>
 <td class="last_row">%.1f/%.1f</td>
 <td class="last_row">%.1f/%.1f</td>
 <td class="last_row"></td>
</tr>
</table>""" % (taia, tait, tpca, tpct)

        user = (session.kind == ADMIN) and "?user_id=" + str(userId) or ""
        string += "<a href='/new_pupil%s'>" % user + _('Agregar alumnos') + "</a>"
        string += "<a href='javascript:history.back()' id='back'>" + _('Volver') + "</a>"
        request.write(string)
        return

    def printClientInfo(self, rows, request):
        _ = request.getSession()._
        fields = [{'pos': 0, 'desc': _('Horas AI disponibles')},
                  {'pos': 1, 'desc': _('Horas CP disponibles')},
                  {'pos': 2, 'desc': _('Cantidad de alumnos')}]
        if len(rows) != 1:
            string = '<div class="message">' + _('No se registran datos para el usuario') \
               + '</div>'
        else:
            string = '<div class="client_info">' + \
                _('Informacion de alumnos y horas:') + '<ul>'
            for row in rows:
                for i in fields:
                    string += '<li><b>' + i['desc'] + ': </b>' + str(row[i['pos']]) \
                      + '</li>'
            string += '</ul></div>'
        request.write(string)
        return

    def getFloatFormat(self, value):
        """esta puede eliminarse cuando la base de datos ponga valores por defecto
        a ai_available y pc_available"""
        return (value != None) and value or 0.0

    def getDateFormat(self, value):
        """esta puede eliminarse cuando la base de datos ponga valores por defecto
        a expires"""
        return (value != None) and value.Format(DATETIME_FORMAT) or "-"
