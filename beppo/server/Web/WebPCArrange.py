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
from twisted.web import server
from twisted.internet import defer
from WebTemplates import WebTemplates
from beppo.server.DBConnect import DBConnect
from twisted.python import log
from beppo.server.utils import getTranslatorFromSession
from beppo.Constants import PUPIL, ADMIN, PACLASS
from WebSchedules import schedule_change_cell
from mx.DateTime import today, DateTime

LASTDAY_MIDNIGHT = 24 * 7 * 2


class WebPCArrangeRoot(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.one = WebPCArrange1()
        self.two = WebPCArrange2()
        self.three = WebPCArrange3()
        self.four = WebPCArrange4()
        self.five = WebPCArrange5()

    def getChild(self, path, request):
        if path == "" or path == "1":
            return self.one
        elif path == "2":
            return self.two
        elif path == "3":
            return self.three
        elif path == "4":
            return self.four
        elif path == "5":
            return self.five
        else:
            return static.File.childNotFound

    def render_GET(self, request):
        return self.one.render_GET(request)

class WebPCArrangeCommon(Resource):
    def __init__(self):
        self.db = DBConnect()
        self.template = WebTemplates()
        Resource.__init__(self)

    # Si estamos autenticados como admin, sirve para coordinar clases para cualquier alumno.
    # Si somos alumno, sirve para coordinar clases propias.
    def render_GET(self, request):
        d = defer.maybeDeferred(getTranslatorFromSession, request)
        d.addCallback(self.doAuthentication, request)
        return server.NOT_DONE_YET

    def doAuthentication(self, trans, request):
        session = request.getSession()
        _ = trans

        msg = '<div id="pchelp"><h3>' + _('Pasos para precoordinar una clase') + \
              '</h3><ol class="steps"><li class="one">' + _('Elige la materia') + \
              '</li><li class="two">' + _('Elige el tutor') + '</li><li class="three">' + \
              _('Elige el horario') + '</li></ol></div>\n'

        msg = msg + self.stepMessage(session)

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
        # La función que procesa e imprime el contenido de la pagina
                    self.printContent(request, d, user_id, msg)
                except ValueError:
                    request.write(self.template.unexpectedArguments(session, _('user_id deberia ser entero')))
            else:
                request.write(self.template.unexpectedArguments(session, _('falta el parametro user_id')))
        # 3) Si es Pupil, coordina sus propias clases
        elif session.kind == PUPIL:
            user_id = session.userId
        # La función que imprime el contenido, pero con otros argumentos
            self.printContent(request, d, user_id, msg)
        else:
        # 4) Si no es ni ni Admin, ni Pupil, ni nadie, es alguien que no está
        #    autorizado a administrar horarios
            request.write(self.template.notAuthorized(session))
        # 5) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return d

    def packSchedule(self, checks):
        try: # Mapeamos a integer y filtramos valores inadecuados
            checks = [int(chk) for chk in checks]
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
        base = today() + 3
        def mktimestamp(x):
            day = base + x / 48
            return DateTime(day.year, day.month, day.day, (x % 48) / 2, (x % 2) * 30)
        for sched in scheds:
            spans.append((mktimestamp(sched[0]), mktimestamp(sched[1])))
        return spans

    def scheduleDescription(self, scheds, request, withDay):
        session = request.getSession()
        _ = session._
        days = [_('lunes'), _('martes'), _('miercoles'), _('jueves'), _('viernes'), _('sabado'), _('domingo')]
        desc = ''
        for sch in scheds:
            if sch[0].day == sch[1].day:
                if withDay:
                    desc += days[sch[0].day_of_week] + ' ' + sch[0].strftime("%d-%m-%Y") + \
                            ', ' + _('de') + ' ' + sch[0].strftime('%H:%M') + \
                            ' ' + _('a') + ' ' + sch[1].strftime('%H:%M')
                else:
                    desc += days[sch[0].day_of_week] + ' ' + _('de') + ' ' + \
                            sch[0].strftime('%H:%M') + ' ' + _('a') + ' ' + \
                            sch[1].strftime('%H:%M')
            else:
                if withDay:
                    desc += _('de') + ' ' + days[sch[0].day_of_week] + ' ' + \
                            sch[0].strftime('%d-%m-%Y, %H:%M') + ' ' + _('a') + \
                            ' ' + days[sch[1].day_of_week] + ' ' + \
                            sch[1].strftime('%d-%m-%Y, %H:%M')
                else:
                    desc += _('de') + ' ' + days[sch[0].day_of_week] + ' ' + \
                            sch[0].strftime('%H:%M') + ' ' + _('a') + ' ' + \
                            days[sch[1].day_of_week] + ' ' + sch[1].strftime('%H:%M')
            desc += '<br />'
        return desc



class WebPCArrange1(WebPCArrangeCommon):
    # Pagina de seleccion de materia.  Al seleccionar cada materia, se indica
    # el o los tutores que saben dictar esa materia
    def printContent(self, request, d, userId, msg):
        _ = request.getSession()._
        # 1) Este formulario no recibe datos, así que no se actualiza la base
        # 2) Se imprime un mensaje de bienvenida configurable
        d.addCallback(lambda a: request.write(msg))
        # 3) Se buscan los datos en la base
        d.addCallback(self.requestTutorSubjectData, request)
        d.addCallback(self.requestSubjectData)
        # 4) Se imprime un formulario
        d.addCallback(self.printForm, request, userId)
        return d

    def requestTutorSubjectData(self, data, request):
        d = self.db.db.runQuery('select s.id, p.first_name, p.last_name from tutor t, person p, subject s, tutor_subject ts where t.id = p.id and ts.fk_tutor = t.id and ts.fk_subject = s.id order by s.id')
        d.addCallback(self.printJavascript, request)
        return d

    def printJavascript(self, rows, request):
        _ = request.getSession()._
        string = '\''
        previous = None
        for r in rows:
            if previous != r[0]:
                string += '\'\ntutors[\'%d\'] = \'' % r[0]
                previous = r[0]
            string += '<li>%s %s' % (r[1], r[2])
        string += '\'\n'
        request.write("""
<script type="text/javascript"><!--
function validateForm(form) {
    if (form.sbj.selectedIndex == -1) {
        alert('""" + _('Debes seleccionar una materia') + """');
        return false;
    }
    return true;
}

function showTutors(select) {
    var tutors = new Array();
""" + string + """  var info = document.getElementById('pc_tutorinfo')
  var idx = select.options[select.selectedIndex].value
  if (!tutors[idx]) { tutors[idx] = '""" + _('Ninguno') + \
    "' }\ninfo.innerHTML = '" + _('Tutores que dan esta materia') + """:<ul>' +
     tutors[idx] + '</ul>'
}
-->
</script>
""")

    def requestSubjectData(self, data):
        return self.db.db.runQuery('select id, name from subject')

    def printForm(self, rows, request, userId):
        _ = request.getSession()._
        string = '<form action="/pc_arrange/2" method="get" onsubmit="javascript:return validateForm(this)"><fieldset><legend>' + \
            _('Materias') + """</legend>
  <table class="pc"><tr><td><select id="sbj" name="sbj" size="%d" onchange="javascript:showTutors(this)">""" % len(rows)
        for sbj in rows:
            string += '<option value="%s">%s</option>\n' % (sbj[0], sbj[1])
        string += """
   </select><br/>
   <input type="hidden" name="user_id" value="%d"/>
   <input type="submit" name="submit" value=\""""  % userId + _('Enviar') + """\"/>
   </td><td class="info">
   <span id="pc_tutorinfo"></span></td></tr></table>
    </fieldset>
  </form>
"""
        request.write(string)
        return

    def stepMessage(self, session):
        _ = session._
        return '<h2>' + _('Elige la materia') + '</h2><p>' + \
              _('Primero elige la materia para la que necesites ayuda de la siguiente lista') + '</p>'

class WebPCArrange2(WebPCArrangeCommon):
    # Pagina de seleccion de tutores.  Debajo de cada tutor se indica los
    # horarios que tiene disponible para brindar tutorías
    def printContent(self, request, d, userId, msg):
        session = request.getSession()
        _ = session._
        # 1) Chequeamos los argumentos
        if 'sbj' not in request.args.keys():
            d.addCallback(lambda a: \
                request.write(self.template.unexpectedArguments(session, \
                        _('Falta el argumento requerido \'sbj\''))))
            return
        try:
            sbj = int(request.args['sbj'][0])
        except ValueError:
            d.addCallback(lambda a: \
               request.write(self.template.unexpectedArguments(session, \
                        _('sbj deberia ser entero'))))
            return
        # 2) Se imprime un mensaje de bienvenida configurable
        d.addCallback(lambda a: request.write(msg))
        # 3) Se buscan los datos en la base
        d.addCallback(self.requestTutorData, request, sbj)
        # 4) Se imprime un formulario
        d.addCallback(self.printForm, request, userId, sbj)
        return d

    def stepMessage(self, session):
        _ = session._
        return '<h2>' + _('Elige el Tutor') + '</h2><p>' + \
              _('Selecciona el tutor de la lista a continuacion.  Cada tutor indica los horarios en los que esta disponible para dar clases.') + '</p>'

    def requestTutorData(self, data, request, sbj):
         d = self.db.db.runQuery('select p.id, p.first_name, p.last_name, tsch.time_start, tsch.time_end from tutor t, person p, tutor_subject ts, tutor_schedule tsch where t.id = p.id and ts.fk_tutor = t.id and tsch.fk_tutor = t.id and ts.fk_subject = %d and tsch.schedule_type = %s order by t.id', (sbj, PACLASS))
         d.addCallback(self.concoctScheduleData, request)
         return d

    def concoctScheduleData(self, rows, request):
         string = ''
         current = None
         for tutor in rows:
             if tutor[0] != current:
                 if current:
                     timetable = self.scheduleDescription(scheds, request, withDay=False)
                     string +='<label for="%d"><input id="%d" type="radio" ' \
                           'name="tutor" value="%d">%s %s</label> <div class="sched_desc">%s</div>' \
                         % (current, current, current, first_name, last_name, timetable)
                 current = tutor[0]
                 first_name = tutor[1]
                 last_name = tutor[2]
                 scheds = []
             scheds = scheds + [(tutor[3], tutor[4])]
         if current:
             timetable = self.scheduleDescription(scheds, request, withDay=False)
             string +='<label for="%d"><input id="%d" type="radio" ' \
                   'name="tutor" value="%d">%s %s</label> <div class="sched_desc">%s</div>' \
                 % (current, current, current, first_name, last_name, timetable)

         return string

    def printForm(self, tutors, request, userId, sbj):
        _ = request.getSession()._
        string = """
<script type="text/javascript"><!--
function validateForm(form) {
    for (i = 0; i < form.elements.length; i++) {
       if (form.elements[i].checked)
           return true;
    }
    alert('""" + _('Debes seleccionar un tutor') + """');
    return false;
}

-->
</script>
<form action="/pc_arrange/3" method="get" onsubmit="javascript:return validateForm(this)">
<fieldset><legend>
""" + _('Tutores') + """</legend>
  <table class="pc"><tr><td>""" + tutors + """
   <input type="hidden" name="user_id" value="%d"/>
   <input type="hidden" name="sbj" value="%d"/>
   <input type="submit" name="submit" value=\""""  % (userId, sbj) + _('Enviar') + """\"/>
   </td><td class="info">
   <span id="pc_tutorinfo"></span></td></tr></table>
    </fieldset>
  </form>
"""
        request.write(string)
        return

class WebPCArrange3(WebPCArrangeCommon):
    # Pagina de seleccion de horario.  En el horario del tutor elegido se
    # indican los compromisos previos que tiene el tutor, y se permite
    # seleccionar un horario para la clase.
    def stepMessage(self, session):
        _ = session._
        return '<h2>' + _('Elige el horario') + '</h2><p>' + \
              _('Finalmente elige el horario en el que necesitas tener la clase.') + '</p>'

    def printContent(self, request, d, userId, msg):
        session = request.getSession()
        _ = session._
        # 1) Chequeamos los argumentos
        if 'sbj' not in request.args.keys() or 'tutor' not in request.args.keys():
            d.addCallback(lambda a: \
                request.write(self.template.unexpectedArguments(session, \
                        _('Faltan argumentos requeridos'))))
            return
        try:
            sbj = int(request.args['sbj'][0])
            tutor = int(request.args['tutor'][0])
        except ValueError:
            d.addCallback(lambda a: \
               request.write(self.template.unexpectedArguments(session)))
            return
        # 2) Se imprime un mensaje de bienvenida configurable
        d.addCallback(lambda a: request.write(msg))
        # 3) Se buscan los datos en la base
        d.addCallback(self.requestScheduleData, tutor)
        # 4) Se imprime un formulario
        d.addCallback(self.printForm, request, userId, sbj, tutor)
        return d


    def requestScheduleData(self, data, tutor):
         d = self.db.db.runQuery('select time_start, time_end from tutor_schedule where fk_tutor = %d and schedule_type = %d', (tutor, PACLASS))
         d.addCallback(self.requestCommitments, tutor)
         return d

    def requestCommitments(self, rows, tutor):
         d = self.db.db.runQuery("select time_start, time_end from prearranged_classes where fk_tutor = %d and time_end > current_date + interval '3 days' and time_start < current_date + interval '10 days'", (tutor,))
         d.addCallback(lambda x, y: (x,y), rows)
         return d

    def unpackSchedule(self, data):
        checks = ['u'] * LASTDAY_MIDNIGHT
        base = today() + 3
        for row in data[1]:
            start_check = ((row[0].day_of_week - base.day_of_week) % 7) * 48 + row[0].hour * 2 + row[0].minute / 30
            end_check = ((row[1].day_of_week - base.day_of_week) % 7) * 48 + row[1].hour * 2 + row[1].minute / 30
            if end_check <= start_check:
                end_check += LASTDAY_MIDNIGHT
            for hour in range(start_check, end_check):
                checks[hour % LASTDAY_MIDNIGHT] = '2'
        for row in data[0]:
            delta = row[0] - base
            start_check = delta.day * 48 + delta.hour * 2 + delta.minute / 30
            delta = row[1] - base
            end_check = delta.day * 48 + delta.hour * 2 + delta.minute / 30
            if end_check <= start_check:
                end_check += LASTDAY_MIDNIGHT
            for hour in range(start_check, end_check):
                checks[hour % LASTDAY_MIDNIGHT] = 'o'
        return checks



    def printForm(self, data, request, userId, sbj, tutor):
        _ = request.getSession()._
        checks = self.unpackSchedule(data)
        days = [_('Lunes'), _('Martes'), _('Miercoles'), _('Jueves'), _('Viernes'), _('Sabado'), _('Domingo')]
        classes={'u': 'sch_unavailable', '1': 'sch_instant', '2': 'sch_precoord', 'o': 'sch_occupied'}
        titles={'u': _('No disponible'), '1': _('Disponible para acceso instantaneo'),
                '2': _('Disponible para clases precoordinadas'), 'o': _('Ya esta reservado')}

        string = """
<script type="text/javascript">
<!--
function validateForm(form) {
    for (i = 0; i < form.elements.length; i++) {
       if (form.elements[i].checked)
           return true;
    }
    alert('""" + _('Debes seleccionar al menos un horario') + """');
    return false;
}

function change_cell (tag) {
  input = tag.getElementsByTagName('input')[0]
  if (!input) return;
  input.checked = ! input.checked;
  if (input.checked) {
    var style = "sch_arranged";
    var tit = '""" + _('Coordinado para este horario') + """';
  } else {
    var style = "sch_precoord";
    var tit = '""" + _('Disponible para clases precoordinadas') + """';
  }
  tag.className = style;
  tag.title = tit;
}

-->
</script>
<form action="4" method="get" onsubmit="javascript:return validateForm(this)" >
  <fieldset>
  <legend>""" + _('Horarios disponibles') + """</legend>
  <table id="schedule">
    <tr>
      <th><p/></th>
"""
        for day in [today() + i for i in range(3,10)]:
            string += '<th class="sch_header">%s %s</th>\n' % (days[day.day_of_week], day.strftime('%d-%m-%Y'))
        for hour in range(48):
            string += '</tr><tr>\n<td class="sch_row">%d:%02dhs</td>\n' % (hour / 2, (hour % 2) * 30)
            for day in enumerate(days):
                pos = 48 * day[0] + hour
                val = checks[pos]
                string += '<td class="%s" title="%s"' % (classes[val], titles[val])
                if val in ['', 'o', 'u']:
                    string += '><p/></td>\n'
                else:
                    string += 'onclick="change_cell(this)"><input type="checkbox" name="sch" value="%d"/></td>\n' % pos
        string += """
   </tr><tr><td class="sch_row">24:00hs</td><td colspan="7" class="sch_invisible"><p/></td>\n</tr></table>
   <input type="hidden" name="user_id" value="%d"/>
   <input type="hidden" name="sbj" value="%d"/>
   <input type="hidden" name="tutor" value="%d"/>
   <input type="submit" name="submit" value=\"""" % (userId, sbj, tutor) + _('Enviar') + """\" />
  </fieldset>
  </form>
"""
        request.write(string)
        return

class WebPCArrange4(WebPCArrangeCommon):
    # Pagina de confirmación.  Se muestra un resumen de la clase que se
    # está por coordinar y se pide que se confirmen los datos.
    def stepMessage(self, session):
        _ = session._
        return '<h2>' + _('Una ultima confirmacion') + '</h2></p>'

    def printContent(self, request, d, userId, msg):
        session = request.getSession()
        _ = session._
        # 1) Chequeamos los argumentos
        if 'sbj' not in request.args.keys() or 'tutor' not in request.args.keys() \
          or 'sch' not in request.args.keys():
            d.addCallback(lambda a: \
                request.write(self.template.unexpectedArguments(session, \
                        _('Faltan argumentos requeridos'))))
            return
        try:
            sbj = int(request.args['sbj'][0])
            tutor = int(request.args['tutor'][0])
            checks = request.args['sch']
            scheds = self.packSchedule(checks)
        except ValueError:
            d.addCallback(lambda a: \
               request.write(self.template.unexpectedArguments(session)))
            return
        # 2) Se imprime un mensaje de bienvenida configurable
        d.addCallback(lambda a: request.write(msg))
        # 3) Se buscan los datos en la base
        d.addCallback(self.requestExplanationData, tutor, sbj)
        # 4) Se imprime un formulario
        d.addCallback(self.printForm, request, userId, tutor, sbj, scheds, checks)
        return d


    def requestExplanationData(self, data, tutor, sbj):
         d = self.db.db.runQuery('select first_name, last_name, name from person, subject where person.id = %d and subject.id = %d', (tutor, sbj))
         return d

    def printForm(self, data, request, userId, tutor, sbj, scheds, checks):
        _ = request.getSession()._
        if len(data) == 0:
            request.write(self.template.unexpectedArguments(session), _('Tutor o materia inexistente'))
            return
        data = data[0]
        string = '<form action="5" method="get">\n<fieldset>\n<legend>' + \
           _('Confirmacion') + '</legend>\n<p>' + \
           _('Estas por coordinar una tutoria') + \
           '</p>\n<table>\n<tr><th class="header_userinfo">' + \
           _('Tutor') + '</th><td>%s %s</td></tr>\n' % (data[0], data[1]) + \
           '<tr><th class="header_userinfo">' + _('Materia') + \
           '</th><td>%s</td></tr>\n' % data[2] + \
           '<tr><th class="header_userinfo">' + _('Fecha y horario') + \
           '</th><td>%s</td></tr>\n</table>\n' \
           % self.scheduleDescription(scheds, request, withDay=True)
        for sched in checks:
           string += '<input type="hidden" name="sch" value="%s" />\n' % sched
        string += '<input type="hidden" name="tutor" value="%d" />\n' % tutor
        string += '<input type="hidden" name="sbj" value="%d" />\n' % sbj
        string += '<input type="hidden" name="user_id" value="%d" />\n' % userId
        string += '<input type="submit" name="submit" value="' + _('Confirmar!') + \
                  '" />\n</fieldset>\n</form>\n'
        request.write(string)
        return



class WebPCArrange5(WebPCArrangeCommon):
    def stepMessage(self, session):
        _ = session._
        return '<h2>' + _('Una ultima confirmacion') + '</h2></p>'

    def checkArgs(self, data, tutor, pupil, sbj, scheds, checks):
        # Revisa que el tutor, la materia y el alumno existan y que el
        # tutor sepa dar la materia en cuestion
        d = self.db.db.runQuery('select tutor.id from tutor, pupil, subject, ' \
            'tutor_subject where tutor.id = %d and subject.id = %d and ' \
            'pupil.id = %d and tutor_subject.fk_tutor = %d and ' \
            'tutor_subject.fk_subject = %d', (tutor, sbj, pupil, tutor, sbj))
        d.addCallback(self.checkArgs2, tutor, pupil, sbj, scheds, checks)
        return d

    def checkArgs2(self, data, tutor, pupil, sbj, scheds, checks):
        # Busca los horarios del tutor para ver que este disponible en
        # los horarios solicitados
        if len(data) == 0: # Tutor, materia o alumno no existe, o ese tutor no está habilitado para esa materia
            return 1
        d = self.db.db.runQuery('select time_start, time_end from tutor_schedule where fk_tutor = %d and schedule_type = %d', (tutor, PACLASS))
        d.addCallback(self.checkArgs3, tutor, pupil, sbj, scheds, checks)
        return d

    def checkArgs3(self, data, tutor, pupil, sbj, scheds, checks):
        # Revisa que el tutor esté disponible en los horarios solicitados
        available = self.unpackSchedule(data)
        for check in checks:
            if not available[check]: # No está disponible en ese horario
                return 2
        return self.checkArgs4([], tutor, pupil, sbj, scheds, scheds[:])

    def checkArgs4(self, data, tutor, pupil, sbj, scheds, scheds2):
        # Revisa que el tutor no tenga compromisos previos para los horarios solicitados
        if len(data) > 0: # Tiene compromisos para algun horario
            return 3
        if len(scheds) == 0: # No quedan horarios que confirmar
            return self.checkArgs5(tutor, pupil, sbj, scheds2)
        sched = scheds.pop()
        d = self.db.db.runQuery("select id from prearranged_classes where time_end > '%s' and time_start < '%s'", (sched[0], sched[1]))
        d.addCallback(self.checkArgs4, tutor, pupil, sbj, scheds, scheds2)
        return d

    def checkArgs5(self, tutor, pupil, sbj, scheds):
        # Revisa que el alumno tenga horas suficientes
        total = sum([sched[1] - sched[0] for sched in scheds]).hours
        print "\nTotal:", total
        d = self.db.db.runQuery("select pc_available >= %f from pupil where id = %d", (total, pupil))
        d.addCallback(self.removeHours, tutor, pupil, sbj, scheds, total)
        return d

    def removeHours(self, data, tutor, pupil, sbj, scheds, total):
        # Disminuye la cantidad de horas PC disponibles para el alumno
        if data[0][0] == False: # No cuenta con horas suficientes de PC
            return 4
        d = self.db.db.runOperation("update pupil set pc_available = pc_available - %f where id = %d", (total, pupil))
        d.addCallback(self.finallyArrange, tutor, pupil, sbj, scheds)
        return d

    def finallyArrange(self, data, tutor, pupil, sbj, scheds):
        if len(scheds) > 0:
            sched = scheds.pop()
            d = self.db.db.runOperation("insert into prearranged_classes (fk_tutor, fk_pupil, time_start, time_end, fk_subject) values (%d, %d, '%s', '%s', %d)", (tutor, pupil, sched[0], sched[1], sbj))
            print "insert into prearranged_classes (fk_tutor, fk_pupil, time_start, time_end, fk_subject) values (%d, %d, '%s', '%s', %d)\n\n" % (tutor, pupil, sched[0], sched[1], sbj)
            d.addCallback(self.finallyArrange, tutor, pupil, sbj, scheds)
            return d
        else:
            return 0

    def unpackSchedule(self, data):
        checks = [False] * LASTDAY_MIDNIGHT
        base = today() + 3
        for row in data:
            start_check = ((row[0].day_of_week - base.day_of_week) % 7) * 48 + row[0].hour * 2 + row[0].minute / 30
            end_check = ((row[1].day_of_week - base.day_of_week) % 7) * 48 + row[1].hour * 2 + row[1].minute / 30
            if end_check <= start_check:
                end_check += LASTDAY_MIDNIGHT
            for hour in range(start_check, end_check):
                checks[hour % LASTDAY_MIDNIGHT] = True
        return checks

    def printContent(self, request, d, userId, msg):
        session = request.getSession()
        _ = session._
        # 1) Chequeamos los argumentos
        if 'sbj' not in request.args.keys() or 'tutor' not in request.args.keys() \
          or 'sch' not in request.args.keys():
            d.addCallback(lambda a: \
                request.write(self.template.unexpectedArguments(session, \
                        _('Faltan argumentos requeridos'))))
            return
        try:
            sbj = int(request.args['sbj'][0])
            tutor = int(request.args['tutor'][0])
            checks = request.args['sch']
            checks = [int(chk) for chk in checks]
            scheds = self.packSchedule(checks)
            print "*** 0 \n\n%s\n\n%s\n\n" % (repr(checks), repr(scheds))
        except ValueError:
            d.addCallback(lambda a: \
               request.write(self.template.unexpectedArguments(session)))
            return
        d.addCallback(self.checkArgs, tutor, userId, sbj, scheds, checks)
        d.addCallback(self.printForm, request)
        return d

    def printForm(self, error_code, request):
        session = request.getSession()
        _ = session._
        if error_code:
            error_msg = ['',
              _('Tutor, alumno o materia inexistente, o ese tutor no esta habilitado para dar esa materia'),
              _('El tutor no esta disponible en algun horario seleccionado'),
              _('El tutor ya tiene compromisos previos para algun horario seleccionado'),
              _('No cuentas con suficientes horas Pre-Coordinadas para esta tutoria')][error_code]

            request.write('<div class="error">' + error_msg + '</div><p>'
              + _('Hubo algun problema.') + ' <a href="/pc_arrange">' +
              _('Vuelve a intentarlo') + '</a></p>\n' + _('O'))
        else:
            request.write('<p>' + _('Clase coordinada con exito') + '</p>')
        request.write(' <a href="/">' + _('Regresa a la pagina principal') + '</a>')
        return
