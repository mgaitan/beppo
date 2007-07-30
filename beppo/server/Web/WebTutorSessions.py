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
from WebGetUserInfo import WebGetUserInfo
from twisted.python import log
from beppo.server.utils import getTranslatorFromSession, dummyTranslator
from beppo.Constants import TUTOR, ADMIN, PUPIL, DATETIME_FORMAT
from beppo.Constants import IACLASS, PACLASS, EXTRA_IACLASS, WAITING
from beppo.Constants import OFFLINE_QUESTION, EXTRA_WAITING, ABSENT
from beppo.Constants import NORMAL, TUTOR_ENTER, PUPIL_ENTER, TUTOR_END, PUPIL_END
from beppo.Constants import TUTOR_QUIT, SERVER_RESTART, QUESTION_ANSWERED
from beppo.Constants import DECIDING, ACCEPTED, REJECTED, QUESTION_NOT_ANSWERED
from beppo.Constants import POST_PROCESS, CORRECTED, NOT_CORRECTED
from beppo.server.DBConnect import DBConnect
from mx import DateTime

class WebTutorSessions(Resource):
    _ = dummyTranslator

    typeToString = {IACLASS: _('Acceso Instantaneo'), PACLASS: _('Clase Precoordinada'), WAITING: _('En espera'), OFFLINE_QUESTION: _('Pregunta offline'), EXTRA_IACLASS: _('AI (Fuera de turno)'), EXTRA_WAITING: _('Espera (Fuera de turno)'), DECIDING: _('Analizando pregunta'), ABSENT: _('Ausente'), POST_PROCESS: _('Postprocesado')}.get

    typeToStyle = {IACLASS: "ia_row", PACLASS: "pc_row", WAITING: "waiting_row", OFFLINE_QUESTION: "offline_row", EXTRA_IACLASS: "extra_ia_row", EXTRA_WAITING: "extra_waiting_row", DECIDING: "deciding_row", ABSENT: "absent_row", POST_PROCESS: "postprocess_row"}.get

    eCodeToString = {NORMAL: _('Fin horario'), TUTOR_ENTER: _('Arribo'), PUPIL_ENTER: _('Entrada de alumno'), TUTOR_END: _('Terminada por Tutor'), PUPIL_END: _('Terminada por alumno'), TUTOR_QUIT: _('Desconexion Tutor'), SERVER_RESTART: _('Reconexion servidor'), QUESTION_ANSWERED: _('Pregunta contestada'), QUESTION_NOT_ANSWERED: _('Pregunta no contestada'), ACCEPTED: _('Pregunta aceptada'), REJECTED: _('Pregunta no aceptada'), CORRECTED: _('Postprocesado'), NOT_CORRECTED: _('No postprocesado'), None: '-'}.get

    def __init__(self):
        self.db = DBConnect()
        self.template = WebTemplates()
        Resource.__init__(self)

    def getChild(self, path, request):
        if path == "":
            return self
        else:
            return static.File.childNotFound

    # Si estamos autenticados como admin, sirve para modificar las
    # materias de cualquier tutor.
    # Si somos tutor, sirve para modificar solo los propios.
    def render_GET(self, request):
        d = defer.maybeDeferred(getTranslatorFromSession, request)
        d.addCallback(self.doAuthentication, request)
        return server.NOT_DONE_YET

    def doAuthentication(self, trans, request):
        session = request.getSession()
        _ = trans
        # 0) Se empieza la página
        request.write(self.template.startPage(session, \
          _('Historial de sesiones del tutor')))
        d = defer.maybeDeferred(lambda:None)
        # 1) Verificar que esté autenticado ante el sistema
        if not hasattr(session, 'username'):
            request.write(self.template.notAuthenticated(session))
        # 2) Si es Admin, administra todos los usuarios
        elif session.kind == ADMIN:
            if "user_id" in request.args.keys():
                try:
                    user_id = int(request.args['user_id'][0])
                    msg = '<h2>' + _('Sesiones del tutor') + '</h2>'
        # La función que procesa e imprime el contenido de la pagina
                    self.printContent(request, d, user_id, msg)
                except ValueError:
                    request.write(self.template.unexpectedArguments(session, \
                      _('user_id deberia ser entero')))
            else:
                request.write(self.template.unexpectedArguments(session, \
                  _('falta el parametro user_id')))
        # 3) Si es Tutor, ve sus propias sesiones
        elif session.kind == TUTOR:
            user_id = session.userId
            msg = '<h2>' + _('Tus sesiones') + '</h2>' + \
              _('Este es el detalle de tus sesiones en el sistema:') + '<br/>'
        # La función que imprime el contenido, pero con otros argumentos
            self.printContent(request, d, user_id, msg)
        else:
        # 4) Si no es ni ni Admin, ni Tutor, ni nadie, es alguien que no está
        #    autorizado a administrar horarios
            request.write(self.template.notAuthorized(session))
        # 5) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return d


    def printContent(self, request, d, user_id, msg):
        """Consulta las sesiones del tutor user_id en la
         base de datos y las manda a imprimir
        """
        d.addCallback(lambda a: request.write(msg))
        now = DateTime.now()
        query =  """select s.session_type, s.time_start, s.time_end, s.error_code, \
         p.username, p.id from session s left join person p on (p.id = s.fk_pupil) \
         where fk_tutor = %d and s.time_end < '%s' order by time_start asc"""
        d.addCallback(lambda a: self.db.db.runQuery(query, (user_id, now)))
        d.addCallback(self.printData, request)
        return d

    def printData(self, rows, request):
        _ = request.getSession()._
        if len(rows) == 0:
            string = _('No se registran sesiones') + '<br/>'
        else:
            string = _('Informacion de %d sesiones:') % len(rows)
            string += """
<table class="table_list" id="sessions">
 <tr>
  <th class="header_list">""" + _('Tipo de sesion') + """</th>
  <th class="header_list">""" + _('Comienzo') + """</th>
  <th class="header_list">""" + _('Fin') + """</th>
  <th class="header_list">""" + _('Duracion') + """</th>
  <th class="header_list">""" + _('Razon cierre') + """</th>
  <th class="header_list">""" + _('Alumno') + """</th>
 </tr>
"""
            for row in rows:
                session_type = _(self.typeToString(row[0], ''))
                style = _(self.typeToStyle(row[0]))
                start = row[1].Format(DATETIME_FORMAT)
                end = row[2].Format(DATETIME_FORMAT)
                diff = self.dateDiffFormat(row[2] - row[1])
                pupil = (row[4] is not None) and row[4] or ""
                pupil_id = (row[5] is not None) and row[5] or ""
                reason = _(self.eCodeToString(row[3], '-'))
                string += """
<tr class="%s">
 <td>%s</td>
 <td>%s</td>
 <td>%s</td>
 <td>%s</td>
 <td>%s</td>
 <td> <a href="/userinfo?user_id=%s&amp;kind=%d"> %s </a> </td>
</tr>""" % (style, session_type, start, end, diff, reason, pupil_id, PUPIL, pupil)
            string += """</table>"""
        request.write(string)
        return

    def dateDiffFormat(self, date):
        hours = int(date.hours)
        minutes = int(date.minutes)
        seconds = int(date.seconds)
        return "%02d:%02d:%02d" % (hours, minutes % 60, seconds % 60)
