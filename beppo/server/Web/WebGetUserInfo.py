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
from twisted.enterprise import adbapi
from twisted.internet import defer
from beppo.server.DBConnect import DBConnect
from beppo.server.utils import dummyTranslator
from beppo.server.utils import timezoneToString
from beppo.Constants import CLIENT, PUPIL, ADMIN, TUTOR
from beppo.Constants import DATETIME_FORMAT

class WebGetUserInfo:
    _ = dummyTranslator
    """ QUERY: diccionario de consultas. una consulta para cada tipo de usuario.
        se incluyen los datos que se quieren mostrar como informacion util
        del usuario
        ROWS: nombre de las columnas a mostrar para cada tipo de usuario
    """
    QUERY = {TUTOR: "select username, first_name, last_name, email, \
         language.name, fk_timezone, address1, address2, zip, phone1, \
         phone2, phone3, icq, msn, aol from tutor, person, language, \
         timezone where person.id = %d and person.id = tutor.id \
         and fk_timezone = timezone.id and person.language = language.id",
     CLIENT: "select username, first_name, last_name, email, language.name, \
          fk_timezone, organization, ai_available, pc_available from client, \
          person, language, timezone where person.id = %d and client.id = person.id \
          and fk_timezone = timezone.id and person.language = language.id",
     ADMIN: "select username, first_name, last_name, email, language.name, fk_timezone \
          from person, language, timezone where person.id = %d and fk_timezone = timezone.id \
          and person.language = language.id",
     PUPIL: "select username, first_name, last_name, email, language.name, \
          fk_timezone, organization, client.id from pupil, person, client, language, \
          timezone where pupil.id = person.id and client.id = pupil.fk_client and \
          person.id = %d and pupil.id = person.id and person.fk_timezone = timezone.id \
          and person.language = language.id"}
    ROWS = {TUTOR: [_('Usuario:'), _('Nombre:'), _('Apellido:'), _('eMail:'), \
         _('Idioma:'), _('Zona horaria:'), _('Direccion 1:'), _('Direccion 2:'), \
         _('Codigo postal:'), _('Telefono 1:'), _('Telefono 2:'), _('Telefono 3:'), \
         _('ICQ:'), _('MSN:'), _('AOL:')],
     CLIENT: [_('Usuario:'), _('Nombre:'), _('Apellido:'), _('eMail:'), \
         _('Idioma:'), _('Zona horaria:'),_('Organizacion:'), \
         _('Horas disponibles (AI):'), _('Horas disponibles (CP):')],
     ADMIN: [_('Usuario:'), _('Nombre:'), _('Apellido:'), _('eMail:'), \
         _('Idioma:'), _('Zona horaria:'),],
     PUPIL: [_('Usuario:'), _('Nombre:'), _('Apellido:'), _('eMail:'), \
         _('Idioma:'), _('Zona horaria:'), _('Organizacion cliente:')]}

    def __init__(self, db, session):
        self.db = db
        self.session = session

    def getUserInfo(self, userId, kind):
        """
        busca los datos del usuario userId (de tipo kind) en la
        base de datos
        """
        try:
            query = self.QUERY[kind]
            d = self.db.db.runQuery(query, (userId,))
        except KeyError:
            d = defer.maybeDeferred(lambda: [])
        d.addCallback(self._getTable, kind, userId)
        return d

    def getFormattedField(self, field, i):
        """ Dependiendo del numero de fila, aplica alguna funcion
            de formato para los datos
        """
        if i == 5:
            return timezoneToString(field)
        else:
            return field

    def _getTable(self, rows, usr, userId):
        """ Toma la informacion de un usuario (en rows), un tipo de usuario (usr)
         y un userId y arma una tabla con la informacion del usuario.
         Ademas agrega un link de modificacion en caso de que se tenga la
         autorizacion necesaria
        """
        _ = self.session._
        if len(rows) != 1:
            page = '<div class="message">' + _('El usuario no existe') + '</div>'
        else:
            page = '<table class="table_info" id="userinfo_table">'
            row = rows[0]
            columns = len(self.ROWS.get(usr))
            for i in range(columns):
                page += """
<tr><th class="header_userinfo">%s</th>
    <td>%s</td></tr>""" % (_(self.ROWS.get(usr)[i]), self.getFormattedField(row[i], i))
            page += """</table>"""
            if self.session.kind == ADMIN:
                if usr == CLIENT:
                    page += '<a href="/client?user_id=%s" id="userInfoModify">' \
                     % userId + _('Modificar datos') + '</a>'
                elif usr == TUTOR:
                    page += '<a href="/tutor?user_id=%s" id="userInfoModify">'  \
                     % userId + _('Modificar datos') + '</a>'
                elif usr == PUPIL:
                    page += '<a href="/pupil_edit?pupil_id=%s&user_id=%s" id="userInfoModify">'  \
                    % (userId, row[7]) + _('Modificar datos') + '</a>'
            elif self.session.userId == userId:
                if usr == CLIENT:
                    page += '<a href="/client?user_id=%s" id="userInfoModify">' \
                     % userId + _('Modificar datos') + '</a>'
            elif self.session.kind == CLIENT:
                if usr == PUPIL:
                    page += '<a href="/pupil_edit?pupil_id=%s" id="userInfoModify">' \
                     % userId + _('Modificar datos') + '</a>'
        page += ' <a href="javascript:history.back()" id="back">' + _('Volver') + '</a>'
        return page

    def getPAFromTutor(self, userId, date):
        """Dado un userId de tutor, busca la informacion de las
           clases precoordinadas del tutor que terminen despues
           de date
        """
        query = "select p2.id, p2.username, time_start, \
                 time_end, s.name from person p, person p2, subject s, \
                 prearranged_classes c where c.fk_tutor = p.id and \
                 c.fk_pupil = p2.id and c.fk_subject = s.id and \
                 p.id = %d and time_end > '%s' order by time_start asc"
        d = self.db.db.runQuery(query, (userId, date))
        d.addCallback(self._getPATable)
        return d

    def _getPATable(self, rows):
        """toma la informacion de las clases precoordinadas de un tutor,
           y arma una tabla con esta informacion.
           El contenido de cada fila row de rows es:
           row[0] = pupil id
           row[1] = pupil username
           row[2] = pa time_start
           row[3] = pa time_end
           row[4] = subject name
        """
        _ = self.session._
        if len(rows) == 0:
            table = '<div class="client_info">' + _('No tienes clases precoodinadas para estos dias. Recuerda revisar periodicamente tus horarios para no perder ninguna clase.') + '</div>'
        else:
            msg = _('Aqui hay una lista de las clases precoordinadas que tienes en estos dias, junto con los alumnos que la tomaran. Recuerda presentarte con anticipacion a tus clases.')
            table = '<div class="spaced">' + msg + '</div>'
            table += '<table class="table_info" id="pa_info">'
            table += '<caption>' + _('Tus clases precoordinadas') + '</caption>'
            table += """<tr>
        <th class="header_list">""" + _('Fecha inicio') + """</th>
        <th class="header_list">""" + _('Fecha fin') + """</th>
        <th class="header_list">""" + _('Alumno') + """</th>
        <th class="header_list">""" + _('Materia') + """</th>
       </tr>"""
            for row in rows:
                start = row[2].Format(DATETIME_FORMAT)
                end = row[3].Format(DATETIME_FORMAT)
                table += """<tr class='row_list'>
    <td> %s </td>
    <td> %s </td>
    <td><a href="pupil_info?user_id=%d"> %s </a></td>
    <td> %s </td></tr>""" % (start, end, row[0], row[1], row[4])
            table += """</table>"""
        return table

    def getHours(self, kind, userId):
        """Dado un userId (de alumno o cliente), busca la informacion de las horas
           restantes en la base de datos
        """
        if kind == PUPIL:
            table = "pupil"
        elif kind == CLIENT:
            table = "client"
        query = "select ai_available, pc_available from " + table + " where id = %d"
        d = self.db.db.runQuery(query, (userId,))
        d.addCallback(self._getHoursDiv, kind)
        return d

    def _getHoursDiv(self, rows, kind):
        """toma la informacion de las horas disponibles de un alumno
           o cliente y arma un div con esa informacion
           El contenido de rows es (se exige que tenga una sola columna)
           rows[0][0] = ai_available hours
           row[0][1] = pc_available hours
        """
        _ = self.session._
        if len(rows) != 0:
            ai = rows[0][0]
            pc = rows[0][1]
            if ai == 0 and pc == 0:
                if kind == CLIENT:
                    msg = _('Recuerde que sin horas disponibles no puede dar de alta alumnos. Contactese con el administrador del sistema para solicitarle mas horas. Tenga en cuenta que las horas de sus alumnos tienen un vencimiento, y que al terminar sus horas debe darlos de alta como alumnos nuevos.')
                elif kind == PUPIL:
                    msg = _('Recuerda que sin horas disponibles no puedes tomar clases ni hacer preguntas. Puedes solicitar mas horas a quien te haya inscripto en el sistema, pero te deben dar de alta como un nuevo alumno.')
                div = '<div class="no_hours">' + _('No le quedan horas disponibles.') \
                    + msg + '</div>'
            else:
                if kind == CLIENT:
                    msg = _('Recuerde que las horas de sus alumnos tienen un vencimiento. Puede contactarse con el administrador del sistema para solicitarle horas para sus alumnos.')
                elif kind == PUPIL:
                    msg = ""
                div = '<div class="client_info">'
                div += '<ul><li>' + _('Horas de Acceso Instantaneo disponibles') \
                    + ': ' + str(ai) + '</li>'
                div += '<li>' + _('Horas de Clases Precoordinadas disponibles') + ': ' \
                    + str(pc) + '</li></ul></div>' + msg
        else:
            div = ""
        return div
