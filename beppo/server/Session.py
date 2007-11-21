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

from SessionLogger import SessionLogger
from beppo.Constants import TUTOR, PUPIL, IACLASS, PACLASS, WAITING, ABSENT, EXTRA_WAITING, EXTRA_IACLASS, DECIDING
from beppo.Constants import TUTOR_ENTER, TUTOR_END, NORMAL, TUTOR_QUIT, PUPIL_ENTER, PUPIL_END, GENERAL
from beppo.Constants import OFFLINE_QUESTION, QUESTION_ANSWERED, QUESTION_NOT_ANSWERED, ACCEPTED, REJECTED
from beppo.Constants import POST_PROCESS, CORRECTED, NOT_CORRECTED

class Session:
    def __init__(self, server, logger, roomId):
        self.server = server
        self.logger = logger
        self.roomId = roomId

    def sessionKey(self):
        key = None
        if self.logger.hasOpenSession(self.roomId):
            key = self.logger.sessionKey(self.roomId)
        return key

    def newSession(self, status):
        raise NotImplementedError

    def closeSession(self):
        raise NotImplementedError

    def tutorDecide(self, pupilId):
        raise NotImplementedError

    def tutorEnter(self, status, pupilId):
        raise NotImplementedError

    def tutorReject(self, status, pupilId):
        raise NotImplementedError

    def tutorEnd(self, status, pupilId):
        raise NotImplementedError

    def tutorQuit(self):
        raise NotImplementedError

    def pupilEnter(self, pupilId):
        raise NotImplementedError

    def pupilEnd(self, status, pupilId):
        raise NotImplementedError
        
class ExtraSession(Session):
    def __init__(self, server, logger, roomId, kind):
        Session.__init__(self, server, logger, roomId)
        self.kind = kind

    def newSession(self, status=EXTRA_WAITING, pupilId="NULL"):
        if status == WAITING:
            status = EXTRA_WAITING
        self.logger.openSession(self.roomId, status, pupilId)

    def closeSession(self):
        self.logger.closeSession(self.roomId, NORMAL)

    def tutorDecide(self, pupilId):
        self.logger.closeSession(self.roomId, PUPIL_ENTER)
        self.logger.openSession(self.roomId, DECIDING, pupilId)

    def tutorEnter(self, pupilId):
        pass

    def tutorReject(self, status, pupilId):
        self.logger.closeSession(self.roomId, REJECTED)
        if status == WAITING:
            status = EXTRA_WAITING
        self.logger.openSession(self.roomId, status, pupilId)

    def tutorEnd(self, status, pupilId):
        self.logger.closeSession(self.roomId, TUTOR_END)
        if status == WAITING:
            status = EXTRA_WAITING
        self.logger.openSession(self.roomId, status, pupilId)
        return False

    def tutorQuit(self):
        self.server.closeRoomQueue(self.roomId)
        self.logger.closeSession(self.roomId, NORMAL)
        return True

    def pupilEnter(self, pupilId):
        self.logger.closeSession(self.roomId, ACCEPTED)
        self.logger.openSession(self.roomId, EXTRA_IACLASS, pupilId)

    def pupilEnd(self, status, pupilId):
        self.logger.closeSession(self.roomId, PUPIL_END)
        if status == WAITING:
            status = EXTRA_WAITING
        self.logger.openSession(self.roomId, status, pupilId)
        return False

class OfflineQuestionSession(Session):
    def __init__(self, server, logger, roomId, kind):
        Session.__init__(self, server, logger, roomId)
        self.kind = kind

    def newSession(self, status=OFFLINE_QUESTION, pupilId="NULL"):
        self.logger.openSession(self.roomId, status, pupilId)

    def closeSession(self):
        self.logger.closeSession(self.roomId, QUESTION_NOT_ANSWERED)

    def tutorEnd(self, status, pupilId):
        self.logger.closeSession(self.roomId, QUESTION_ANSWERED)
        return True

    def tutorQuit(self):
        self.logger.closeSession(self.roomId, QUESTION_NOT_ANSWERED)
        return True

class PostProcessSession(Session):
    def __init__(self, server, logger, roomId, kind):
        Session.__init__(self, server, logger, roomId)
        self.kind = kind

    def newSession(self, status=POST_PROCESS, pupilId="NULL"):
        self.logger.openSession(self.roomId, status, pupilId)

    def closeSession(self):
        self.logger.closeSession(self.roomId, NOT_CORRECTED)

    def tutorEnd(self, status, pupilId):
        self.logger.closeSession(self.roomId, CORRECTED)
        return True

    def tutorQuit(self):
        self.logger.closeSession(self.roomId, NOT_CORRECTED)
        return True

