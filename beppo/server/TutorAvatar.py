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

from twisted.internet import defer
from mx.DateTime import now
from WBQueuer import WBQueuer
from WBStatus import WBStatus
from psycopg import QuotedString
from ClientAvatar import ClientAvatar
from beppo.Constants import GENERAL, TUTOR, PUPIL, TUTOR_COLOR, ARCHIVE_DIR, ARCHIVE_EXT, PS_TO_EXT, PS_OPTIONS, PS_INFILE, PS_OUTFILE
from beppo.Constants import IN_QUEUE, IN_CLASS, IN_VIEW, OUT, IN_WAITING, IN_ANSWERING, IN_POST_PROCESS
import os

class Tutor(ClientAvatar):
    def __init__(self, avId, server):
        ClientAvatar.__init__(self, avId, server)
        self.questionId = None
        self.paPupil = None
        self._searchSubjects()

    def setMyWBColor(self):
        self.remote.callRemote("wbMyColor", TUTOR_COLOR)

    def _searchSubjects(self):
        query = """select name from tutor_subject as t, subject as s
            where t.fk_subject = s.id and t.fk_tutor=%d"""
        d = self.db.db.runQuery(query, (int(self.avId),))
        d.addCallback(self._loadSubjects)

    def perspective_whoami(self):
        return TUTOR

    def perspective_requestRoom(self):
        if self.avId not in self.server.shouldBeOpenPARooms() and self.selectedSubject == None:
            self.remote.callRemote("wbShowSubjects")
            self.server.notifyClient(self.avId, "Elegir al menos una materia")
            return
        if self.questionId == None:
            self.server.requestRoom(self.avId)
        else:
            self.server.notifyClient(self.avId, "Respondiendo pregunta offline")

    def perspective_removeRoom(self):
        self.server.removeRoom(self.avId)

    def perspective_rejectClient(self):
        if self.avId not in self.server.wbRooms.keys():
            return
        clientId = self.server.wbRooms[self.roomId].roomPupilWaiting()
        if clientId != None:
            self.server.exitViewers(self.roomId)
            self.server.wbRooms[self.roomId].roomPupilReject()
            self.cleanWhiteBoard()
