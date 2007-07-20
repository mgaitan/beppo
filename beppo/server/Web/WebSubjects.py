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
from beppo.Constants import TUTOR, ADMIN
from beppo.server.utils import getTranslatorFromSession
from beppo.server.DBConnect import DBConnect

class WebSubjects(Resource):
    def __init__(self):
        self.db = DBConnect()
        self.template = WebTemplates()
        Resource.__init__(self)

    def getChild(self, path, request):
        if path == "":
            return self
        else:
            return static.File.childNotFound

    # Si estamos autenticados como admin, sirve para modificar las materias de cualquier tutor.
    # Si somos tutor, sirve para modificar solo los propios.
    def render_GET(self, request):
        d = defer.maybeDeferred(getTranslatorFromSession, request)
        d.addCallback(self.doAuthentication, request)
        return server.NOT_DONE_YET

    def doAuthentication(self, trans, request):
        session = request.getSession()
        _ = trans
        # 0) Se empieza la página
        request.write(self.template.startPage(session, _('Modificacion de materias')))
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
                    msg = '<h2>' + _('Administracion de materias') + '</h2>' + \
                     _('Selecciona las materias que el tutor sepa ensenar, para actualizar los datos en el sistema.')
        # La función que procesa e imprime el contenido de la pagina
                    self.printContent(request, d, user_id, msg)
                except ValueError:
                    request.write(self.template.unexpectedArguments(session, \
                       _('user_id deberia ser entero')))
            else:
                request.write(self.template.unexpectedArguments(session, \
                   _('falta el parametro user_id')))
        # 3) Si es Tutor, administra sus propias materias
        elif session.kind == TUTOR:
            user_id = session.userId
            msg = '<h2>' + _('Seleccion de materias') + '</h2>' + \
                _('Selecciona las materias que sepas ensenar, para actualizar tus datos en el sistema.')
        # La función que imprime el contenido, pero con otros argumentos
            self.printContent(request, d, user_id, msg)
        else:
        # 4) Si no es ni ni Admin, ni Tutor, ni nadie, es alguien que no está
        #    autorizado a administrar materias
            request.write(self.template.notAuthorized(session))
        # 5) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return d

    def printContent(self, request, d, userId, msg):
        _ = request.getSession()._
        # 1) Si se envían datos, se actualiza la base primero
        if "submit" in request.args.keys():
            op = "delete from tutor_subject where fk_tutor = %d"
            d.addCallback(lambda a: self.db.db.runOperation(op, (userId, )))
            for sbj in request.args.get('sbj', []):
                try:
                    sbj = int(sbj)
                    d.addCallback(self.addSubject, userId, sbj)
                except ValueError: # Alguien editó la url a mano?
                    d.addCallback(lambda a: \
                     request.write(self.template.unexpectedArguments(session, + \
                        _('sbj deberia tomar valores enteros.'))))
            d.addCallback(lambda a: request.write('<div class="message"><h2>' + \
                _('Cambios guardados.') + '</h2>' + \
                _('Se guardaron los cambios correctamente') + '</div>'))
        # 2) Se imprime un mensaje de bienvenida configurable
        d.addCallback(lambda a: request.write(msg))
        # 3) Se buscan los datos nuevos en la base
        d.addCallback(self.requestSubjectData, userId)
        # 4) Se imprime un formulario con los datos actualizados
        d.addCallback(self.printForm, request, userId)
        return d


    def requestSubjectData(self, data, userId):
        query = 'select s.id, s.name, t.fk_tutor from subject as s \
                 left join tutor_subject as t on (t.fk_subject = s.id \
                 and t.fk_tutor = %d)'
        return self.db.db.runQuery(query, (userId,))

    def printForm(self, rows, request, userId):
        _ = request.getSession()._
        string = """<form action="" method="GET">
  <select id="sbj" name="sbj" size="%d" multiple="multiple">""" % len(rows)
        for sbj in rows:
            selected = ''
            if sbj[2] is not None:
                selected = ' selected="selected"'
            string += '<option value="%s" %s>%s</option>\n' % (sbj[0], selected, sbj[1])
        string += """
   </select>
   <input type="hidden" name="user_id" value="%d"/>
   <input type="submit" name="submit" value=\""""  % userId + _('Enviar') + """\"/>
  </form>
"""
        request.write(string)
        return

    def addSubject(self, data, userId, sbj):
        operation = "insert into tutor_subject (id, fk_tutor, fk_subject) \
                     values (nextval('pk_seq_tutor_subject'), %d, %d)"
        return self.db.db.runOperation(operation, (userId, sbj))
