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
from psycopg import QuotedString
from mx import DateTime
from beppo.server.utils import getTranslatorFromSession, dummyTranslator
from beppo.server.DBConnect import DBConnect
from beppo.Constants import TUTOR, PUPIL, ADMIN, CLIENT
from beppo.Constants import EXPIRE_TIME
import sha
import re

class WebPupilInsert(Resource):
    def __init__(self):
        _ = dummyTranslator
        self.fields = [{'name': 'username', 'pos': 1, 'desc': _('Nombre de usuario'), \
            'required': True, 'type': 'text', 'maxlength': 80, 'query': "person"},
        {'name': 'password', 'pos': 2, 'desc': _('Contrasena'), 'required': True, \
            'type': 'password', 'maxlength': 80, 'query': "person"},
        {'name': 'password2', 'pos': 2, 'desc': _('Repita contrasena'), 'required': True, \
            'type': 'password', 'maxlength': 80, 'query': ""},
        {'name': 'first_name', 'pos': 3, 'desc': _('Nombre'), 'required': True, \
            'type': 'text', 'maxlength': 255, 'query': "person"},
        {'name': 'last_name', 'pos': 4, 'desc': _('Apellido'), 'required': True, \
            'type': 'text', 'maxlength': 255, 'query': "person"},
        {'name': 'email', 'pos': 5, 'desc': _('eMail'), 'required': True, \
            'type': 'text', 'maxlength': 255, 'query': "person"},
        {'name': 'ai_total', 'pos': 6, 'desc': _('Horas de AI'), 'required': True, \
            'type': 'text', 'maxlength': 255, 'query': "pupil"},
        {'name': 'pc_total', 'pos': 7, 'desc': _('Horas de CP'), 'required': True, \
            'type': 'text', 'maxlength': 255, 'query': "pupil"}]
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
        request.write(self.template.startPage(session, _('Pagina del Alumno')))
        d = defer.maybeDeferred(lambda :None)
        msg = '<h2>' + _('Nuevo alumno') + '</h2> ' + \
          _('Recuerde que los campos indicados con <sup>*</sup> son obligatorios')
        if not hasattr(session, 'username'):
            request.write(self.template.notAuthenticated(session))
        elif session.kind == ADMIN:
            if "user_id" in request.args.keys():
                try:
                    user_id = int(request.args.get('user_id', [-1])[0])
        # La función que procesa e imprime el contenido de la pagina
                    self.printContent(request, d, user_id, msg)
                except ValueError:
                    request.write(self.template.unexpectedArguments(session, \
                        _('user_id deberia ser entero')))
            else:
                request.write(self.template.unexpectedArguments(session, \
                    _('Falta el argumento user_id')))
        elif session.kind == CLIENT:
            user_id = session.userId
        # La función que imprime el contenido, pero con otros argumentos
            self.printContent(request, d, user_id, msg)
        else:
        # 4) Si no es ni ni Admin, ni Cliente es alguien no autorizado a ver alumnos
            request.write(self.template.notAuthorized(session))
        # 5) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())

        return d

    def checkRequest(self, d, request):
        session = request.getSession()
        _ = session._
        args = dict([(i, request.args[i][0]) for i in request.args.keys()])
        if "submit" in request.args.keys():
            for value in self.fields:
                if value['name'] not in args.keys():
                    args[value['name']] = ''
                    d.addCallback(lambda a: \
                        request.write(self.template.unexpectedArguments(session, \
                        _('Falta el argumento \'%s\'') % value['name'])))
                elif len(args[value['name']]) > value['maxlength']:
                    args[value['name']] = (args[value['name']][:value['maxlength']])
                    d.addCallback(lambda a: \
                        request.write(self.template.unexpectedArguments(session, \
                        _('Longitud excesiva del argumento \'%s\'') % value['name'])))
            if args['password'] != args['password2']:
                request.write(self.template.unexpectedArguments(session, \
                    _('Las contrasenas no coinciden')))

            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", args['email']) == None:
                request.write(self.template.unexpectedArguments(session, \
                                    _('El email ingresado es incorrecto')))
            try:
                args['ai_total'] = float(args['ai_total'])
                args['pc_total'] = float(args['pc_total'])
            except ValueError:
                request.write(self.template.unexpectedArguments(session, \
                    _('El argumento de Hora debe ser numerico')))
        return args

    def printContent(self, request, d, userId, msg):
        _ = request.getSession()._
        args = self.checkRequest(d, request)
        d.addCallback(lambda a: request.write(msg))
        #chequeamos que el cliente exista
        query = "select ai_available, pc_available from client where id = %d"
        d.addCallback(lambda a: self.db.db.runQuery(query, (userId,)))
        d.addCallback(self._checkAndInsert, request, userId, args)
        d.addErrback(self.printError, request)
        d.addCallback(self.printForm, request, args, userId)


    def _printAvailable(self, row, request):
        _ = request.getSession()._
        string = _('Detalle de horas disponibles:') + "<br/>" + \
          "<ul id='client_info'><li>" + _('Horas AI disponibles:') + \
          ' %.1f' % row[0][0] + "</li><li>" + _('Horas CP disponibles:') + \
          ' %.1f' % row[0][1] + "</li></ul>"
        d = defer.maybeDeferred(lambda: request.write('<div class="client_info">' + \
          string + '</div>') or row)
        return d

    def printError(self, failure, request):
        """Imprime el error de failure y genera una fila
        vacia para la consulta de la base de datos
        """
        session = request.getSession()
        d = defer.maybeDeferred(lambda :None)
        d.addCallback(lambda a: request.write("""<div class="error"> %s </div>""" % \
             failure.getErrorMessage()))
        d.addCallback(self.getEmptyRow, 8)
        return d


    def _checkAndInsert(self, rows, request, userId, args):
        _ = request.getSession()._
        if len(rows) == 1:
            ai_available = rows[0][0]
            pc_available = rows[0][1]

            if 'submit' in request.args.keys():
                username = QuotedString(args['username'])
                ai_asked = args['ai_total']
                pc_asked = args['pc_total']
                if (ai_asked <= ai_available and pc_asked <= pc_available):
                    query = "select username from person where username = %s"
                    d = self.db.db.runQuery(query, (username,))
                    d.addCallback(self._insertDB, request, userId, args)
                else:
                    return failure.Failure(_('Ha solicitado mas horas de las que dispone'))
            else:
                d = defer.maybeDeferred(lambda: self.getEmptyRow(None, 8))
        else:
            return failure.Failure(_('El cliente solicitado no existe'))
        return d

    def _insertDB(self, rows, request, userId, args):
        """inserta una persona en la base de datos y llama a la
        función que inserta a la misma persona como alumno
        """
        _ = request.getSession()._
        if len(rows) != 0:
            return failure.Failure(_('El usuario ya existe en el sistema'))
        else:
            person_name = []
            person_value = []
            for field in self.fields:
                if field['query'] == "person":
                    person_name.append(field['name'])
                    person_value.append("'" + args[field['name']] + "'")
            person_name = ", ".join(person_name) + ", language, fk_timezone"
            person_value = ", ".join(person_value) + ", " + str(PUPIL) + ", 2"
            person_op = "insert into person (kind, " + person_name + ") values \
                (%d"+ ", " + person_value + ")"
            d = self.db.db.runOperation(person_op, (PUPIL,))
            query = "select id from person where username = %s"
            username = QuotedString(args['username'])
            d.addCallback(lambda a: self.db.db.runQuery(query, (username,)))
            d.addCallback(self.insertPupil, request, userId, args)
        return d


    def insertPupil(self, rows, request, userId, args):
        """Inserta un alumno en la base de datos de acuerdo a los
        datos de rows
        """
        _ = request.getSession()._
        assert(len(rows) == 1)
        pupil_name = []
        pupil_value = []
        expire_time = DateTime.now() + DateTime.RelativeDate(**EXPIRE_TIME)
        for field in self.fields:
            if field['query'] == "pupil":
                pupil_name.append(field['name'])
                pupil_value.append("'" + str(args[field['name']]) + "'")
        pupil_name = ", ".join(pupil_name) + ", fk_client, ai_available, pc_available, expires"
        pupil_value = ", ".join(pupil_value) + ", %d, %f, %f, '%s'" % (userId, args['ai_total'], args['pc_total'], expire_time)
        pupil_op = "insert into pupil (id, " + pupil_name + ") values \
            (%d" + ", " + pupil_value + ")"
        client_op = "update client set ai_available = ai_available - %f, pc_available = pc_available - %f where id = %s"
        d = self.db.db.runOperation(pupil_op, (rows[0][0],))
        d.addCallback(lambda a: self.db.db.runOperation(client_op, (args['ai_total'], args['pc_total'], args['user_id'])))
        d.addCallback(lambda a: request.write('<div class="message">' + \
            _('Usuario ingresado con exito') + '</div>') or self.getEmptyRow(None, 8))
        return d

    def getEmptyRow(self, data, size):
        """Devuelve una consulta vacia de tamaño size"""
        return [[""] * size]

    def printCheckArgs(self, hours, request):
        """Para cada diccionario de la lista fields chequea si el campo es
        obligatorio y arma la funcion de JavaScript para el chequeo de datos.
        Agrega a continuacion el chequeo de que las contraseñas coincidan
        """
        _ = request.getSession()._
        ai = hours[0][0]
        pc = hours[0][1]
        page = """
<script type="text/javascript" src="/static/js/valid.js"></script>

<script type="text/javascript">\n function check_args(form){
message='';"""

        for i in self.fields:
            if i['required']:
                page += """if(form.%s.value == "")
                message += "- """ % i['name'] + \
                _('El campo %s es obligatorio') % _(i['desc']) + """\\n";\n"""
        page += """if(form.password.value != form.password2.value)
        message += \"- """ + _('Las contrasenas no coinciden') + """\\n";
if(!isNaN(parseFloat(form.ai_total.value))){
    form.ai_total.value = parseFloat(form.ai_total.value);
}else{
    message += \"- """ + _('El campo Horas AI disponibles debe ser numerico') + """\\n";
}
if(form.ai_total.value > """ + str(ai) + """){
    message += \"- """ + _('Se ha excedido en las Horas AI asignadas') + """\\n";
}
if(form.ai_total.value < 0){
    message += \"- """ + _('El campo Horas de AI debe ser positivo') + """\\n";
}
if(!isNaN(parseFloat(form.pc_total.value))){
    form.pc_total.value = parseFloat(form.pc_total.value);
}else{
    message += \"- """ + _('El campo Horas PC disponibles debe ser numerico') + """\\n";
}
if(form.pc_total.value > """ + str(pc) + """){
    message += \"- """ + _('Se ha excedido en las Horas PC asignadas') + """\\n";
}
if(form.pc_total.value < 0){
    message += \"- """ + _('El campo Horas de PC debe ser positivo') + """\\n";
}
if(form.pc_total.value == 0 && form.ai_total.value == 0){
    message += \"- """ + _('Debe asignarle horas al alumno') + """\\n";
}

if(!isEmailAddress(form.email)){
        message += \"- """ + _('El email ingresado es incorrecto') + """\\n";
}





if(message){
    alert(" """ + _('Error en el ingreso de datos:') + """\\n"+message+"\\n");
    return false;
}else{
    return true;
}
}
</script>
"""
        request.write(page)
        return

    def printForm(self, row, request, args, userId):
        """Para cada diccionario de la lista fields arma el campo del
        formulario correspondiente.
        """
        session = request.getSession()
        _ = session._
        d = self.db.db.runQuery("select ai_available, pc_available from client where id = %d", (userId,))
        d.addCallback(self._printAvailable, request)
        d.addCallback(self.printCheckArgs, request)
        page = """<form action="" method="post" \
            onsubmit="return check_args(this)"><div> """
        for i in self.fields:
            value = row[0][i['pos']]
            required = i['required'] and "<sup>*</sup>" or ""
            text = i['type']
            page += """<label for="%s">%s%s: <input type="%s" name="%s"
    size="20" value="%s" maxlength="%d" id="%s" /></label><br/>\n""" % \
        (i['name'], _(i['desc']), required, text, i['name'], value, i['maxlength'], i['name'])
        d.addCallback(lambda a: request.write(page))
        d.addCallback(lambda a: request.write("""<input type="submit" \
            name="submit" id="submit" value=\"""" + _('Guardar') + """\"/>"""))
        if userId > 0:
            d.addCallback(lambda a: request.write("""<input type="hidden" name="user_id" value="%s"/>""" % userId))
        d.addCallback(lambda a: request.write("""</div></form>"""))
        return d

