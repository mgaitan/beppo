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
from DBDelete import DBDelete
from psycopg import QuotedString
from beppo.server.utils import getTranslatorFromSession
from beppo.Constants import ADMIN
from beppo.server.DBConnect import DBConnect
from beppo.Constants import ITEMS_PAG

class WebSubjectAdmin(Resource):
    def __init__(self):
        self.db = DBConnect()
        self.template = WebTemplates()
        Resource.__init__(self)

    def getChild(self, path, request):
        if path == "":
            return self
        else:
            return static.File.childNotFound

    # Si estamos autenticados como admin, sirve para ver, agregar y borrar materias
    def render_GET(self, request):
        d = defer.maybeDeferred(getTranslatorFromSession, request)
        d.addCallback(self.doAuthentication, request)
        return server.NOT_DONE_YET

    def doAuthentication(self, trans, request):
        session = request.getSession()
        _ = trans
        # 0) Se empieza la página
        request.write(self.template.startPage(session, _('Administracion de materias')))
        d = defer.maybeDeferred(lambda:None)
        # 1) Verificar que esté autenticado ante el sistema
        if not hasattr(session, 'username'):
            request.write(self.template.notAuthenticated(session))
        # 2) Si es Admin, administra todos los usuarios
        elif session.kind == ADMIN:
            msg = '<h2>' + _('Administracion de Materias') + '</h2>' + _('Estas son las materias disponibles en el sistema. Desde aqui se pueden agregar y borrar materias') + '<br/>'
        # La función que procesa e imprime el contenido de la pagina
            self.printContent(request, d, msg)
        else:
        # 4) Si no es Admin, es alguien que no está autorizado a
        # administrar materias
            request.write(self.template.notAuthorized(session))
        # 5) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return d

    def printContent(self, request, d, msg):
        # 1) Si se envían datos, se agrega
        _ = request.getSession()._
        if "submit" in request.args.keys():
            op = "insert into subject (name) values (%s)"
            name = QuotedString(request.args['name'][0])
            d.addCallback(lambda a: self.db.db.runOperation(op, (name,)))
            d.addCallback(lambda a: request.write("""<div class="message"><h2>""" + \
             _('Materia agregada') + '</h2>' + \
             _('La materia ha sido guardada correctamente') + """</div>"""))
        elif "del" in request.args.keys():
            # si nos piden borrar, llamamos al metodo de borrar materias de
            # DBDelete, el cual borra la materia si no tiene referencias
            # y si no devuelve False
            erase = DBDelete(self.db)
            delete = int(request.args['del'][0])
            d.addCallback(lambda a: erase.deleteSubject(delete))
            d.addCallback(self.printSubjectDelete, request)
        # 2) Se imprime un mensaje de bienvenida configurable
        d.addCallback(lambda a: request.write(msg))
        # 3) Se buscan los datos nuevos en la base
        op = "select s.id, s.name, count(fk_subject) from subject s \
              left join tutor_subject t on (s.id = t.fk_subject) \
              group by s.id, s.name order by name asc"
        d.addCallback(lambda a: self.db.db.runQuery(op))
        d.addCallback(self.printForm, request)
        return d

#return confirm("¿Está seguro de borrar la materia" + subject + "?\n (" + tutors + " " + "tutores la tienen como seleccionada)");

    def printForm(self, rows, request):
        """recibe el resultado de una consulta de materias e imprime la tabla que las
           muestra y permite borrarlas. ademas imprime un formulario para agregar
           materias (y el codigo JavaScript de chequeo correspondiente)
        """
        _ = request.getSession()._
        string = """
<script type="text/javascript">
function del_confirm(subject, tutors){
    string = \" """ + _('Esta seguro de borrar la materia') + """ \"+subject+\"?\\n\";
    if(tutors == 1){
        string += \"(""" + _('1 tutor la tiene como seleccionada') + """)\";
    }else if(tutors > 0){
        string += \"(\" + tutors + \" \" + \"""" + \
        _('tutores la tienen como seleccionada') + """)\";
    }
    return confirm(string);
}
</script>

<br/>
<table class="table_list" id="subjects">
 <tr>
  <th class="icon_list"></th>
  <th class="header_list">""" + _('Materia') + """</th>
  <th class="header_list">""" + _('# Tutores') + """</th>
 </tr>
"""
        for i in range(len(rows)):
            string += """
<tr>
<td class="row_list"><a href="?del=%d" onclick="return del_confirm('%s', %d)" class="link_image"><img src="/static/graphics/delete.gif" width="16" height="16" alt=\"""" %  (rows[i][0], rows[i][1], rows[i][2])+ _('Borrar') + """\" title=\"""" + _('Borrar') + """\"/></a></td>
<td class="row_list">%s</td>
<td class="row_list">%d</td>
</tr>""" % (rows[i][1], rows[i][2])
        string += """
</table>
<br/>
<script type="text/javascript">
function check_args(form){
    if(form.name.value == ""){
        alert(\"""" + _('El nombre de la materia no puede ser vacio') + """\");
        return false;
    }else{
        return true;
    }
}
</script>
<form action="" method="get" onsubmit="return check_args(this)" ><div>
<input type="text" name="name" id="name" size="20"/>
<input type="submit" name="submit" id="submit" value=\"""" + _('Insertar') + """\" size="15"/></div>
</form>
"""
        request.write(string)
        return

    def printSubjectDelete(self, result, request):
        """Chequea el resultado de la llamada al metodo de DBDelete para el borrado
           de una materia. Imprime el mensaje correspondiete, de acuerdo si la materia
           ha sido o no borrada
        """
        _ = request.getSession()._
        if result == False:
            msg = """<div class="error"><h2>""" + _('Materia no borrada') + """</h2>""" + \
                _('Existen clases por darse o preguntas por contestarse para esta materia')\
                 + """</div>"""
        else:
            msg = """<div class="message"><h2>""" + _('Materia borrada') + """</h2>""" + \
                _('La materia ha sido borrada correctamente') + """</div>"""
        request.write(msg)