#            self.server.wbQueues.enterQueueFirst(GENERAL, clientId)
#            self.server.wbClients[clientId].waitingInQueue = GENERAL
            self.server.wbClients[clientId].unlockWhiteBoard()
            self.server.wbClients[clientId].waitingInRoom = None
            self.server.setClientWindow(clientId, OUT)
            self.server.notifyClient(clientId, "El tutor te rechazo")
            self.server.manageNextPupil(self.roomId, self.server.sessions.tutorReject)

    def perspective_acceptClient(self):
        if self.avId not in self.server.wbRooms.keys():
            return
        clientId = self.server.wbRooms[self.roomId].roomPupilWaiting()
        if  clientId == None:
            return
        avClient = self.server.wbClients[clientId]
        avClient.waitingInRoom = None
        avClient.roomId = self.roomId
        avClient.lastMinute = now().minute
        for client in self.server.wbRooms[self.roomId].roomListClients():
            avatar = self.server.wbClients[client]
            avatar.cleanWhiteBoard()
            self.server.clientUpdate(avatar, avClient)
        self.server.wbRooms[self.avId].roomPupilAccept()
        #cierro sesion de espera y abro de clase con clientId
        self.server.wbClients[clientId].unlockWhiteBoard()
        self.server.sessions.pupilEnter(self.avId, clientId)
        self.server.setClientWindow(self.avId, IN_CLASS)
        self.server.setClientWindow(clientId, IN_CLASS)

    def perspective_quitClient(self):
        if self.avId not in self.server.wbRooms.keys():
            return
        #si no hay a quien echar
        clientId = self.server.wbRooms[self.roomId].roomPupilCurrent()
        if clientId == None:
            return
        self.saveClassStatus()
        self.server.exitViewers(self.roomId)
        self.server.wbRooms[self.roomId].roomPupilExit(clientId)
        avClient = self.server.wbClients[clientId]
        avClient.roomId = None
        discount = (now().minute - avClient.lastMinute) % 60
        avClient.discountIA(discount)
        avClient.lastMinute = None
        avClient.cleanWhiteBoard()
        # Vaciamos la pizarra del tutor también
        self.cleanWhiteBoard()
        #tutor cierra sesion de clase; se abre sesion de espera
        self.server.setClientWindow(clientId, OUT)
        self.server.notifyClient(clientId, "El tutor cerro")
        self.server.manageNextPupil(self.roomId, self.server.sessions.tutorEnd)

    def loadPAClass(self):
        pa_query = """select fk_pupil, fk_subject from prearranged_classes
            where (time_start <= '%s' and time_end >= '%s') and fk_tutor = %d
            """
        date = now()
        d = self.db.db.runQuery(pa_query, (date, date, int(self.avId)))
        d.addCallback(self._loadPupilAndSubject)

    def _loadPupilAndSubject(self, res):
        self.paPupil = str(res[0][0])
        self.perspective_setSubjects([res[0][1]])

    def saveClassStatus(self):
        sessionId = self.server.sessions.sessionKey(self.avId)
        status = self.server.wbClientStatus[self.avId].pickle()
        d = self.server.askStringClient(self.avId, "Fin de clase", "Comentario")
        d.addCallback(self._archiveClass, sessionId, status)
        d.addErrback(lambda a: self.server.notifyClient(self.avId, "Error al guardar clase"))
        return d

    def _archiveClass(self, comment, sessionId, status):
        if comment != None:
            d = self._prearchive(comment, sessionId, status)
        else:
            d = self._prearchive("", sessionId, status)
        return d

    def _prearchive(self, comment, sessionId, status):
        if comment != None:
            answer = comment.decode("utf-8")
            query = """insert into pre_archive (fk_session, status, comment)
                values (%d, %s, %s)
                """
            status = QuotedString(status)
            d = self.db.db.runOperation(query, (sessionId, status, comment))
            d.addCallback(lambda a: True)
        else:
            d = defer.maybeDeferred(lambda: False)
        return d

    #########################################
    # Comun PostProcesado / Offline Questions
    #########################################
    def perspective_rejectQuestion(self):
        if self.questionId != None:
            self.server.sessions.tutorQuit(self.avId)
            self.cleanWhiteBoard()
            self.server.setClientWindow(self.avId, OUT)
            self.questionId = None

    def _questionList(self, res):
        questions = {}
        for row in res:
            questions[row[0]] = row[1:]
        return questions

    def _checkTutorOut(self):
        if self.questionId != None:
            self.server.notifyClient(self.avId, "Respondiendo pregunta offline")
            return False
        if self.avId in self.server.wbRooms.keys():
            self.server.notifyClient(self.avId, "Tiene un aula abierta")
            return False
        if self.avId in self.server.wbRoomRequests:
            self.server.notifyClient(self.avId, "Tiene un aula solicitada")
            return False
        if self.avId in self.server.shouldBeOpenRooms():
            self.server.notifyClient(self.avId, "Tiene horario de clases asignado ahora")
            return False
        return True

    ################
    # Post Procesado
    ################
    def perspective_acceptPost(self, idQ):
        if self._checkTutorOut():
            query = """select status from pre_archive
                where id = %s"""
            d = self.db.db.runQuery(query, (idQ,))
            d.addCallback(self._loadPost, idQ)
            d.addCallback(self._initPostSession)

    def perspective_postProcess(self):
        if self.questionId != None:
            d = self._getPreInfo(self.questionId)
            d.addCallback(self._savePost)

    def perspective_getPost(self):
        query = """select p.id, p.comment
            from pre_archive as p
            """
        d = self.db.db.runQuery(query)
        d.addCallback(self._questionList)
        return d

    def _getPreInfo(self, idQ):
        pre_query = """select fk_session, comment from pre_archive where id = %d"""
        d = self.db.db.runQuery(pre_query, (idQ,))
        return d

    def _loadPost(self, questionRes, idQ):
        if len(questionRes) > 0:
            question = questionRes[0][0]
            status = WBStatus()
            status.unpickle(question)
            self.cleanWhiteBoard()
            self.server.clientUpdateFromStatusModif(self, status)
            self.questionId = idQ
            return True
        return False

    def _initPostSession(self, success):
        if success:
            self.server.sessions.newPostProcessSession(self.avId)
            self.server.setClientWindow(self.avId, IN_POST_PROCESS)

    def _savePost(self, res):
            sessionId = res[0][0]
            comment = res[0][1]
            idQ = self.questionId
            d = self.server.askStringClient(self.avId, "Postprocesado", "Comentario", comment)
            d.addCallback(self._postArchive, sessionId)
            d.addCallback(self._notifyPostArchive)
            d.addCallback(self._deletePost, idQ)
            d.addErrback(lambda a: self.server.notifyClient(self.avId, "Error al guardar respuesta"))

    def _postArchive(self, comment, sessionId):
        if comment != None:
            filename = str(sessionId)
            answer = comment.decode("utf-8")
            query = """insert into archive (filename, fk_session, comment)
                values (%s, %s, %s)
                """
            self._psWhiteBoard(filename)
            d = self.db.db.runOperation(query, (filename + ARCHIVE_EXT, sessionId, comment))
            d.addCallback(lambda a: True)
        else:
            d = defer.maybeDeferred(lambda: False)
        return d

    def _psWhiteBoard(self, filename):
        self.cleanExtraWhiteBoard()
        d = self.server.wbClients[self.avId].remote.callRemote("wbPSWhiteBoard")
        d.addCallback(self._writePS, filename)
        return d

    def _writePS(self, ps, filename):
        ps_archive = ARCHIVE_DIR + filename + ".ps"
        f = open(ps_archive, "w")
        f.write(ps)
        f.close()
        os.system(PS_TO_EXT + PS_OPTIONS + PS_INFILE + ps_archive + PS_OUTFILE + ARCHIVE_DIR + filename + ARCHIVE_EXT)

    def _notifyPostArchive(self, confirm):
        if confirm:
            self.server.sessions.tutorEnd(self.avId, OUT)
            self.server.notifyClient(self.avId, "Respuesta guardada")
            self.cleanWhiteBoard()
            self.server.setClientWindow(self.avId, OUT)
            self.questionId = None
        else:
            self.server.notifyClient(self.avId, "Respuesta no guardada")
        return confirm

    def _deletePost(self, confirm, questionId):
        if confirm:
            del_query = """delete from pre_archive where id = %d"""
            d = self.db.db.runOperation(del_query, (questionId,))

    ##################
    #Offline Questions
    ##################
    def perspective_answerOfflineQuestion(self):
        if self.questionId != None:
            idQ = self.questionId
            sessionId = self.server.sessions.sessionKey(self.avId)
            status = self.server.wbClientStatus[self.avId].pickle()
            d = self.server.askStringClient(self.avId, "Pregunta offline", "Comentario")
            d.addCallback(self._prearchive, sessionId, status)
            d.addCallback(self._notifyArchiveQuestion)
            d.addCallback(self._deleteAnsweredQuestion, idQ)
            d.addErrback(lambda a: self.server.notifyClient(self.avId, "Error al guardar respuesta"))

    def perspective_acceptOfflineQuestion(self, idQ):
        if self._checkTutorOut():
            query = """select status, fk_pupil from offline_questions
                where id = %s"""
            d = self.db.db.runQuery(query, (idQ,))
            d.addCallback(self._loadOfflineQuestion, idQ)
            d.addCallback(self._initOfflineSession)

    def perspective_getOfflineQuestions(self):
        query = """select q.id, p.first_name, p.last_name, s.name
            from offline_questions as q, person as p, subject as s
            where q.fk_pupil = p.id and q.fk_subject = s.id
            """
        d = self.db.db.runQuery(query)
        d.addCallback(self._questionList)
        return d

    def _loadOfflineQuestion(self, questionRes, idQ):
        if len(questionRes) > 0:
            question = questionRes[0][0]
            pupilId = questionRes[0][1]
            status = WBStatus()
            status.unpickle(question)
            self.cleanWhiteBoard()
            self.server.clientUpdateFromStatus(self, status)
            self.questionId = idQ
            return pupilId
        return None

    def _initOfflineSession(self, pupilId):
        if pupilId != None:
            self.server.sessions.newOfflineSession(self.avId, pupilId)
            self.server.setClientWindow(self.avId, IN_ANSWERING)

    def _notifyArchiveQuestion(self, confirm):
        if confirm:
            self.server.sessions.tutorEnd(self.avId, OUT)
            self.server.notifyClient(self.avId, "Respuesta guardada")
            self.cleanWhiteBoard()
            self.server.setClientWindow(self.avId, OUT)
            self.questionId = None
        else:
            self.server.notifyClient(self.avId, "Respuesta no guardada")
        return confirm

    def _deleteAnsweredQuestion(self, confirm, questionId):
        if confirm:
            del_query = """delete from offline_questions where id = %d"""
            d = self.db.db.runOperation(del_query, (questionId,))
