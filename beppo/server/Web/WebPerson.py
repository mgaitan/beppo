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
from beppo.Constants import TUTOR, ADMIN, CLIENT, PUPIL
from beppo.server.utils import getTranslatorFromSession, dummyTranslator
from beppo.server.DBConnect import DBConnect

from psycopg import QuotedString

class WebPerson(Resource):
    _ = dummyTranslator
    fields = [{'name': 'username', 'pos': 1, 'desc': _('Nombre de usuario'), \
         'required': True, 'isPass': False, 'maxlength': 80, 'query': "person"},
        {'name': 'password', 'pos': 2, 'desc': _('Contrasena'), \
         'required': True, 'isPass': True, 'maxlength': 80, 'query': "person"},
        {'name': 'password2', 'pos': 2, 'desc': _('Repita contrasena'), \
         'required': True, 'isPass': True, 'maxlength': 255, 'query': ""},
        {'name': 'first_name', 'pos': 3, 'desc': _('Nombre'), 'required': True, \
         'isPass': False, 'maxlength': 255, 'query': "person"},
        {'name': 'last_name', 'pos': 4, 'desc': _('Apellido'), 'required': True, \
         'isPass': False, 'maxlength': 255, 'query': "person"},
        {'name': 'email', 'pos': 5, 'desc': _('eMail'), 'required': True, \
         'isPass': False, 'maxlength': 255, 'query': "person"}]

    def __init__(self, table, title, kind, query, empty, xtra_fields):
        _ = dummyTranslator
        self.db = DBConnect()
        self.render_POST = self.render_GET
        self.template = WebTemplates()
        self.table = table
        self.title = title
        self.kind = kind
        self.query = query
        self.empty = empty
        self.fields = WebPerson.fields + xtra_fields
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
        request.write(self.template.startPage(session, self.title))
        d = defer.maybeDeferred(lambda :None)

        if not hasattr(session, 'username'):
            request.write(self.template.notAuthenticated(session))
        elif session.kind == ADMIN:
            try:
                user_id = int(request.args.get('user_id', [-1])[0])
                msg = '<h2>' + _('Datos personales') + '</h2> ' + \
                    _('Recuerde que los campos indicados con <sup>*</sup> son obligatorios')
    # La función que procesa e imprime el contenido de la pagina
                self.printContent(request, d, user_id, msg)
            except ValueError:
                request.write(self.template.unexpectedArguments(session, \
                    _('user_id deberia ser entero')))
        # 3) Administra sus propios datos
        elif session.kind == self.kind:
            user_id = session.userId
            msg = '<h2>' + _('Tus Datos personales') + '</h2>' + \
                _('Recuerda que los campos indicados con <sup>*</sup> son obligatorios')
        # La función que imprime el contenido, pero con otros argumentos
            self.printContent(request, d, user_id, msg)
        else:
        # 4) Es alguien que no está autorizado a administrar materias
            request.write(self.template.notAuthorized(session))
        # 5) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())

        return server.NOT_DONE_YET

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
                    args[value['name']] = args[value['name']][:value['maxlength']]
                    d.addCallback(lambda a: \
                        request.write(self.template.unexpectedArguments(session, \
                        _('Longitud excesiva del argumento \'%s\'') % value['name'])))
            if(args['password'] != args['password2']):
                request.write(self.template.unexpectedArguments(session, \
                    _('Las contrasenas no coinciden')))
        return args

    def printContent(self, request, d, userId, msg):
        # si se estan enviando datos
        _ = request.getSession()._
        args = self.checkRequest(d, request)
        if "submit" in args.keys():
            # si tenemos que actualizar
            if userId > 0:
                person = []
                kind = []
                for field in self.fields:
                    if field['query'] == "person":
                        person.append(field['name'] + " = '" + args[field['name']] + "'")
                    elif field['query'] == self.table:
                        kind.append(field['name'] + " = '" + args[field['name']] + "'")
                person = ", ".join(person)
                kind = ", ".join(kind)
                update_person = "update person set " + person + " where id = %s"
                update_kind = "update " + str(self.table) + " set " + kind + " where id=%s"
                d.addCallback(lambda a: self.db.db.runOperation(update_person, (userId,)))
                d.addCallback(lambda a: self.db.db.runOperation(update_kind, (userId,)))
                d.addCallback(lambda a: request.write("""<div class="message">""" + \
                    _('Datos actualizados con exito') + """</div>""") or userId)
            #antes de insertar debemos chequear si el usuario ya existe
            else:
                query = "select username from person where username = %s"
                username = args['username']
                d.addCallback(lambda a: self.db.db.runQuery(query, (username,)))
                d.addCallback(self._insertDB, request, args)
        else:
            d.addCallback(lambda a:userId)
        d.addCallback(self._requestData, request, msg)

        d.addErrback(self.printError, request)
        d.addCallback(self.printForm, request, args, userId)

    def _requestData(self, userId, request, msg):
        request.write(msg)
        # no se estan mandando datos, se los solicita
        if userId > 0:
            d = self.db.db.runQuery(self.query, (userId,))
            return d
        # ni se mandan ni se solicitan datos (formulario en blanco)
        else:
            return self.getEmptyRow(None, self.empty)

    def printError(self, failure, request):
        """Imprime el error de failure y genera una fila
        vacia para la consulta de la base de datos
        """
        session = request.getSession()
        d = defer.maybeDeferred(lambda :None)
        d.addCallback(lambda a: request.write("""<div class="error"> %s </div>""" % \
            failure.getErrorMessage()))
        d.addCallback(self.getEmptyRow, self.empty)
        return d

    def _insertDB(self, rows, request, args):
        """inserta una persona en la base de datos y llama a la
        función que inserta a la misma persona como self.kind
        """
        session = request.getSession()
        _ = session._
        if len(rows) == 0:
            person_name = []
            person_value = []
            for field in self.fields:
                if field['query'] == "person":
                    person_name.append(field['name'])
                    person_value.append("'" + args[field['name']] + "'")
            person_name = ", ".join(person_name) + ", language, fk_timezone"
            person_value = ", ".join(person_value) + \
              ", " + str(session.locale_id) + ", 2"
            person_op = "insert into person (kind, " + person_name + ") values \
                (%d"+ ", " + person_value + ")"

            d = self.db.db.runOperation(person_op, (self.kind,))
            query = "select id from person where username=%s"
            username = QuotedString(args['username'])
            d.addCallback(lambda a: self.db.db.runQuery(query, (username,)))
            d.addCallback(self.insertKind, request, args)
            return d
        else:
            return failure.Failure(_('El usuario %s ya existe en el sistema') % \
                args['username'])

    def insertKind(self, rows, request, args):
        """Inserta un usuario en la base de datos de acuerdo a los
        datos de rows
        """
        _ = request.getSession()._
        assert(len(rows) == 1)

        kind_name = []
        kind_value = []
        for field in self.fields:
            if field['query'] == self.table:
                kind_name.append(field['name'])
                kind_value.append("'" + args[field['name']] + "'")
        kind_name = ", ".join(kind_name)
        kind_value = ", ".join(kind_value)

        kind_op = "insert into " + self.table + "(id, " + kind_name + ") values \
            (%d"+ ", " + kind_value + ")"
        d = self.db.db.runOperation(kind_op, (rows[0][0],))
        d.addCallback(lambda a: request.write("""<div class="message">""" + \
            _('Usuario ingresado con exito') + """</div>""") or rows[0][0])
        return d

    def getEmptyRow(self, data, size):
        """Devuelve una consulta vacia de tamaño size"""
        return [[""] * size]

    def printCheckArgs(self, request):
        """Para cada diccionario de la lista fields chequea si el campo es
        obligatorio y arma la funcion de JavaScript para el chequeo de datos.
        Agrega a continuacion el chequeo de que las contraseñas coincidan
        """
        _ = request.getSession()._
        page = """
<script type="text/javascript">\n function check_args(form){
message='';"""

        for i in self.fields:
            if i['required']:
                page += 'if(form.%s.value == "") message += "- ' % i['name'] + \
                  _('El campo %s es obligatorio') % _(i['desc']) + '\\n";\n'
        page += 'if(form.password.value != form.password2.value) message += \"- ' + \
            _('Las contrasenas no coinciden') + ' \"; if(message){ alert(\" ' + \
            _('Error en el ingreso de datos:') + """\\n\"+message+\"\\n\");
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
        _ = request.getSession()._
        if len(row) == 0:
            request.write(self.template.unexpectedArguments(request.getSession(), \
                _('El usuario solicitado no existe')))
            row = self.getEmptyRow(None, self.empty)

        self.printCheckArgs(request)
        page = """<form action="" method="post" \
            onsubmit="return check_args(this)"><div> """
        for i in self.fields:
            value = args.get(i['name'], row[0][i['pos']])
            required = i['required'] and "<sup>*</sup>" or ""
            text = i['isPass'] and "password" or "text"
            if value is None:
                value = ''

            page += """<label for='%s'>%s%s: <input type='%s' name='%s'
size="20" value='%s' maxlength="%d" id="%s" /></label><br/>\n""" % (i['name'], _(i['desc']), required, text, i['name'], value, i['maxlength'], i['name'])
        page += """<input type="submit" id="submit" name="submit" value=\"""" + _('Guardar') + """\"/>"""
        if userId > 0:
            page += """<input type="hidden" name="user_id" value='%s'/>""" % userId
        page += """</div></form>"""
        request.write(page)
        return
