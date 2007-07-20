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

from twisted.spread import pb
from twisted.internet import defer
from DBConnect import DBConnect
from psycopg import QuotedString
from mx.DateTime import now
from ClientAvatar import ClientAvatar
from beppo.Constants import GENERAL, TUTOR, PUPIL, PUPIL_COLOR, PACLASS, OFFLINEQ_COST
from beppo.Constants import IN_QUEUE, IN_CLASS, IN_VIEW, OUT, IN_WAITING, IN_ASKING

class Pupil(ClientAvatar):
    def __init__(self, avId, server):
        ClientAvatar.__init__(self, avId, server)
        self.lastMinute = None
        self.waitingInQueue = None
        self.waitingInRoom = None
        self.viewing = None
        self.hasQuestion = False
        self._searchSubjects()

    def setMyWBColor(self):
        self.remote.callRemote("wbMyColor", PUPIL_COLOR)

    def perspective_whoami(self):
        return PUPIL

    def _searchSubjects(self):
        query = """select name from subject"""
        d = self.db.db.runQuery(query)
        d.addCallback(self._loadSubjects)

    def getSubject(self):
        return self.selectedSubject
        
    def perspective_proposeQuestion(self):
        if self.selectedSubject == None:
            self.remote.callRemote("wbShowSubjects")
            self.server.notifyClient(self.avId, "Elegir una materia")
            return False
        self.hasQuestion = True
        #self.server.setClientWindow(self.avId, IN_ASKING)
        self.lockWhiteBoard()
        return True

    def perspective_unproposeQuestion(self):
        self.hasQuestion = False
        #self.server.setClientWindow(self.avId, OUT)
        self.unlockWhiteBoard()

    def _checkEnter(self, roomId):
        if self.waitingInQueue != None or self.roomId != None \
          or self.waitingInRoom != None or self.viewing != None:
            return defer.maybeDeferred(lambda: False)
        if roomId not in self.server.wbQueues.roomList():
            return defer.maybeDeferred(lambda: False)
        if roomId != GENERAL and self.server.wbRooms[roomId].roomType() == PACLASS:
            return defer.maybeDeferred(lambda: self._isMyPARoom(roomId))
        if roomId != GENERAL and self.server.wbRooms[roomId].roomIsClosing():
            self.server.notifyClient(self.avId, "La clase esta por terminar")
            return defer.maybeDeferred(lambda: False)
        if not self.hasQuestion:
            if not self.perspective_proposeQuestion():
                #self.server.notifyClient(self.avId, "Proponer pregunta")
                return defer.maybeDeferred(lambda: False)
        d = self.IAHoursAvailable()
        d.addCallback(self._checkMinutesAvailable, 0)
        d.addCallback(self._checkSubject, roomId)
        return d

    def _isMyPARoom(self, roomId):
        if self.server.wbClients[roomId].paPupil == self.avId:
            return True
        self.server.notifyClient(self.avId, "Clase precoordinada (acceso no permitido)")
        return False

    def _checkSubject(self, hsAvail, roomId):
        if not hsAvail:
            return defer.maybeDeferred(lambda: False)
        if roomId == GENERAL:
            return defer.maybeDeferred(lambda: True)
        if self.selectedSubject in self.server.wbClients[roomId].getSelectedSubjects():
            return defer.maybeDeferred(lambda: True)
        else:
            d = self.server.askClient(self.avId, "Encolar", "Tutor no da materia. Entrar?")
            return d

    def _enterRoom(self, check, roomId):
        if not check:
            return
        self.server.wbQueues.enterQueue(roomId, self.avId)
        self.server.setClientWindow(self.avId, IN_QUEUE)
        self.waitingInQueue = roomId
        if roomId != GENERAL and self.server.wbRooms[roomId].roomIsEmpty():
            self.server.manageNextPupil(roomId, self.server.sessions.tutorDecide)
        elif roomId == GENERAL and self.server.wbQueues.lenQueue(roomId) == 1:
            room = self.server.lookForEmptyRoom(self.selectedSubject)
            if room != None:
                self.server.manageNextPupil(room, self.server.sessions.tutorDecide)

    def perspective_enterRoom(self, roomId):
        d = self._checkEnter(roomId)
        d.addCallback(self._enterRoom, roomId)

    def perspective_leaveRoom(self):
        self.perspective_unproposeQuestion()
        self.server.setClientWindow(self.avId, OUT)
        #si estaba observando
        if self.viewing != None:
            self.server.wbRooms[self.viewing].roomViewerExit(self.avId)
            self.cleanWhiteBoard()
            self.unlockWhiteBoard()
            self.viewing = None
            #self.server.setClientWindow(self.avId, OUT)
        #si estaba esperando
        if self.waitingInQueue != None:
            self.server.wbQueues.leaveQueue(self.waitingInQueue, self.avId)
            self.waitingInQueue = None
            #self.server.setClientWindow(self.avId, IN_ASKING)
        #si estaba siendo observado
        if self.waitingInRoom != None:
            self.server.exitViewers(self.waitingInRoom)
            self.server.wbRooms[self.waitingInRoom].roomPupilStopWaiting()
            #self.server.setClientWindow(self.avId, IN_ASKING)
            avTutor = self.server.wbClients[self.waitingInRoom]
            avTutor.cleanWhiteBoard()
            self.server.manageNextPupil(self.waitingInRoom, self.server.sessions.pupilEnd)
            self.waitingInRoom = None
        #si estaba en un room
        if self.roomId != None:
            #estaba en un room
            self.server.notifyClient(self.roomId, "El alumno abandono")
            avTutor = self.server.wbClients[self.roomId]
            avTutor.saveClassStatus()
            avTutor.cleanWhiteBoard()
            discount = (now().minute - self.lastMinute) % 60
            self.discountIA(discount)
            self.server.exitViewers(self.roomId)
            self.server.wbRooms[self.roomId].roomPupilExit(self.avId)
            self.cleanWhiteBoard()
            # alumno cierra sesion de clase; se abre de espera
            self.server.setClientWindow(self.roomId, IN_WAITING)
            #self.server.setClientWindow(self.avId, OUT)
            self.server.manageNextPupil(self.roomId, self.server.sessions.pupilEnd)
            self.roomId = None
            self.lastMinute = None

    def perspective_offQuestion(self):
        if self.selectedSubject == None:
            self.remote.callRemote("wbShowSubjects")
            self.server.notifyClient(self.avId, "Elegir una materia")
            return
        if self.roomId == None and self.waitingInRoom == None and self.viewing == None:
            d = self.server.askClient(self.avId, "Pregunta offline", "Guardar pregunta offline?")
            d.addCallback(self._checkQuestion)
            d.addCallback(self._saveQuestion)

    def _checkQuestion(self, answer):
        if answer:
            d = self.IAHoursAvailable()
            d.addCallback(self._checkMinutesAvailable, OFFLINEQ_COST)
        else:
            d = defer.maybeDeferred(lambda: False)
        return d

    def _saveQuestion(self, check):
        if check:
            d = self.discountIA(OFFLINEQ_COST)
            d.addCallback(lambda a: self.cleanExtraWhiteBoard())
            d.addCallback(lambda a: self._saveStatus())
            d.addCallback(lambda a: self.server.notifyClient(self.avId, "Pregunta guardada"))
            d.addCallback(lambda a: self.cleanWhiteBoard())
            d.addErrback(lambda a: self.server.notifyClient(self.avId, "Pregunta no guardada"))
        
    def _saveStatus(self):
        date = now()
        status = self.server.wbClientStatus[self.avId].pickle()
        queryIdSubject = """select id from subject where name=%s"""
        query = """insert into offline_questions (fk_pupil, fk_subject, time_submit, status)
            values (%s, %s, '%s', %s)
            """
        status = QuotedString(status)
        d = self.db.db.runQuery(queryIdSubject, (self.selectedSubject,))
        d.addCallback(lambda idRes: self.db.db.runOperation(query, (self.avId, idRes[0][0], date, status)))
        return d       

    def perspective_enterViewer(self, roomId):
        if self.roomId == None and self.waitingInRoom == None \
          and self.waitingInQueue == None and roomId != GENERAL \
          and not self.server.wbRooms[roomId].roomIsEmpty():
            self.server.wbRooms[roomId].roomViewerEnter(self.avId)
            self.cleanWhiteBoard()
            self.lockWhiteBoard()
            self.viewing = roomId
            room = self.server.wbClients[roomId]
            self.server.clientUpdate(self, room)
            self.server.setClientWindow(self.avId, IN_VIEW)

    def IAHoursAvailable(self):
        hs_query = """select ai_available from pupil where id = %d"""
        d = self.db.db.runQuery(hs_query, (int(self.avId),))
        d.addCallback(lambda res: res[0][0])
        return d

    def discountIA(self, minutes):
        d = self.IAHoursAvailable()
        d.addCallback(self._discount, minutes)
        return d

    def _discount(self, available, minutes):
        hours = minutes/60.0
        disc = min(hours, available)
        dc_query = """update pupil set ai_available = ai_available - %f where id = %d"""
        d = self.db.db.runOperation(dc_query, (disc, int(self.avId)))
        return d

    def _checkMinutesAvailable(self, hs, minutesReq):
        if hs <= (minutesReq / 60.0):
            self.server.notifyClient(self.avId, "No tiene suficientes horas disponibles")
            return False
        return True
