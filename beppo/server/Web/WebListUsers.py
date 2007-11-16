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
from psycopg import QuotedString
from DBDelete import DBDelete
from beppo.server.utils import getTranslatorFromSession
from beppo.Constants import TUTOR, PUPIL, ADMIN, CLIENT
from beppo.Constants import ITEMS_PAG
from beppo.server.DBConnect import DBConnect

class WebListUsers(Resource):
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
    # Mostrará una lista de clientes, tutores, etc. de acuerdo a lo que se le pase por
    # direccion
    def render_GET(self, request):
        d = defer.maybeDeferred(getTranslatorFromSession, request)
        d.addCallback(self.doAuthentication, request)
        return server.NOT_DONE_YET

    def doAuthentication(self, trans, request):
        session = request.getSession()
        _ = trans
        # Se escribe el comienzo de la página
        request.write(self.template.startPage(session, \
             _('Listado de usuarios del sistema')))
        d = defer.maybeDeferred(lambda: None)
        keys = request.args.keys()
        # Si no es admin o no esta loggeado, no seguimos
        if not hasattr(session, 'username') or session.kind != ADMIN:
            request.write(self.template.notAuthenticated(session))
        else:
            if "kind" in request.args.keys():
                try:
                    kind = int(request.args['kind'][0])
                    if "del" in keys:
                        erase = DBDelete(self.db)
                        client = QuotedString(request.args['del'][0])
                        d.addCallback(lambda a: erase.deletePerson(client, kind))
                        d.addCallback(lambda a: request.write('<div class="message">' + \
                         _('El usuario ha sido borrado correctamente') + '</div>'))
                    elif ("ia" in keys or "pc" in keys) and "user_id" in keys and \
                        not ("ia" in keys and "pc" in keys):
                        hours = ("ia" in keys) and "ia" or "pc"
                        user = QuotedString(request.args['user_id'][0])
                        cant = float(request.args[hours][0].replace(",", "."))
                        d.addCallback(lambda a: self.setClientHours(user, cant, hours))
                        d.addCallback(lambda a: request.write('<div class="message">' + \
                         _('Se ha actualizado correctamente la cantidad de horas  disponibles') + '</div>'))
                    d.addCallback(lambda a: self.listClient(request))
                except ValueError:
                        d.addCallback(lambda a: \
                         request.write(self.template.unexpectedArguments(session, \
                         _('Argumento no valido'))))
            else:
                d.addCallback(lambda a: \
                 request.write(self.template.unexpectedArguments(session, \
                _('Falta el argumento \'kind\''))))
        # Se escribe el final de la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return d

    def setClientHours(self, user, cant, hours):
        if hours == "pc":
            query = "update client set pc_available = %f where id=%s """
        else:
            query = "update client set ai_available = %f where id=%s """
        d = self.db.db.runOperation(query, (cant, user))
        return d

    def listClient(self, request):
        """Busca la información para todos los usuarios del tipo dado por la request
        y llama a printContent con el resultado de la busqueda
        """
        kind = int(request.args['kind'][0])
        try:
            pag = int(request.args['pag'][0])
        except:
            pag = 0
        
        if kind == TUTOR:
            cols = "tutor.id, username, first_name, last_name"
            fromWhere = "from tutor, person where tutor.id = person.id"
            order = "order by id asc"
        elif kind == PUPIL:
            cols = "p.id, p1.username, p1.first_name, p1.last_name, p2.username, p.fk_client"
            fromWhere = "from person p1, person p2, pupil p where p.id = p1.id and p2.id = p.fk_client"
            order = "order by p.id asc"
        elif kind == CLIENT:
            cols = "client.id, username, first_name, \
             last_name, organization, client.ai_available, client.pc_available, \
             count(pupil.id)"
            fromWhere = "from client left join pupil on \
             (pupil.fk_client = client.id) left join person on (client.id = person.id) \
             group by client.id, person.username, person.first_name, person.last_name, \
             client.organization, client.ai_available, client.pc_available"
            order = "order by id asc"
        elif kind == ADMIN:
            cols = "person.id, username, first_name, last_name"
            fromWhere = "from person  where kind = %s" % kind
            order = "order by id asc"
        else: # kind desconocido
            cols = "person.id, username, first_name, last_name"
            fromWhere = "from person where kind = %s" % kind
            order = "order by id asc" 
        
        cols += ", (SELECT count(*) %s)" % fromWhere
        query = "SELECT %s %s %s LIMIT %d OFFSET %d" % (cols, fromWhere, order, ITEMS_PAG, ITEMS_PAG*pag)
        print repr(query)
        d = self.db.db.runQuery(query)            
        d.addCallback(self.printContent, kind, request)
        return d

    def printContent(self, rows, kind, request):
        """Lista todos los usuarios del sistema del typo kind (de acuerdo al resultado
        de la consulta rows
        """
        _ = request.getSession()._
        if len(rows) != 0:

            def paginacion():
                total = rows[0][-1:][0] #la ultima columna es el total de datos para la consulta
                try:            
                    actual = int(request.args['pag'][0])
                except:
                    actual = 0
                if total > ITEMS_PAG:
                    request.write('<div> <strong>' + _('Página:') + '</strong>')
                    for pagina in range(int(total/ITEMS_PAG)+1):
                        tip = "href"
                        if pagina == actual:
                            tip = "id"
                        link = "<a %s='/list?kind=%d&pag=%d'>%d</a>&nbsp;" % (tip,kind,pagina,pagina+1)
                        request.write(link)
                    request.write('</div><br />')
                    
            
            request.write('<h2>' + _('Usuarios del sistema:') + '</h2>')
            if kind == TUTOR:
                request.write("""
<script type="text/javascript">
function del_confirm(tutor){
    return confirm(\"""" + _('Esta seguro de borrar el tutor') + """ \"+tutor+"?");
}
</script>
""")
                request.write("""
<table class="table_list" id="usersinsystem">
 <tr>
  <th class="icon_list"></th>
  <th class="icon_list"></th>
  <th class="icon_list"></th>
  <th class="icon_list"></th>
  <th class="header_list">""" + _('Usuario') + """</th>
  <th class="header_list">""" + _('Apellido') + """</th>
  <th class="header_list">""" + _('Nombre') + """</th>
 </tr>""")
                for i in range(len(rows)):
                # row tiene todos los datos de los usuarios del tipo kind
                    request.write("""<tr>
<td class="row_list"><a href="tutor?user_id=%s" class="link_image"><img src="/static/graphics/modify.gif"  width="16" height="16" alt=\"""" % rows[i][0] + _('Modificar') + """\" title=\"""" + _('Modificar') + """\"/></a></td>
<td class="row_list"><a href="?kind=%s&amp;del=%s" class="link_image" onclick="return del_confirm('%s')"><img src="/static/graphics/delete.gif" width="16" height="16" alt=\"""" % (TUTOR, rows[i][0], rows[i][1]) + _('Borrar') + """\" title=\"""" + _('Borrar') + """\"/></a></td>
<td class="row_list"><a href="/schedules?user_id=%s" class="link_image"><img src="/static/graphics/schedule.gif" width="16" height="16" alt=\"""" % rows[i][0] + _('Asignar horas') + """\" title=\"""" + _('Asignar horas') + """\"/></a></td>
<td class="row_list"><a href="/subjects?user_id=%s" class="link_image"><img src="/static/graphics/subjects.gif" width="16" height="16" alt=\"""" % rows[i][0] + _('Asignar materias') + """\" title=\"""" + _('Asignar materias') + """\"/></a></td>
<td class="row_list"><a href="/userinfo?user_id=%s&amp;kind=%d">%s</a></td>
<td class="row_list">%s</td>
<td class="row_list">%s</td>
</tr>""" % (rows[i][0], TUTOR, rows[i][1], rows[i][3], rows[i][2]))
                request.write('</table>')
                paginacion()
                request.write('<a href="/tutor"> ' + _('Agregar tutores') +'</a>')

            elif kind == PUPIL:
                request.write("""
<script type="text/javascript">
function del_confirm(pupil){
    return confirm(" """ + _('Esta seguro de borrar el alumno') + """ "+pupil+"?");
}
</script>""")
                request.write("""
<table class="table_list" id="usersinsystem">
 <tr>
  <th class="icon_list"></th>
  <th class="icon_list"></th>
  <th class="header_list">""" + _('Usuario') + """</th>
  <th class="header_list">""" + _('Apellido') + """</th>
  <th class="header_list">""" + _('Nombre') + """</th>
  <th class="header_list">""" + _('Cliente') + """</th>
 </tr>""")
                for i in range(len(rows)):
                    request.write("""<tr>
<td class="row_list"><a href="pupil_edit?pupil_id=%s&amp;user_id=%s" class="link_image"><img src="/static/graphics/modify.gif" width="16" height="16" alt=\"""" % (rows[i][0], rows[i][5]) + \
_('Modificar') + """\" title=\"""" + _('Modificar') + """\"/></a></td>
<td class="row_list"><a href="?kind=%s&amp;del=%s" class="link_image" onclick="return del_confirm('%s')"><img src="/static/graphics/delete.gif" width="16" height="16" alt=\"""" %(PUPIL, rows[i][0], rows[i][1]) + _('Borrar') + """\" title=\"""" + _('Borrar') + """\"/></a></td>
<td class="row_list"><a href="/userinfo?user_id=%s&amp;kind=%d">%s</a></td>
<td class="row_list">%s</td>
<td class="row_list">%s</td>
<td class="row_list">%s</td></tr>""" %(rows[i][0], PUPIL, rows[i][1], rows[i][3], rows[i][2], rows[i][4]))
                request.write('</table>')
                paginacion()

            elif kind == CLIENT:
                request.write("""
<script type="text/javascript">
function del_confirm(client, pupils){
    message = \"""" + _('Esta seguro de borrar el cliente') + """\"+client+"?\\n";
    if (pupils > 0){
        message += \"(""" + _('Aun tiene') + """ \" + pupils + \" """+_('alumno(s) a cargo') + """)\";
    }
    return confirm(message);
}

function ask_hours(client, hour_type){
    var hours = NaN;
    while((!hours && hours != 0) && hours != null){
        hours = prompt(" """ + _('Indique la cantidad de horas a asignar:') + """ ", "100");
        if(hours != null) hours = parseFloat(hours);
    }
    if(parseFloat(hours) >= 0){
        var url = "?kind=%s&amp;" + hour_type + "=" + parseFloat(hours) + "&amp;user_id=" +client;
        location.href = url;
    }
}
</script>
""" % CLIENT)
                request.write("""
<table class="table_list" id="usersinsystem">
 <tr>
  <th class="icon_list"></th>
  <th class="icon_list"></th>
  <th class="icon_list"></th>
  <th class="icon_list"></th>
  <th class="header_list">""" + _('Usuario') + """</th>
  <th class="header_list">""" + _('Apellido') + """</th>
  <th class="header_list">""" + _('Nombre') + """</th>
  <th class="header_list">""" + _('Organizacion') + """</th>
  <th class="icon_list"></th>
  <th class="header_list">""" + _('Horas disponibles (AI)') + """</th>
  <th class="header_list">""" + _('Horas disponibles (CP)') + """</th>
  <th class="icon_list"></th>
 </tr>""")
                for i in range(len(rows)):
                    request.write("""<tr>
<td class="row_list"><a href="client?user_id=%s" class="link_image"><img src="/static/graphics/modify.gif" width="16" height="16" alt=\"""" % (rows[i][0],) + _('Modificar') + """\" title=\"""" + _('Modificar') + """\"/></a></td>
<td class="row_list"><a href="?kind=%d&amp;del=%s" onclick="return del_confirm('%s', %d)" class="link_image"><img src="/static/graphics/delete.gif" width="16" height="16" alt=\"""" % (CLIENT, rows[i][0], rows[i][1], rows[i][7]) + _('Borrar') + """\" title=\"""" + _('Borrar') + """\"/></a></td>
<td class="row_list"><a href="new_pupil?user_id=%s" class="link_image"><img src="/static/graphics/board.gif" width="16" height="16" alt=\"""" % (rows[i][0],) + _('Agregar alumno') + """\" title=\"""" + _('Agregar alumno') + """\"/></a></td>
<td class="row_list"><a href="report?user_id=%s" class="link_image"><img src="/static/graphics/board.gif" width="16" height="16" alt=\"""" % (rows[i][0],) + _('Ver alumnos') + """\" title=\"""" + _('Ver alumnos') + """\"/></a></td>
<td class="row_list"><a href="/userinfo?user_id=%s&amp;kind=%d">%s</a></td>
<td class="row_list">%s</td>
<td class="row_list">%s</td>
<td class="row_list">%s</td>
<td class="row_list"><a href="" class="link_image" onclick="ask_hours(\'%s\', \'ia\'); return false;"><img src="/static/graphics/schedule.gif" width="16" height="16" alt=\"""" % (rows[i][0], CLIENT, rows[i][1], rows[i][3], rows[i][2], rows[i][4], rows[i][0]) + _('Asignar horas') + """\" title=\"""" + _('Asignar horas') + """\"/></a></td>
<td class="row_list">%s</td>
<td class="row_list">%s</td>
<td class="row_list"><a href="" class="link_image" onclick="ask_hours(\'%s\', \'pc\'); return false;"><img src="/static/graphics/schedule.gif" width="16" height="16" alt=\"""" % (self.hoursFormat(rows[i][5]), self.hoursFormat(rows[i][6]), rows[i][0]) + _('Asignar horas') + """\" title=\"""" + _('Asignar horas') + """\"/></a></td></tr>""")
                request.write('</table>')
                paginacion()
                request.write('<a href="/client">' + _('Agregar clientes') + '</a>')

            elif kind == ADMIN:
                request.write("""
<table class="table_list" id="usersinsystem">
 <tr>
  <th class="header_list"></th>
  <th class="header_list">""" + _('Usuario') + """</th>
  <th class="header_list">""" + _('Apellido') + """</th>
  <th class="header_list">""" + _('Nombre') + """</th>
 </tr>""")
                for i in range(len(rows)):
                    request.write("""<tr>
<td class="row_list"><a href="editadmin?user_id=%s" class="link_image"><img src="/static/graphics/modify.gif" width="16" height="16" alt=\"""" % (rows[i][0],) + _('Modificar') + """\" title=\"""" + _('Modificar') + """\"/></a></td>                    
<td class="row_list"><a href="/userinfo?user_id=%s&amp;kind=%d">%s</a></td>
<td class="row_list">%s</td>
<td class="row_list">%s</td>
</tr>"""% (rows[i][0], ADMIN, rows[i][1], rows[i][3], rows[i][2]))
                request.write('</table>')
                paginacion()
                request.write('<a href="/editadmin"> ' + _('Agregar Administrador') +'</a>')            

            else:
                for i in range(len(rows)):
                    request.write('<li>' + _('Usuarios') + '%s %s, %s</li>' % (rows[i][0], rows[i][4], rows[i][5]))

        else:
            request.write('<h2> ' + _('No hay usuarios de este tipo en el sistema') + '</h2>')
        
        
        request.write('<a href="/admin" id="back"> ' + _('Volver') + '</a>')
        return

    def hoursFormat(self, hours):
        return (hours == None) and "0.0" or hours


