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

from twisted.internet import reactor, defer
from cronner import HourlyCronJob, MultiHourlyCronJob
from time import localtime, mktime, time
from mx.DateTime import DateTime, now, RelativeDateTime
from DBConnect import DBConnect
from twisted.python import log
from beppo.Constants import IACLASS, PACLASS, WAITING, ABSENT, EXTRA_IACLASS, DECIDING
from beppo.Constants import SERVER_RESTART, NORMAL


class ClassRoomOpenTask(MultiHourlyCronJob):
    """
    Actualiza la lista de rooms que deberian estar abiertos
    la hora siguiente; si el room habia sido solicitado,
    se abre.
    """
    def __init__(self, server):
        MultiHourlyCronJob.__init__(self, minutes=[28, 58])
        self.db = DBConnect()
        self.server = server
        self.server.sessions.closeAll(SERVER_RESTART)

        query = """select fk_tutor, time_end from tutor_schedule
            where (time_start <= '%s' and time_end >= '%s')
            or (time_start <= '%s' and time_end >= '%s')
            """
        self._restoring(query, self.server.wbRoomsIA, IACLASS)
        query2 = """select fk_tutor, time_end from prearranged_classes
            where (time_start <= '%s' and time_end >= '%s')
            """
        self._restoring(query2, self.server.wbRoomsPA, PACLASS)
        
    def run(self):
        print "OPENING..."
        #rooms que deberian estar abiertos la hora proxima
        query = """select fk_tutor, time_end from tutor_schedule 
            where time_start = '%s'
            """
        self._opening(query, self.server.wbRoomsIA, IACLASS)
        query2 = """select fk_tutor, time_end from prearranged_classes
            where time_start = '%s'
            """
        self._opening(query2, self.server.wbRoomsPA, PACLASS)

    def _restoring(self, query, roomList, kind):
        day = now()
        if kind == IACLASS:
            day1 = DateTime(2005, 5, (1 + day.day_of_week) % 7 + 1, day.hour, day.minute)
            day2 = DateTime(2005, 5, (1 + day.day_of_week) % 7 + 8, day.hour, day.minute)
            day1_start = day1 + RelativeDateTime(minute=day.minute+2)
            day2_start = day2 + RelativeDateTime(minute=day.minute+2)
            d = self.db.db.runQuery(query, (day1_start, day1, day2_start, day2))
        elif kind == PACLASS:
            d = self.db.db.runQuery(query, (day, day))
        d.addCallback(self._updateRooms, roomList)
        d.addCallback(self._openRooms, roomList, kind)

    def _restoringPA(self, query, roomList, kind):
        day = now()
        day1 = DateTime(2005, 5, (1 + day.day_of_week) % 7 + 1, day.hour, day.minute)
        day2 = DateTime(2005, 5, (1 + day.day_of_week) % 7 + 8, day.hour, day.minute)
        day1_start = day1 + RelativeDateTime(minute=day.minute+2)
        day2_start = day2 + RelativeDateTime(minute=day.minute+2)

        d = self.db.db.runQuery(query, (day1_start, day1, day2_start, day2))
        d.addCallback(self._updateRooms, roomList)
        d.addCallback(self._openRooms, roomList, kind)

    def _opening(self, query, roomList, kind):
        day = now()
        if kind == IACLASS:
            day = DateTime(2005, 5, (1 + day.day_of_week) % 7 + 1, day.hour, day.minute)
        day = day + RelativeDateTime(minute=day.minute+2)

        d = self.db.db.runQuery(query, (day,))
        d.addCallback(self._updateRooms, roomList)
        d.addCallback(self._openRooms, roomList, kind)
       
    def _updateRooms(self, res, roomList):
        for i in range(len(res)):
            roomDesc = (str(res[i][0]), res[i][1])
            if roomDesc not in roomList:
                roomList.append(roomDesc)

    def _openRooms(self, data, roomList, kind):
        opened = []
        for room in roomList:
            if room[0] in self.server.wbRoomRequests:
                if room[0] in self.server.wbRooms.keys():
                    pupilId = self.server.wbRooms[room[0]].roomPupilCurrent()
                    self.server.wbRooms[room[0]].setRoomType(kind, room[1])
                    self.server.sessions.changeSessionKind(room[0], kind, pupilId)
                else:
                    #self.server.addRoom(room, kind)
                    # abro sesion de espera
                    self.server.openRoom(room[0], roomList, kind)
                    self.server.sessionStart(room[0], kind)
                if kind == PACLASS:
                    self.server.wbClients[room[0]].loadPAClass()
                opened.append(room[0])
            elif not self.server.sessions.hasOpenSession(room[0]):
                # abro sesion de ausente
                self.server.sessions.newSession(room[0], kind, ABSENT)
        for room in opened:
            self.server.wbRoomRequests.remove(room)
        print "ROOMS DEBERIAN:", self.server.shouldBeOpenRooms()

