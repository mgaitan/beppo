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
                    msg = '<h2>' + _('Administracion de horarios') + '</h2>' + _('Selecciona las horarios de acceso instantaneo para el tutor.')
        # La función que procesa e imprime el contenido de la pagina
                    self.printContent(request, d, user_id, msg)
                except ValueError:
                    request.write(self.template.unexpectedArguments(session, _('user_id deberia ser entero')))
            else:
                request.write(self.template.unexpectedArguments(session, _('falta el parametro user_id')))
        # 3) Si es Tutor, administra sus propios horarios
        elif session.kind == TUTOR:
            user_id = session.userId
            msg = '<h2>' + _('Seleccion de horarios') + '</h2>' + _('Selecciona los horarios en los que estas disponible para horas de acceso instantaneo.')
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
        # 1) Si se envían datos, se actualiza la base primero
        _ = request.getSession()._
        if "submit" in request.args.keys():
            op = "delete from tutor_schedule where fk_tutor = %d"
            d.addCallback(lambda a: self.db.db.runOperation(op, (userId, )))
            instant = self.packSchedule(request.args.get('sched_ai', []))
            for sched in instant:
                d.addCallback(self.addSchedule, userId, sched, INSTANT)
            precoord = self.packSchedule(request.args.get('sched_pc', []))
            for sched in precoord:
                d.addCallback(self.addSchedule, userId, sched, PRECOORD)
            d.addCallback(lambda a: request.write('<div class="message"><h2>' + _('Cambios guardados.') + '</h2>' + _('Se guardaron los cambios correctamente') + '</div>'))
        # 2) Se imprime un mensaje de bienvenida configurable
        d.addCallback(lambda a: request.write(msg))
        # 3) Se buscan los datos nuevos en la base
        d.addCallback(self.requestScheduleData, userId)
        # 4) Se imprime un formulario con los datos actualizados
        d.addCallback(self.printForm, request, userId)
        return d

    def packSchedule(self, checks):
        try: # Mapeamos a integer y filtramos valores inadecuados
            checks = filter(lambda x: 0 <= x  and x < LASTDAY_MIDNIGHT, map(int, checks))
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
        checks = {}
        checks['ai'] = [False] * LASTDAY_MIDNIGHT
        checks['pc'] = [False] * LASTDAY_MIDNIGHT
        for row in rows:
            start_check = row[0] * 24 + row[1]
            end_check = row[2] * 24 + row[3]
            if end_check < start_check:
               end_check += LASTDAY_MIDNIGHT
            for hour in range(start_check, end_check):
                if row[4] == INSTANT:
                    checks['ai'][hour % LASTDAY_MIDNIGHT] = True
                elif row[4] == PRECOORD:
                    checks['pc'][hour % LASTDAY_MIDNIGHT] = True
        return checks

    def requestScheduleData(self, data, userId):
        return self.db.db.runQuery('select extract(dow from time_start), extract(hour from time_start), extract(dow from time_end), extract(hour from time_end), schedule_type from tutor_schedule where fk_tutor = %d', (userId,))

    def printForm(self, rows, request, userId):
        _ = request.getSession()._
        checks = self.unpackSchedule(rows)
        days = [_('Domingo'), _('Lunes'), _('Martes'), _('Miercoles'), _('Jueves'), _('Viernes'), _('Sabado')]
        string = """
<script>
<!--
function change_cell (tag) {
  input = tag.getElementsByTagName('input')[0]
  if (!input) return;
  input.checked = ! input.checked;
  if (input.checked) {
    var other = tag.id.substring(0, 6) + (((tag.id[6] * 1) + 1) % 2);
    other = document.getElementById(other);
    input = other.getElementsByTagName('input')[0]
    input.checked = false;
    other.className = other.className.substring(0, 7) + 'unchecked';
    other.title = '""" + _('No disponible') + """';
    var style = tag.className.substring(0, 7) + "checked";
    var tit = '""" + _('Disponible') + """';
  } else {
    var style = tag.className.substring(0, 7) + "unchecked";
    var tit = '""" + _('No disponible') + """';
  }
  tag.className = style;
  tag.title = tit;
}
-->
</script>

<form action="" method="GET">
  <fieldset class="sched">
    <legend>""" + _('Tipo de horarios') + """</legend>
      <p class="sch_instant">""" + _('Acceso instantaneo') + """</p>
      <p class="sch_precoord">""" + _('Clases Precoordinadas') + """</p>
  </fieldset>
</form>
<form action="" method="GET">
  <table id="schedule">
    <tr>
      <th></th>
"""
        for day in days:
            string += '<th colspan="2">%s</th>\n' % day
        string += '\n</tr><tr><th></th>\n'
        for day in days:
            string += '<th>AI</th><th>PC</th>\n'
        for hour in range(24):
            string += '</tr><tr>\n<td class="sch_row">%dhs</td>\n' % hour
            for day in enumerate(days):
                check = 24 * day[0] + hour
                for sufix, kind in enumerate(('ai', 'pc')):
                    if checks[kind][check]:
                        string += """<td id="sch%03d%d" class="sch_%s_checked" title=" """ %(check, sufix, kind) + _('Disponible') + """ " onmousedown="change_cell(this)"><input type="checkbox" name="sched_%s" value="%d" checked="checked"/></td>\n""" % (kind, check)
                    else:
                        string += """<td id="sch%03d%d" class="sch_%s_unchecked" title=" """  % (check, sufix, kind) + _('No disponible') + """ " onmousedown="change_cell(this)"><input type="checkbox" name="sched_%s" value="%d" /></td>\n""" % (kind, check)
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
