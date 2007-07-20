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
from WebTemplates import WebTemplates
from psycopg import QuotedString
from beppo.server.utils import getTranslatorFromSession
from beppo.Constants import GENERAL, ADMIN, TUTOR
from beppo.server.DBConnect import DBConnect
import cgi

class WebRoomInfo(Resource):
    def __init__(self, server):
        self.db = DBConnect
        self.rOpen = server.openRoomsAndLenQueues # clave room -> valor cant gente
        self.subjects = server.openRoomsAndSubjects # clave room -> valor lista materias
        self.sbOpen = server.shouldBeOpenAndClosedRooms
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
        request.write(self.template.startPage(session, \
            _('Informacion de Pizarras en el sistema')))
        d = defer.maybeDeferred(lambda :None)
        if not hasattr(session, 'username'):
            request.write(self.template.notAuthenticated(session))
        # 2) Si es Admin, administra todos los usuarios
        elif session.kind == ADMIN:
            msg = '<h2>' + _('Estado del sistema') + '</h2>' + \
            _('Aqui se muestran las aulas que se encuentran abiertas, una descripcion de ellas y la lista de aulas que deberian estar abiertas.')
        # La función que procesa e imprime el contenido de la pagina
        else:
            msg = '<h2>' + _('Estado del sistema') + '</h2>' + \
            _('Aqui se muestran las aulas que se encuentran abiertas y una descripcion de ellas')
        self.printContent(request, d, session, msg)
        # 5) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return d


    def printContent(self, request, d, session, msg):
        rOpen = self.rOpen()
        subjects = self.subjects()
        d.addCallback(lambda a: request.write(msg))
        d.addCallback(lambda a: self._getORoomInfo(rOpen))
        d.addCallback(self._printORoomTable, request, rOpen, subjects)
        if session.kind == ADMIN:
            d.addCallback(lambda a: self._getSBORoomInfo(self.sbOpen()))
            d.addCallback(self._printSBORoomTable, request)
        # 2) Se imprime un mensaje de bienvenida configurable
        return d


    def _getORoomInfo(self, openRooms):
        ids = tuple([int(b) for b in openRooms.keys() if b != GENERAL] + [0])
        if len(ids) > 1:
            query = "select username, id from person where id in %s"
            d = self.db.db.runQuery(query, (ids,))
        else:
            d = defer.maybeDeferred(lambda: [])
        return d

    def _getSBORoomInfo(self, sbopenRooms):
        if sbopenRooms != []:
            query = "select username, id from person where id in %s"
            d = self.db.db.runQuery(query, (tuple(sbopenRooms + [0]),))
        else:
            d = defer.maybeDeferred(lambda: [])
        return d

    def _printORoomTable(self, rows, request, openRooms, subjects):
        _ = request.getSession()._
        page = """<br/><br/>
<table class="table_list" id="opened_rooms">
 <caption>""" + _('Aulas abiertas:') + """</caption>
 <tr class="header_list">
  <th>""" + _('Aula') + """</th>
  <th>""" + _('Usuarios conectados') + """</th>
  <th>""" + _('Tutor a cargo') + """</th>
  <th>""" + _('Materias') + """</th>
 </tr>"""
        if len(openRooms) == 1:
            page += '<tr><td colspan ="4" style="text-align: center">' + \
                _('Ningun aula abierta') + ' </td></tr>'
        else:
            for room in rows:
                rm = room[1]
                connected = openRooms.get(str(room[1]))
                in_charge = "<a href='/tutor_data?user_id=%s'> %s </a>" % (room[1], room[0])
                sub = self.printSubjects(subjects.get(str(room[1])))
                page += """
 <tr>
  <td> %s </td>
  <td> %s </td>
  <td> %s </td>
  <td> %s </td></tr>""" % (rm, connected, in_charge, sub) + """ </td></tr>"""
        page += '</table><br/><br/>'
        page += _('Usuarios en la cola general:') + '%d' % openRooms.get(GENERAL)
        request.write(page)

    def printSubjects(self, subjects):
        return " - ".join(subjects)


    def _printSBORoomTable(self, rows, request):
        _ = request.getSession()._
        page = """<br/><br/>
<table class="table_list" id="sbopen_rooms">
 <caption>""" + _('Aulas que deberian estar abiertas y no estan:') + """</caption>
 <tr class="header_list">
  <th>""" + _('Aula') + """</th>
  <th>""" + _('Tutor') + """</th>
 </tr>"""
        if len(rows) == 0:
           page += """
<tr><td colspan ="3" style="text-align: center">""" + \
     _('No hay tutores ausentes') +  """</td></tr>"""
        else:
            for room in rows:
                page += """
 <tr>
  <td> %s </td>
  <td> <a href="/tutor_data?user_id=%s"> %s </a> </td>
 </tr>""" % (room[1], room[1], room[0])

        page += '</table>'
        request.write(page)
