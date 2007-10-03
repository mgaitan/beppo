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
from twisted.internet import reactor, defer
from twisted.cred import portal
from twisted.web import resource, server
from twisted.application import service, internet
from mx.DateTime import now
from beppo.server.Web.WebRoot import WebRoot
from beppo.server.WBChecker import WBChecker
from beppo.server.WBRealm import WBRealm
from beppo.server.WBRoom import WBRoom
from beppo.server.WBQueuer import WBQueuer
from beppo.server.WBStatus import WBStatus
from beppo.server.Session import SessionAdmin
from beppo.server.cronner import Cronner
from beppo.server.cronTasks import ClassRoomOpenTask, ClassRoomClosingTask, ClassRoomCloseTask, ClassRoomRemoveTask, ClassRoomTimeTask
from beppo.Constants import TUTOR, PUPIL, IACLASS, PACLASS, EXTRA_IACLASS, EXTRA_WAITING, DECIDING, WAITING
from beppo.Constants import IN_QUEUE, IN_CLASS, IN_VIEW, OUT, IN_WAITING, IN_ASKING, IN_DECIDING, POST
from beppo.Constants import GENERAL

class WBServer(pb.Viewable):
    """Servidor que mantiene el estado del WhiteBoard, como asi tambien
    una lista de clientes conectados al mismo, entre los que difunde
    los cambios realizados sobre el WhiteBoard.
    """
    def __init__(self):
        self.wbRooms = {}                       #diccionario con rooms creados (no nec. abiertos)
        self.wbClients = {}                     #usuarios conectados
        self.wbClientStatus = {}                #status de la pizarra de cada cliente (fuera de room)
        self.wbQueues = WBQueuer(self.wbClients)#adm. colas de rooms abiertos

        self.wbRoomsIA = []         #rooms IA que deberian estar funcionando actualmente
        self.wbRoomsPA = []         #rooms PA que deberian estar funcionando actualmente
        self.wbRoomRequests = []    #rooms solicitados

        self.offlineQuestions = {}

        self.sessions = SessionAdmin(self)
        self.cronner = Cronner()
        self.cronner.addJob(ClassRoomOpenTask(self))
        self.cronner.addJob(ClassRoomClosingTask(self))
        self.cronner.addJob(ClassRoomCloseTask(self))
        self.cronner.addJob(ClassRoomTimeTask(self))
        self.cronner.addJob(ClassRoomRemoveTask(self))
        
    def requestRoom(self, roomId):
        if roomId in self.wbRooms.keys():
            return
        if self.openRoom(roomId, self.wbRoomsIA, IACLASS):
            self.manageNextPupil(roomId, self.sessions.tutorEnter)
        elif self.openRoom(roomId, self.wbRoomsPA, PACLASS):
            self.sessions.tutorEnter(roomId, WAITING)
            self.wbClients[roomId].loadPAClass()
            self.setClientWindow(roomId, IN_WAITING)
        else:
            question = "Abrir IA extra?"
            d = self.askClient(roomId, "IA extra", question)
            d.addCallback(self.openExtraRoom, roomId)

    def openRoom(self, roomId, roomList, kind):
        rooms = [str(i[0]) for i in roomList]
        opened = False
        if roomId in rooms:
            room = roomList[rooms.index(roomId)]
            self.addRoom(room, kind)
            opened = True
        return opened

    def openExtraRoom(self, answer, roomId):
        if answer:
            room = (roomId, None)
            self.addRoom(room, EXTRA_IACLASS)
            self.sessionStart(roomId, EXTRA_IACLASS)
        if roomId not in self.wbRoomRequests:
            self.wbRoomRequests.append(roomId)

    def addRoom(self, roomDesc, roomType):
        """Agrega el room de tutorId a los rooms actuales e inicializa
        su cola de espera (un unico room por tutorId); el status del room
        corresponde al status de tutorId.
        """
        assert(roomDesc[0] not in self.wbRooms.keys())
        tutorStatus = self.wbClientStatus[roomDesc[0]]
        self.wbRooms[roomDesc[0]] = WBRoom(roomDesc, roomType, tutorStatus)
        self.wbClients[roomDesc[0]].roomId = roomDesc[0]
        self.wbQueues.addQueue(roomDesc[0])

    def addClient(self, avatar, avatarId):
        """Agrega al avatar a la lista de usuarios actuales, indexado
        con su avatarId. Tambien agrega status de su pizarra.
        """
        self.wbClients[avatarId] = avatar
        avatar.setMyWBColor()
        self.wbClientStatus[avatarId] = WBStatus()

    def itemId(self, avId, tagId):
        return "%s:%d" % (avId, tagId)

    def removeRoom(self, roomId):
        """Quita el room roomId de los rooms actuales; ademas quita a los
        clientes que esperaban por dicho room (y la correspondiente cola) y
        desconecta del mismo a los usuarios que estaban dentro.
        """

        self.setClientWindow(roomId, OUT)
        #si estaba respondiendo pregunta offline
        if self.wbClients[roomId].questionId != None:
            self.sessions.closeSession(roomId)
            self.wbClients[roomId].questionId = None
            return

        #si estaba en espera de ser creado o ya fue eliminado
        if roomId in self.wbRoomRequests:
            self.wbRoomRequests.remove(roomId)

        if roomId not in self.wbRooms.keys():
            return

        room = self.wbRooms[roomId]
        #avisa que se cerro (cuando todavia tendria que estar)
        #cierra la cola
        if room.roomPupilCurrent() != None:
            d = self.wbClients[roomId].saveClassStatus()
            d.addCallback(lambda a: self.sessions.tutorQuit(roomId))
        else:
            self.sessions.tutorQuit(roomId)

        self.exitViewers(roomId)
        self.exitPupils(roomId)
        self.wbClients[roomId].roomId = None
        try:
            self.wbClients[roomId].cleanWhiteBoard()
        except (pb.DeadReferenceError):
            pass
        del(self.wbRooms[roomId])

    def removeClient(self, perspective):
        """Quita al cliente de id clientId de la lista de clientes actuales.
        """
        #si era tutor elimino su room
        if perspective.perspective_whoami() == TUTOR:
            self.removeRoom(perspective.avId)
        else:
            if perspective.viewing != None:
                self.wbRooms[perspective.viewing].roomViewerExit(perspective.avId)
            #si esperaba lo elimino de la cola
            if perspective.waitingInQueue != None:
                self.wbQueues.leaveQueue(perspective.waitingInQueue, perspective.avId)
            #si estaba en "observacion"
            if perspective.waitingInRoom != None:
                self.wbRooms[perspective.waitingInRoom].roomPupilStopWaiting()
                avTutor = self.wbClients[perspective.waitingInRoom]
                avTutor.cleanWhiteBoard()
                self.exitViewers(perspective.waitingInRoom)
                self.manageNextPupil(perspective.waitingInRoom, self.sessions.pupilEnd)
            if perspective.roomId != None:
                self.wbRooms[perspective.roomId].roomPupilExit(perspective.avId)
                discount = (now().minute - perspective.lastMinute) % 60
                perspective.discountIA(discount)
                avTutor = self.wbClients[perspective.roomId]
                try:
                    self.notifyClient(perspective.roomId, "El alumno abandono")
                    avTutor.saveClassStatus()
                    avTutor.cleanWhiteBoard()
                except (pb.DeadReferenceError):
                    pass
                self.exitViewers(perspective.roomId)
                self.manageNextPupil(perspective.roomId, self.sessions.pupilEnd)
        del(self.wbClients[perspective.avId])
        del(self.wbClientStatus[perspective.avId])

    def sessionStart(self, roomId, kind):
        if kind == PACLASS:
            self.sessions.newSession(roomId, kind, WAITING)
            self.setClientWindow(roomId, IN_WAITING)
        else:
            pupilId = self._nextPupil(roomId)
            if pupilId != None:
                self.sessions.newSession(roomId, kind, DECIDING, pupilId)
                self.setClientWindow(roomId, IN_DECIDING)
            else:
                self.sessions.newSession(roomId, kind, WAITING)
                self.setClientWindow(roomId, IN_WAITING)

    def _nextPupil(self, roomId):
        if roomId not in self.wbRooms.keys():
            return None
        if self.wbRooms[roomId].roomIsClosed():
            return None
        pupilId = self.wbQueues.nextClient(roomId)
        if pupilId != None:
            self.wbClients[roomId].cleanWhiteBoard()
            self.wbRooms[roomId].roomPupilCheck(pupilId)
            avClient = self.wbClients[pupilId]
            avTutor = self.wbClients[roomId]
            self.clientUpdate(avTutor, avClient)
            avClient.waitingInQueue = None
            avClient.waitingInRoom = roomId
        return pupilId

    def manageNextPupil(self, roomId, session):
        pupilId = self._nextPupil(roomId)
        if pupilId != None:
            session(roomId, DECIDING, pupilId)
            self.setClientWindow(roomId, IN_DECIDING)
        else:
            session(roomId, WAITING)
            self.setClientWindow(roomId, IN_WAITING)

    def lookForEmptyRoom(self, subject):
        for roomId in self.wbRooms.keys():
            if self.wbRooms[roomId].roomIsEmpty() \
              and self.wbRooms[roomId].roomType() != PACLASS \
              and subject in self.wbClients[roomId].getSelectedSubjects():
                return roomId
        return None

    def view_moveItems(self, perspective, selection, dx, dy):
        items = []
        tagId = self.itemId(perspective.avId, int(perspective.avId))
        for i in selection:
            items.append(self.itemId(perspective.avId, i))
        wbStatus = self.getWorkingStatus(perspective)
        wbStatus.statusMoveItems(items, dx, dy, perspective.avId)
        if perspective.roomId != None:
            for clientId in self.wbRooms[perspective.roomId].roomListClients():
                if perspective.avId != clientId:
                    try:
                        wb = self.wbClients[clientId]
                        d = wb.remote.callRemote("wbMoveItems", tagId, items, dx, dy)
                    except (pb.DeadReferenceError):
                        pass

    def view_eraseItem(self, perspective, selection):
        items = []
        tagId = self.itemId(perspective.avId, int(perspective.avId))
        for i in selection:
            items.append(self.itemId(perspective.avId, i))
        wbStatus = self.getWorkingStatus(perspective)
        wbStatus.statusEraseItem(items, perspective.avId)
        if perspective.roomId != None:
            for clientId in self.wbRooms[perspective.roomId].roomListClients():
                if perspective.avId != clientId:
                    try:
                        wb = self.wbClients[clientId]
                        d = wb.remote.callRemote("wbEraseItem", tagId, items)
                    except (pb.DeadReferenceError):
                        pass

    def view_fillItem(self, perspective, tagId, color):
        item = self.itemId(perspective.avId, tagId)
        wbStatus = self.getWorkingStatus(perspective)
        wbStatus.statusFillItem(item, color, perspective.avId)
        if perspective.roomId != None:
            for clientId in self.wbRooms[perspective.roomId].roomListClients():
                if perspective.avId != clientId:
                    try:
                        wb = self.wbClients[clientId]
                        d = wb.remote.callRemote("wbFillItem", item, color)
                    except (pb.DeadReferenceError):
                        pass

    def view_addItem(self, perspective, tagId, kind, points, outline, fill, width):
        itemId = self.itemId(perspective.avId, tagId)
        wbStatus = self.getWorkingStatus(perspective)
        wbStatus.statusAddItem(itemId, kind, points, outline, fill, width, perspective.avId)
        if perspective.roomId != None:
            for clientId in self.wbRooms[perspective.roomId].roomListClients():
                if perspective.avId != clientId:
                    try:
                        wb = self.wbClients[clientId]
                        d = wb.remote.callRemote("wbAddItem", itemId, kind, points, outline, fill, width)
                    except (pb.DeadReferenceError):
                        pass

    def view_addTextBox(self, perspective, tagId, points, color):
        """Agrega una caja de texto (creada por client) en las coordenadas
        dadas; se actualiza estado en el servidor y si esta dentro de un room
        el cambio se aplica al status de ese room y se difunde a los demas
        clientes; caso contrario actualiza su status solamente.
        """
        self.pupilsInIAClass()
        boxId = self.itemId(perspective.avId, tagId)
        wbStatus = self.getWorkingStatus(perspective)
        wbStatus.statusAddTextBox(boxId, points, color, perspective.avId)
        if perspective.roomId != None:
            for clientId in self.wbRooms[perspective.roomId].roomListClients():
                if perspective.avId != clientId:
                    try:
                        wb = self.wbClients[clientId]
                        d = wb.remote.callRemote("wbAddTextBox", boxId, points, color)
                    except (pb.DeadReferenceError):
                        pass

    def view_insertChars(self, perspective, tagId, index, string):
        """Inserta el texto string desde index en la caja de texto identificada
        por boxId; se actualiza estado en el servidor y si esta dentro de un
        room el cambio se aplica al status de ese room y se difunde a los demas
        clientes; caso contrario actualiza su status solamente.
        """
        boxId = self.itemId(perspective.avId, tagId)
        wbStatus = self.getWorkingStatus(perspective)
        currentText = wbStatus.statusGetField(boxId, "text")
        c = string.decode("utf-8")
        text = currentText.decode("utf-8")
        text = text[:index] + c + text[index:]
        currentText = text.encode("utf-8")
        wbStatus.statusSetField(boxId, "text", currentText)
        if perspective.roomId != None:
            for clientId in self.wbRooms[perspective.roomId].roomListClients():
                if perspective.avId != clientId:
                    try:
                        wb = self.wbClients[clientId]
                        d = wb.remote.callRemote("wbInsertChars", boxId, index, string)
                    except (pb.DeadReferenceError):
                        pass

    def view_deleteChars(self, perspective, tagId, startIndex, endIndex):
        """Borra el texto entre startIndex y endIndex de la caja de texto
        identificada por boxId; se actualiza estado en el servidor y si esta
        dentro de un room el cambio se aplica al status de ese room y se
        difunde a los demas clientes; caso contrario actualiza su status
        solamente.
        """
        boxId = self.itemId(perspective.avId, tagId)
        wbStatus = self.getWorkingStatus(perspective)
        currentText = wbStatus.statusGetField(boxId, "text")
        text = currentText.decode("utf-8")
        text = text[:startIndex] + text[endIndex+1:]
        currentText = text.encode("utf-8")
        wbStatus.statusSetField(boxId, "text", currentText)
        if perspective.roomId != None:
            for clientId in self.wbRooms[perspective.roomId].roomListClients():
                if perspective.avId != clientId:
                    try:
                        wb = self.wbClients[clientId]
                        d = wb.remote.callRemote("wbDeleteChars", boxId, startIndex, endIndex)
                    except (pb.DeadReferenceError):
                        pass

    def view_sendMsg(self, perspective, string):
        """Envia una linea de texto mediante el chat; se actualiza estado en el servidor y si esta dentro de un
        room el cambio se guarda en el log de ese room y se difunde a los demas
        clientes; caso contrario actualiza su status solamente.
        """
        #boxId = self.itemId(perspective.avId, tagId)
        #wbStatus = self.getWorkingStatus(perspective)
        print string
        c = string.decode("utf-8")
        
        wb = self.wbClients[perspective.avId]
        d = wb.remote.callRemote("wbSendMsg", string)
        
        if perspective.roomId != None:
            for clientId in self.wbRooms[perspective.roomId].roomListClients():
                if perspective.avId != clientId:
                    try:
                        wb = self.wbClients[clientId]
                        d = wb.remote.callRemote("wbSendMsg", string)
                    except (pb.DeadReferenceError):
                        pass



    def getWorkingStatus(self, perspective):
        if perspective.roomId != None:
            wbStatus = self.wbRooms[perspective.roomId].wbStatus
        else:
            wbStatus = self.wbClientStatus[perspective.avId]
        return wbStatus

    def clientUpdate(self, perspective, sourceClient):
        """Actualiza el WhiteBoard (vacio) de client y su status al estado
        actual de source en el servidor.
        """
        status = self.wbClientStatus[sourceClient.avId]
        self.clientUpdateFromStatus(perspective, status)

    def clientUpdateFromStatus(self, perspective, status):
        for itemId in status.statusGetKeys():
            wbObject = status.statusGetObject(itemId)
            self.wbClientStatus[perspective.avId].add(itemId, wbObject)
            if wbObject["kind"] == "text":
                perspective.remote.callRemote("wbAddTextBoxFull", itemId, wbObject["points"], wbObject["text"], wbObject["line"])
            else:
                perspective.remote.callRemote("wbAddItem", itemId, wbObject["kind"], wbObject["points"], wbObject["outline"], wbObject["fill"], wbObject["width"])

    def clientUpdateFromStatusModif(self, perspective, status):
        for itemId in status.statusGetKeys():
            wbObject = status.statusGetObject(itemId)
            if wbObject["kind"] == "text":
                perspective.remote.callRemote("wbAddTextBoxFull", None, wbObject["points"], wbObject["text"], wbObject["line"])
            else:
                perspective.remote.callRemote("wbAddItem", POST, wbObject["kind"], wbObject["points"], wbObject["outline"], wbObject["fill"], wbObject["width"])

    def signalEndClass(self, roomId):
        #Cierra cola para evitar nuevos alumnos
        pupilWaiting = self.wbRooms[roomId].roomPupilWaiting()
        if pupilWaiting != None:
            self.wbClients[pupilWaiting].waitingInRoom = None
        # No hay alumnos => elimino room
        if self.wbRooms[roomId].roomPupilCurrent() == None:
            self.removeRoom(roomId)
        self.closeRoomQueue(roomId)

    def signalEndingClass(self, roomId):
        #Avisa a los que estaban esperando en cola
        for clientId in self.wbQueues.clientsWaiting(roomId):
            self.notifyClient(clientId, "La clase esta por terminar")

    def exitPupils(self, roomId):
        pupilWaiting = self.wbRooms[roomId].roomPupilWaiting()
        if pupilWaiting != None:
            self.wbClients[pupilWaiting].waitingInRoom = None
            self.wbClients[pupilWaiting].unlockWhiteBoard()
            self.setClientWindow(pupilWaiting, OUT)
        client = self.wbRooms[roomId].roomPupilCurrent()
        if client != None:
            discount = (now().minute - self.wbClients[client].lastMinute) % 60
            self.wbClients[client].discountIA(discount)
            self.wbClients[client].lastMinute = None
            self.wbClients[client].roomId = None
            self.wbClientStatus[client].statusReset()
            self.wbClients[client].cleanWhiteBoard()
            self.notifyClient(client, "El aula se cerro")
            self.setClientWindow(client, OUT)
            self.wbRooms[roomId].roomPupilExit(client)

    def exitViewers(self, roomId):
        for client in self.wbRooms[roomId].roomListViewers():
            self.wbClients[client].viewing = None
            self.wbClientStatus[client].statusReset()
            self.wbClients[client].cleanWhiteBoard()
            self.wbClients[client].unlockWhiteBoard()
            self.notifyClient(client, "Fin de clase")
            self.setClientWindow(client, OUT)
        self.wbRooms[roomId].roomViewersExit()

    def closeRoomQueue(self, roomId):
        #Avisa cierre de cola; elimina cola
        for client in self.wbQueues.clientsWaiting(roomId):
            self.notifyClient(client, "El aula se cerro")
            self.wbClients[client].waitingInQueue = None
            self.setClientWindow(client, IN_ASKING)
        self.wbQueues.removeQueue(roomId)

    def setClientWindow(self, clientId, desc):
        try:
            self.wbClients[clientId].remote.callRemote("serverClientWindow", desc)
        except (pb.DeadReferenceError):
            pass

    def notifyClient(self, clientId, msg):
        try:
            self.wbClients[clientId].remote.callRemote("serverMessage", msg)
        except (pb.DeadReferenceError):
            pass

    def askClient(self, clientId, title, question):
        try:
            d = self.wbClients[clientId].remote.callRemote("serverQuestion", title, question)
        except (pb.DeadReferenceError):
            d = defer.maybeDeferred(lambda: False)
        return d

    def askStringClient(self, clientId, title, question, initial=""):
        try:
            d = self.wbClients[clientId].remote.callRemote("serverStringQuestion", title, question, initial)
        except (pb.DeadReferenceError):
            d = defer.maybeDeferred(lambda: None)
        return d

    def getRoot(self):
        #rooms = self.openRoomsAndLenQueues()
        #sbOpen = self.shouldBeOpenRooms()
        #r = WebRoot(self.wbClients, rooms, sbOpen)
        r = WebRoot(self)
        return r

    def pupilsInIAClass(self):
        pupils = []
        for clientId in self.wbClients.keys():
            if self.wbClients[clientId].perspective_whoami() == PUPIL \
              and self.wbClients[clientId].roomId != None \
              and (self.wbRooms[self.wbClients[clientId].roomId].roomType() == IACLASS
              or self.wbRooms[self.wbClients[clientId].roomId].roomType() == EXTRA_IACLASS):
                pupils.append(clientId)
        return pupils        

    def connectedUsers(self):
        return self.wbClients

    def openRoomsAndLenQueues(self):
        """
        Devuelve diccionario con clave room abierto
        y valor longitud de cola para ese room;
        incluye cola general (clave: GENERAL)
        """
        return self.wbQueues.getListQueues()

    def shouldBeOpenRooms(self):
        """
        Devuelve lista de rooms que deberian estar abiertos
        """
        return ([str(i[0]) for i in self.wbRoomsIA] + [str(i[0]) for i in self.wbRoomsPA])

    def shouldBeOpenIARooms(self):
        return [str(i[0]) for i in self.wbRoomsIA]

    def shouldBeOpenPARooms(self):
        return [str(i[0]) for i in self.wbRoomsPA]

    def shouldBeOpenAndClosedRooms(self):
        """
        Devuelve lista de rooms que debieran estar abiertos y no están
        """
        ret = []
        sbOpen = self.shouldBeOpenRooms()
        rOpen = self.openRoomsAndLenQueues()
        for room in sbOpen:
            if not rOpen.has_key(room):
                ret.append(room)
        return ret

    def openRoomsAndSubjects(self):
        ret = {}
        for roomId in self.wbRooms.keys():
            ret[roomId] = self.wbClients[roomId].getSelectedSubjects()
        return ret

    def roomInfo(self, roomId):
        d = self.wbQueues.queueInfo(roomId)
        if roomId != GENERAL:
            d.addCallback(self._getRoomInfo)
        return d

    def _getRoomInfo(self, res):
        roomId = str(res[0][0])
        tutor = res[0][1] + " " + res[0][2]
        if self.wbRooms[roomId].endTime != None:
            end = self.wbRooms[roomId].endTime.strftime("%H:%M")
        else:
            end = None
        kind = self.wbRooms[roomId].roomType()
        subjects = self.wbClients[roomId].getSubjects()
        selSubjects = [s for s in subjects.keys() if subjects[s]]

        return (tutor, kind, end, selSubjects)