class ClassRoomClosingTask(MultiHourlyCronJob):
    """
    Notifica a los clientes encolados en un room cuyo horario
    de cierre esta proximo
    """
    def __init__(self, server):
        MultiHourlyCronJob.__init__(self, minutes=[15, 45])
        self.db = DBConnect()
        self.server = server
        
    def run(self):
        print "NOTIFY CLOSING..."
        for room in self.server.wbRoomsIA + self.server.wbRoomsPA:
            if room[0] in self.server.wbRooms.keys() and self.server.wbRooms[room[0]].roomIsClosing():
                self.server.signalEndingClass(room[0])
                
class ClassRoomCloseTask(MultiHourlyCronJob):
    """
    Cierra los rooms que alcanzaron la hora de cierre
    a la hora actual, siempre que no esten atendiendo una clase
    """
    def __init__(self, server):
        MultiHourlyCronJob.__init__(self, minutes=[0, 30])
        self.db = DBConnect()
        self.server = server

    def _closing(self, roomList):
        roomsToRemove = []
        y, m, d, hs, ms, ss, wd, yd, c = localtime()
        for room in roomList:
            if room[0] in self.server.wbRooms.keys() and self.server.wbRooms[room[0]].roomIsClosed():
                self.server.signalEndClass(room[0])
                roomsToRemove.append(room)
            elif room[1].day_of_week == wd and (room[1].hour < hs or (room[1].hour == hs and room[1].minute <= ms)):
                # cierro sesion (estaba ausente)
                self.server.sessions.closeSession(room[0])
                roomsToRemove.append(room)
        for room in roomsToRemove:
             roomList.remove(room)

    def run(self):
        print "CLOSING..."
        self._closing(self.server.wbRoomsIA)
        self._closing(self.server.wbRoomsPA)
        print "ROOMS DEBERIAN:", self.server.shouldBeOpenRooms()

class ClassRoomRemoveTask(MultiHourlyCronJob):
    """
    Elimina los rooms que llevan cierto tiempo de cerrado y
    todavia tienen alumnos
    """
    def __init__(self, server):
        MultiHourlyCronJob.__init__(self, minutes=[15, 45])
        self.db = DBConnect()
        self.server = server
        
    def run(self):
        print "REMOVING..."
        roomsToRemove = []
        for roomId in self.server.wbRooms.keys():
            if self.server.wbRooms[roomId].roomIsClosed():
                roomsToRemove.append(roomId)
        for room in roomsToRemove:
             self.server.removeRoom(room)


class ClassRoomTimeTask(MultiHourlyCronJob):
    """
    Descuenta tiempo de clase a los alumnos
    """
    def __init__(self, server):
        MultiHourlyCronJob.__init__(self, minutes=[i*5 for i in range(0,12)])
        self.db = DBConnect()
        self.server = server
        
    def run(self):
        print "CASHING..."
        pupils = self.server.pupilsInIAClass()
        d = self.getAvailable(pupils)
        d.addCallback(self._discounting)
        
    def _discounting(self, available):
        minutes = now().minute
        for clientId in available.keys():
            if available[clientId] > 0:
                delta = (minutes - self.server.wbClients[clientId].lastMinute) % 60
                delta = delta / 60.0
                if delta >= available[clientId]:
                    self.server.notifyClient(clientId, "No tiene mas horas disponibles")
                    self.server.wbClients[clientId].perspective_leaveRoom()
                else:
                    disc_query = """update pupil set ai_available = ai_available - %f where id = %d"""
                    d = self.db.db.runOperation(disc_query, (delta, int(clientId)))
                    self.server.wbClients[clientId].lastMinute = minutes

    def getAvailable(self, pupils):
        if len(pupils) > 0:
            ids = tuple(pupils + [0])
            av_query = """select id, ai_available from pupil where id in %s"""
            d = self.db.db.runQuery(av_query, (ids,))
            d.addCallback(self._getAvailable)
        else:
            d = defer.maybeDeferred(lambda: {})
        return d

    def _getAvailable(self, res):
        ret = {}
        for row in res:
            ret[str(row[0])] = row[1]
        return ret

