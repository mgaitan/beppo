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
from beppo.server.DBConnect import DBConnect
from beppo.Constants import TUTOR, ADMIN, DATE_FORMAT
from beppo.Constants import IACLASS, PACLASS, EXTRA_IACLASS, OFFLINE_QUESTION
from beppo.Constants import WAITING, EXTRA_WAITING, ABSENT
from beppo.Constants import POST_PROCESS, CORRECTED, NOT_CORRECTED
from mx import DateTime

class WebTutorInfo(Resource):
    _ = dummyTranslator
    MAX_TYPE = POST_PROCESS + 1
    session_types = [{'code': IACLASS, 'desc': _('A.I.'), 'arr': 0},
    {'code': PACLASS, 'desc': _('C.P.'), 'arr': 1},
    {'code': EXTRA_IACLASS, 'desc': _('Sin turno'), 'arr': 2},
    {'code': OFFLINE_QUESTION, 'desc': _('Preguntas offline'), 'arr': 3},
    {'code': WAITING, 'desc': _('En espera'), 'arr': 4},
    {'code': EXTRA_WAITING, 'desc': _('En espera (Sin turno)'), 'arr': 5},
    {'code': ABSENT, 'desc': _('Ausente'), 'arr': 6},
    {'code': POST_PROCESS, 'desc': _('Postprocesado'), 'arr': 7}]

    def __init__(self):
        self.db = DBConnect()
        self.template = WebTemplates()
        Resource.__init__(self)

    def getChild(self, path, request):
        if path == "":
            return self
        else:
            return static.File.childNotFound

    # Si estamos autenticados como admin, sirve para modificar las materias de
    # cualquier tutor.
    # Si somos tutor, sirve para modificar solo los propios.
    def render_GET(self, request):
        d = defer.maybeDeferred(getTranslatorFromSession, request)
        d.addCallback(self.doAuthentication, request)
        return server.NOT_DONE_YET

    def doAuthentication(self, trans, request):
        session = request.getSession()
        _ = trans
        # 0) Se empieza la página
        header = """
<link rel="stylesheet" type="text/css" media="all" href="/calendar/calendar-win2k-cold-1.css" title="win2k-cold-1" />
<script type="text/javascript" src="/calendar/calendar.js"></script>
<script type="text/javascript" src="/calendar/lang/calendar-sp.js"></script>
<script type="text/javascript" src="/calendar/calendar-setup.js"></script>"""

        request.write(self.template.startPageWithHeader(session, header, \
         _('Informacion de tutores')))
        d = defer.maybeDeferred(lambda:None)
        # 1) Verificar que esté autenticado ante el sistema
        if not hasattr(session, 'username'):
            request.write(self.template.notAuthenticated(session))
        # 2) Si es Admin, administra todos los usuarios
        elif session.kind == ADMIN:
            msg = '<h2>' + _('Informacion de los tutores del sistema') + '</h2>'
        # La función que imprime el contenido, pero con otros argumentos
            self.printContent(request, d, msg)
        else:
        # 4) Si no es Admin es alguien que no está
        #    autorizado a ver la información de tutores
            request.write(self.template.notAuthorized(session))
        # 5) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return d

    def printContent(self, request, d, msg):
        """Consulta los datos de tutores de la base de datos y los manda
        a imprimir
        """
        args = self.checkRequest(d, request)
        d.addCallback(lambda a: request.write(msg))
        d.addCallback(lambda a: self.printForm(request, args))
        d.addCallback(lambda a: self.requestData(request, args['start'], args['end']))
        d.addCallback(self.printData, request)
        return d


    def requestData(self, request, time_start, time_end):
        """Consulta los datos de los tutores en la tabla session con los límites de
        fecha dados por time_start y time_end
        """

        query = "select p.username, p.id, sum(dmin('%s', s.time_end) - \
          dmax('%s', s.time_start)) as total, s.session_type from person p, \
          tutor t left join session s on (s.fk_tutor = t.id and \
          s.time_start < '%s' and s.time_end > '%s') where t.id = p.id \
          group by p.id, p.username, s.session_type \
          order by username, session_type"

        d = self.db.db.runQuery(query, ((time_end, time_start) * 2))
        return d

    def printData(self, rows, request):
        _ = request.getSession()._
        length = len(rows)
        string = ""
        if length == 0:
            string += _('No hay resultados disponibles') + '<br/>'
        else:
            #averiguo cuantos usuarios distintos hay
            i = 0
            current = rows[0][0]
            count = 1
            while i < length:
                if rows[i][0] != current:
                    current = rows[i][0]
                    count = count + 1
                i = i + 1
            #inicializo matriz resultado
            res = [[0] * self.MAX_TYPE for i in range (0,count)]
            #inicializo matriz sumas
            sum = [0] * self.MAX_TYPE

            j = 0 #marca la fila de res
            curr_row = 0 #marca la fila de rows
            current = rows[0][0]
            res[0][0] = (rows[0][0], rows[0][1])
            while(curr_row < length):
                if rows[curr_row][2] != None:
                    res[j][rows[curr_row][3]] = (rows[curr_row][2]).hours
                    sum[rows[curr_row][3]] += (rows[curr_row][2]).hours
                curr_row = curr_row + 1
                if curr_row < length and rows[curr_row][0] != current:
                    current = rows[curr_row][0]
                    j = j + 1
                    res[j][0] = (rows[curr_row][0], rows[curr_row][1])

            string = _('Informacion de %d tutores:') % count + '<br/>'
            string += '<table class="table_list"><tr class="header_list"> '
            string += '<th>' + _('Tutor') + '</th>'
            for i in self.session_types:
                string += '<th>' + _(i['desc']) + '</th>'
            string += '</tr>'

            for row in res:
                string += '<tr style="text-align: center">'
                string += '<td style="text-align: left">'
                string += '<a href="/tutor_sessions?user_id=%s">%s</a></td>' \
                   % (row[0][1], row[0][0])

                for i in self.session_types:
                    data = row[i['code']]
                    string += '<td>%.2f hs.</td>' % data
                string += '</tr>'
            string += '<tr class="last_row">'
            string += '<td>' + _('Totales') + '</td>'
            for i in self.session_types:
                string += '<td>%.2f hs.</td>' % sum[i['code']]
            string += '</tr></table>'

        request.write(string)
        return

    def dateFormat(self, date):
        return (date != 0) and date.hours or 0

    def checkRequest(self, d, request):
        """
        Chequea si los campos de fecha vienen con datos (en cuyo caso arma la fecha con
        esos datos -notar que valores mal formateados generan la fecha de hoy-) o no
        (en cuyo caso genera una fecha por defecto)
        """
        session = request.getSession()
        args = dict([(i, request.args[i][0]) for i in request.args.keys()])
        try:
            args["start"] = DateTime.strptime(args["start"], DATE_FORMAT)
            end = DateTime.strptime(args["end"], DATE_FORMAT)
            # para tomar en cuenta todo el día del final
            args["end"] = end + DateTime.RelativeDateTime(days=+1)
        except (KeyError, DateTime.Error):
            now = DateTime.now()
            start = DateTime.DateTime(now.year, now.month)
            args["start"] = start
            end = DateTime.now()
            # para tomar en cuenta todo el día del final
            args["end"] = end + DateTime.RelativeDateTime(days=+1, hour=0,minute=0,second=0)
            return args
        return args

    def printForm(self, request, args):
        _ = request.getSession()._
        start = args['start'].Format(DATE_FORMAT)
        end = (args['end'] - DateTime.RelativeDateTime(days=+1)).Format(DATE_FORMAT)
        string = """
<form action="#" method="get">
<table cellspacing="0" cellpadding="0" style="border-collapse: collapse">
<tr>
 <td>""" + _('Fecha Inicio:') + """</td>
 <td><input type="text" name='start' id="time_start" value="%s"/></td>
 <td><img src="/static/graphics/calendar.gif" width="16" height="16" alt=\"""" % start + _('Elegir fecha') + """\" title=\"""" + _('Elegir fecha') + """\" id="calendar_from" style="cursor: pointer; border: 1px solid black;"/> </td>
 <td>""" + _('(dd/mm/aaaa)') + """</td>
</tr>
<tr>
 <td>""" + _('Fecha Fin:') + """ </td>
 <td><input type="text" name="end" id="time_end" value="%s"/></td>
 <td><img src="/static/graphics/calendar.gif" width="16" height="16" alt=\"""" % end + _('Elegir fecha') + """\" title=\"""" + _('Elegir fecha') + """\" id="calendar_to" style="cursor: pointer; border: 1px solid black;"/> </td>
 <td>""" + _('(dd/mm/aaaa)') + """</td>
</tr>
<tr>
<td colspan="4" align="center"><input type="submit" name="submit" value=\"""" + _('Actualizar') + """\"/></td>
</tr>
</table>
</form>
<script type="text/javascript">
    Calendar.setup({
        inputField     :    "time_start",     // id of the input field
        ifFormat       :    "%s",      // formato de entrada
        button         :    "calendar_from",  // id del trigger
        align          :    "Tl",           // alineamiento
        singleClick    :    true
    });
    Calendar.setup({
        inputField     :    "time_end",     // id of the input field
        ifFormat       :    "%s",      // formato de entrada
        button         :    "calendar_to",  // id del trigger
        align          :    "Tl",           // alineamiento
        singleClick    :    true
    });
</script>
""" % (DATE_FORMAT, DATE_FORMAT)
        request.write(string)
        return