#        roomId = str(res[0][0])
#        info = _("Tutor") + ": " + res[0][1] + " " + res[0][2]
#        if self.wbRooms[roomId].roomType() == IACLASS:
#            end = self.wbRooms[roomId].endTime
#            info = info + "\n" + _("Tipo de clase") + ": " + _("Acceso instantaneo") + "\n" + _("Hora de cierre") + ": " + end.strftime("%H:%M")
#        elif self.wbRooms[roomId].roomType() == PACLASS:
#            end = self.wbRooms[roomId].endTime
#            info = info + "\n" + _("Tipo de clase") + ": " + _("Precoordinada") + "\n" + _("Hora de cierre") + ": " + end.strftime("%H:%M")
#        else:
#            info = info + "\n" + _("Tipo de clase") + ": " + _("Acceso instantaneo (extra)")
#        info = info + "\n" + _("Materias") + ":\n"
#        subjects = self.wbClients[roomId].getSubjects()
#        for s in subjects.keys():
#            if subjects[s]:
#                info = info + "\t" + s + "\n"
#        return info

wbServer = WBServer()
realm = WBRealm()
realm.server = wbServer
p = portal.Portal(realm)
c = WBChecker(wbServer.wbClients)
p.registerChecker(c)
factory = pb.PBServerFactory(p)
application = service.Application('wb')
serviceCollection = service.IServiceCollection(application)
internet.TCPServer(10102, factory).setServiceParent(serviceCollection)
internet.TCPServer(10101, server.Site(wbServer.getRoot())).setServiceParent(serviceCollection)