class IAPASession(Session):
    def __init__(self, server, logger, roomId, kind):
        Session.__init__(self, server, logger, roomId)
        self.kind = kind

    def newSession(self, status=WAITING, pupilId="NULL"):
        self.logger.openSession(self.roomId, status, pupilId)

    def closeSession(self):
        self.logger.closeSession(self.roomId, NORMAL)

    def tutorDecide(self, pupilId):
        self.logger.closeSession(self.roomId, PUPIL_ENTER)
        self.logger.openSession(self.roomId, DECIDING, pupilId)

    def tutorEnter(self, status, pupilId):
        self.logger.closeSession(self.roomId, TUTOR_ENTER)
        self.logger.openSession(self.roomId, status, pupilId)

    def tutorReject(self, status, pupilId):
        self.logger.closeSession(self.roomId, REJECTED)
        self.logger.openSession(self.roomId, status, pupilId)

    def tutorEnd(self, status, pupilId):
        if self.server.wbRooms[self.roomId].roomIsClosed():
            self.server.removeRoom(self.roomId)
            return True
        else:
            self.logger.closeSession(self.roomId, TUTOR_END)
            self.logger.openSession(self.roomId, status, pupilId)
            return False

    def tutorQuit(self):
        if self.server.wbRooms[self.roomId].roomIsClosed():
            self.logger.closeSession(self.roomId, NORMAL)
            return True
        else:
            self.server.closeRoomQueue(self.roomId)
            self.logger.closeSession(self.roomId, TUTOR_QUIT)
            self.logger.openSession(self.roomId, ABSENT)
            return False

    def pupilEnter(self, pupilId):
        self.logger.closeSession(self.roomId, ACCEPTED)
        self.logger.openSession(self.roomId, self.kind, pupilId)

    def pupilEnd(self, status, pupilId):
        if self.server.wbRooms[self.roomId].roomIsClosed():
            self.server.removeRoom(self.roomId)
            return True
        else:
            self.logger.closeSession(self.roomId, PUPIL_END)
            self.logger.openSession(self.roomId, status, pupilId)
            return False

class SessionAdmin:
    def __init__(self, server):
        self.sessionLogger = SessionLogger()
        self.server = server
        self.openSessions = {}
    
    def closeAll(self, error):
        self.sessionLogger.closeAllSessions(error)

    def newPostProcessSession(self, tutorId):
        session = PostProcessSession(self.server, self.sessionLogger, tutorId, POST_PROCESS)
        self.openSessions[tutorId] = session
        session.newSession()

    def newOfflineSession(self, tutorId, pupilId):
        session = OfflineQuestionSession(self.server, self.sessionLogger, tutorId, OFFLINE_QUESTION)
        self.openSessions[tutorId] = session
        session.newSession(OFFLINE_QUESTION, pupilId)
    
    def newSession(self, roomId, kind, status, pupilId="NULL"):
        if kind == EXTRA_IACLASS:
            session = ExtraSession(self.server, self.sessionLogger, roomId, kind)
        else:
            session = IAPASession(self.server, self.sessionLogger, roomId, kind)
        self.openSessions[roomId] = session
        session.newSession(status, pupilId)
        
    def closeSession(self, roomId):
        session = self.openSessions[roomId]
        session.closeSession()
        del(self.openSessions[roomId])

    def hasOpenSession(self, roomId):
        return (roomId in self.openSessions.keys())

    def tutorDecide(self, roomId, status=DECIDING, pupilId="NULL"):
        session = self.openSessions[roomId]
        session.tutorDecide(pupilId)

    def tutorEnter(self, roomId, status, pupilId="NULL"):
        session = self.openSessions[roomId]
        session.tutorEnter(status, pupilId)

    def tutorReject(self, roomId, status, pupilId="NULL"):
        session = self.openSessions[roomId]
        session.tutorReject(status, pupilId)

    def tutorEnd(self, roomId, status, pupilId="NULL"):
        session = self.openSessions[roomId]
        if session.tutorEnd(status, pupilId):
            del(self.openSessions[roomId])

    def tutorQuit(self, roomId):
        session = self.openSessions[roomId]
        if session.tutorQuit():
            del(self.openSessions[roomId])

    def pupilEnter(self, roomId, pupilId):
        session = self.openSessions[roomId]
        session.pupilEnter(pupilId)

    def pupilEnd(self, roomId, status, pupilId="NULL"):
        session = self.openSessions[roomId]
        if session.pupilEnd(status, pupilId):
            del(self.openSessions[roomId])

    def changeSessionKind(self, roomId, kind, pupilId=None):
        self.closeSession(roomId)
        if pupilId != None:
            self.newSession(roomId, kind, IACLASS, pupilId)
        else:
            self.newSession(roomId, kind, WAITING)

    def sessionKey(self, roomId):
	print self.openSessions
        try:
		session = self.openSessions[roomId]
		return session.sessionKey()
	except KeyError:
		return None
