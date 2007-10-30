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
from beppo.server.utils import getTranslatorFromSession, dummyTranslator
from beppo.server.DBConnect import DBConnect
from beppo.Constants import TUTOR, PUPIL, ADMIN, CLIENT
import re
import sha

class WebPupilEdit(Resource):
    def __init__(self):
        _ = dummyTranslator
        self.fields = [{'name': 'username', 'pos': 1, 'desc': _('Nombre de usuario'), \
            'required': True, 'type': 'text', 'maxlength': 80, 'query': "person"},
        {'name': 'password', 'pos': 2, 'desc': _('Contrasena'), 'required': False, \
            'type': 'password', 'maxlength': 80, 'query': "person"},
        {'name': 'password2', 'pos': 2, 'desc': _('Repita contrasena'), 'required': False, \
            'type': 'password', 'maxlength': 80, 'query': ""},
        {'name': 'first_name', 'pos': 3, 'desc': _('Nombre'), 'required': True, \
            'type': 'text', 'maxlength': 255, 'query': "person"},
        {'name': 'last_name', 'pos': 4, 'desc': _('Apellido'), 'required': True, \
            'type': 'text', 'maxlength': 255, 'query': "person"},
        {'name': 'email', 'pos': 5, 'desc': _('eMail'), 'required': True, \
            'type': 'text', 'maxlength': 255, 'query': "person"}]
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
        _ = session._
        request.write(self.template.startPage(session, _('Pagina del Alumno')))
        d = defer.maybeDeferred(lambda :None)
        msg = '<h2>' + _('Informacion de alumno') + '</h2>'
        msg += _('Recuerda que los campos indicados con <sup>*</sup> son obligatorios<br>')
        msg += _('Si desea conservar la contraseña actual deje los campos en blanco')
        if not hasattr(session, 'username'):
            request.write(self.template.notAuthenticated(session))
        elif session.kind == ADMIN:
            if 'user_id' in request.args.keys() and 'pupil_id' in request.args.keys():
                try:
                    user_id = int(request.args.get('user_id', [-1])[0])
                    pupil_id = int(request.args.get('pupil_id')[0])
        # La función que procesa e imprime el contenido de la pagina
                    self.printContent(request, d, user_id, pupil_id, msg)
                except ValueError:
                    request.write(self.template.unexpectedArguments(session, \
                        _('user_id y pupil_id deberian ser enteros')))
            else:
                request.write(self.template.unexpectedArguments(session, \
                        _('Faltan argumentos requeridos')))
        # 3) Si es Cliente, ve solo su alumno
        elif session.kind == CLIENT:
            user_id = session.userId
            if 'pupil_id' in request.args.keys():
                try:
                    pupil_id = int(request.args.get('pupil_id')[0])
        # La función que imprime el contenido, pero con otros argumentos
                    self.printContent(request, d, user_id, pupil_id, msg)
                except ValueError:
                    request.write(self.template.unexpectedArguments(session, \
                        _('pupil_id deberia ser entero')))
            else:
                request.write(self.template.unexpectedArguments(session, \
                        _('Faltan argumentos requeridos')))
        else:
        # 4) Si no es ni ni Admin, ni Cliente es alguien que no está
        #    autorizado a modificar alumnos
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
            if(args['password'] != args['password2']):
                request.write(self.template.unexpectedArguments(session, \
                    _('Las contrasenas no coinciden')))
            
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", args['email']) == None:
                request.write(self.template.unexpectedArguments(session, \
                    	_('El email ingresado es incorrecto')))

        return args


    def printContent(self, request, d, userId, pupilId, msg):
        # si se estan enviando datos
        _ = request.getSession()._
        args = self.checkRequest(d, request)
        if "submit" in args.keys():
            # si tenemos que actualizar
            query = "select username from person where username = %s and id <> %d"
            d.addCallback(lambda a: self.db.db.runQuery(query, (args['username'], pupilId)))
            d.addCallback(self._updateUser, request, pupilId, args, userId)
        else:
            d.addCallback(lambda a:userId)
        d.addCallback(self._requestData, request, pupilId, msg)
        d.addErrback(self.printError, request)
        d.addCallback(self.printForm, request, args, userId)

    def _updateUser(self, row, request, pupilId, args, userId):
        _ = request.getSession()._
        if len(row) == 0:
            person = []
            
            #encripto el password
            if args['password']!="":
                args['password'] = sha.new(args['password']).hexdigest()  
            
            for field in self.fields:
                if field['query'] == "person":
                    #si los password estan en blanco no se incluyen en la query de actualizacion                       
                    if not(field['name']=='password' and args['password']==""):
                        person.append(field['name'] + " = '" + args[field['name']] + "'")
            person = ", ".join(person)
            
            update_person = "update person set " + person + " where id = %s"
            d = self.db.db.runOperation(update_person, (pupilId,))
            d.addCallback(lambda a: request.write('<div class="message">' + \
                    _('Datos actualizados con exito') + '</div>') or userId)
        else:
            return failure.Failure(_('El usuario %s ya existe en el sistema') % \
                row[0][0])
        return d

    def _requestData(self, userId, request, pupilId, msg):
        request.write(msg)
        # no se estan mandando datos, se los solicita
        query = "select person.id, username, password, first_name, last_name, \
            email from person, pupil, client where person.id = pupil.id and \
            client.id = pupil.fk_client and client.id = %s and person.id = %s"
        d = self.db.db.runQuery(query, (userId, pupilId))
        return d

    def printError(self, failure, request):
        """Imprime el error de failure y genera una fila
        vacia para la consulta de la base de datos
        """
        session = request.getSession()
        d = defer.maybeDeferred(lambda :None)
        d.addCallback(lambda a: request.write("""<div class="error"> %s </div>""" % \
             failure.getErrorMessage()))
        d.addCallback(self.getEmptyRow, 6)
        return d

    def getEmptyRow(self, data, size):
        """Devuelve una consulta vacia de tamaño size"""
        return [[""] * size]

    def printCheckArgs(self, request):
        """Para cada diccionario de la lista fields chequea si el campo es
        obligatorio y arma la funcion de JavaScript para el chequeo de datos.
        Agrega a continuacion el chequeo de que las contraseñas coincidan
        
        TO-DO: si las contraseñas estan en blanco, ignorar el update. 
        
        """
        _ = request.getSession()._
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
        message += \"- """ + _('Las contrasenas no coinciden') + """\";\n"""

        page += """if(!isEmailAddress(form.email))
        message += \"- """ + _('El email ingresado es incorrecto') + """\";


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
        if len(row) == 0:
            request.write(self.template.unexpectedArguments(session, \
            _('El usuario solicitado no existe')))
            row = self.getEmptyRow(None, 6)

        self.printCheckArgs(request)
        page = """<form action="" method="post" \
            onsubmit="return check_args(this)"><div> """
        for i in self.fields:
            value = args.get(i['name'], row[0][i['pos']])
            required = i['required'] and "<sup>*</sup>" or ""
            text = i['type']

            #dejo los campos password en blanco por defecto.
            if value is None or i['name']=='password' or i['name']=='password2':
                value = ''

            page += """<label for="%s">%s%s: <input type="%s" name="%s"
    size="20" value="%s" maxlength="%d" id="%s" /></label><br/>\n""" % \
        (i['name'], _(i['desc']), required, text, i['name'], value, i['maxlength'], i['name'])
        request.write(page)
        request.write("""<input type="submit" name="submit" id="submit" value=\"""" + \
            _('Guardar') + """\"/>""")
        if userId > 0:
            request.write("""<input type="hidden" name="user_id" value="%s"/>""" % userId)
        request.write("""</div></form>""")
        return

