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
from beppo.server.utils import getTranslatorFromSession
from beppo.Constants import TUTOR, ADMIN

LASTDAY_MIDNIGHT = 24 * 7
INSTANT = 1
PRECOORD = 2

class WebSchedules(Resource):
    def __init__(self, db):
        self.db = db
        self.template = WebTemplates()
        Resource.__init__(self)

    def getChild(self, path, request):
        if path == "":
            return self
        else:
            return static.File.childNotFound

    # Si estamos autenticados como admin, sirve para modificar los horarios de cualquier tutor.
    # Si somos tutor, sirve para modificar solo los propios.
    def render_GET(self, request):
        session = request.getSession()
        _ = getTranslatorFromSession(session)
        # 0) Se empieza la página
        request.write(self.template.startPage(session, _('Modificacion de horarios')))
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
                    msg = '<h2>' + _('Administracion de horarios') + '</h2>' + _('Selecciona las horas en las que el tutor se encuentra disponible.')
        # La función que procesa e imprime el contenido de la pagina
                    self.printContent(request, d, user_id, msg)
                except ValueError:
                    request.write(self.template.unexpectedArguments(session, _('user_id deberia ser entero')))
            else:
                request.write(self.template.unexpectedArguments(session, _('falta el parametro user_id')))
        # 3) Si es Tutor, administra sus propios horarios
        elif session.kind == TUTOR:
            user_id = session.userId
            msg = '<h2>' + _('Seleccion de horarios') + '</h2>' + _('Indica los horarios en los que te encuentras disponible.')
        # La función que imprime el contenido, pero con otros argumentos
            self.printContent(request, d, user_id, msg)
        else:
        # 4) Si no es ni ni Admin, ni Tutor, ni nadie, es alguien que no está
        #    autorizado a administrar horarios
            request.write(self.template.notAuthorized(session))
        # 5) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return server.NOT_DONE_YET

    def printContent(self, request, d, userId, msg):
        _ = request.getSession()._
        # 1) Si se envían datos, se actualiza la base primero
        if "submit" in request.args.keys():
            op = "delete from tutor_schedule where fk_tutor = %d"
            d.addCallback(lambda a: self.db.db.runOperation(op, (userId, )))
            instants = self.packSchedule(request.args.get('sch', []), str(INSTANT))
            for sched in instants:
                d.addCallback(self.addSchedule, userId, sched, INSTANT)
            precoords = self.packSchedule(request.args.get('sch', []), str(PRECOORD))
            for sched in precoords:
                d.addCallback(self.addSchedule, userId, sched, PRECOORD)
            d.addCallback(lambda a: request.write('<div class="message"><h2>' + _('Cambios guardados.') + '</h2>' + _('Se guardaron los cambios correctamente') + '</div>')))
        # 2) Se imprime un mensaje de bienvenida configurable
        d.addCallback(lambda a: request.write(msg))
        # 3) Se buscan los datos nuevos en la base
        d.addCallback(self.requestScheduleData, userId)
        # 4) Se imprime un formulario con los datos actualizados
        d.addCallback(self.printForm, request, userId)
        return d

    def packSchedule(self, checks, kind):
        try: # Mapeamos a integer y filtramos valores inadecuados
            checks = [int(chk[:-2]) for chk in checks
                      if chk[-1] == kind]
        except ValueError:
            return []
        checks.sort()

        scheds = []
        last_hour = None
        start_time = None
        end_time = None
        for hour in checks:
            if last_hour is None:
                start_time = hour
            elif last_hour < hour - 1:
                scheds.append((start_time, end_time))
                start_time = hour
            last_hour = hour
            end_time = hour + 1
        # Falta el último span, que lo agregamos ahora:
        if end_time is not None:
            if end_time == LASTDAY_MIDNIGHT:
                if start_time == 0: # Este tipo labura 24/7!
                    scheds.append((0, end_time))
                elif len(scheds) > 0 and scheds[0][0] == 0: # El horario abarca las 0 del domingo
                    scheds.append((start_time, end_time + scheds[0][1]))
                    del(scheds[0])
                else:
                    scheds.append((start_time, end_time))
            else:
                scheds.append((start_time, end_time))
        # Convertimos a DateTime

        spans = []
        # Elejimos mayo del 2005 porque el 1ero cae domingo.
        mktimestamp = lambda x: DateTime(2005, 5, 1 + x / 24, x % 24)
        for sched in scheds:
            spans.append((mktimestamp(sched[0]), mktimestamp(sched[1])))
        return spans

    def unpackSchedule(self, rows):
        checks = [''] * LASTDAY_MIDNIGHT
        for row in rows:
            start_check = row[0] * 24 + row[1]
            end_check = row[2] * 24 + row[3]
            if end_check < start_check:
                end_check += LASTDAY_MIDNIGHT
            for hour in range(start_check, end_check):
                checks[hour % LASTDAY_MIDNIGHT] = str(row[4])
        return checks

    def requestScheduleData(self, data, userId):
        return self.db.db.runQuery('select extract(dow from time_start), extract(hour from time_start), extract(dow from time_end), extract(hour from time_end), schedule_type from tutor_schedule where fk_tutor = %d', (userId,))

    def printForm(self, rows, request, userId):
        _ = request.getSession()._
        checks = self.unpackSchedule(rows)
        days = [_('Domingo'), _('Lunes'), _('Martes'), _('Miercoles'), _('Jueves'), _('Viernes'), _('Sabado')]
        classes={'': 'sch_unchecked', '1': 'sch_instant', '2': 'sch_precoord'}
        titles={'': _('No disponible'), '1': _('Disponible para acceso instantaneo'),
                '2': _('Disponible para clases precoordinadas')}

        string = """
<script>
<!--
function change_cell (tag) {
  var classes=new Array();
  classes[''] = 'sch_unchecked';
  classes['1'] = 'sch_instant';
  classes['2'] = 'sch_precoord';
  var titles = new Array();
  titles[''] = """ + _('No disponible') + """;
  titles['1'] = """ + _('Disponible para acceso instantaneo') + """;
  titles['2'] = """ + _('Disponible para clases precoordinadas') + """;

  var input = tag.getElementsByTagName('input')[0];
  if (!input) return;
  parts = input.value.split('a');
  var sel = document.getElementById('sch_kind');
  if (!sel) return;
  opts = sel.getElementsByTagName('input');
  if (opts[0].checked) { var opt = '1' }
  else if (opts[1].checked) { var opt = '2' }
  else {
     alert(""" + _('No ha seleccionado un tipo de horario!') + """);
     var opt = '';
  }
  if (parts[1] == opt) { opt = '' }
  input.value = parts[0] + 'a' + opt;
  tag.className = classes[opt];
  tag.title = titles[opt];
}
-->
</script>

<form action="" method="GET">
  <fieldset class="sched" id="sch_kind">
   <legend>""" + _('Tipo de horarios') + """</legend>
   <p class="sch_instant"><label for="instant"><input id="instant" type="radio" name="kind" value="1" checked="true">
           """ + _('Acceso instantaneo') + """</label></p>
   <p class="sch_precoord"><label for="precoord"><input id="precoord" type="radio" name="kind" value="2">
           """ + _('Clases precoordinadas') + """</label></p>
  </fieldset>
</form>
<form action="" method="GET">
  <table id="schedule">
    <tr>
      <th></th>
"""
        for day in days:
            string += '<th class="sch_header">%s</th>\n' % day
        for hour in range(24):
            string += '</tr><tr>\n<td class="sch_row">%dhs</td>\n' % hour
            for day in enumerate(days):
                pos = 24 * day[0] + hour
                val = checks[pos]
                string += '<td class="%s" title="%s" onmousedown="change_cell(this)"><input type="text" name="sch" value="%da%s" /></td>\n' % (classes[val], titles[val], pos, val)
        string += """
   </tr><tr><td class="sch_row">24hs</td>\n</tr></table>
   <input type="hidden" name="user_id" value="%d"/>
   <input type="submit" name="submit" value="""  % userId + _('Enviar') + """/>
  </form>
"""
        request.write(string)
        return

    def addSchedule(self, data, userId, sched, kind):
        return self.db.db.runOperation("insert into tutor_schedule (fk_tutor, time_start, time_end, schedule_type) values (%d, %s, %s, %d)", (userId, str(sched[0]), str(sched[1]), kind))
