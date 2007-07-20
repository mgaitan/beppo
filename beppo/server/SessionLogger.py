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

from time import localtime, strftime
from DBConnect import DBConnect

class SessionLogger:
    def __init__(self):
        self.db = DBConnect()
        self.sessionId = {}

    def sessionKey(self, tutorId):
        return self.sessionId[tutorId]

    def openSession(self, tutorId, status, pupilId="NULL"):
        if tutorId not in self.sessionId.keys():
            d = self._nextId()
            d.addCallback(self._createSession, tutorId, status, pupilId)
        return d

    def closeSession(self, tutorId, code=1):
        d = self.db.db.runOperation("update session set time_end = %s, error_code = %d where id = %d", (self._currentTimestamp(), code, self.sessionId[tutorId]))
        del(self.sessionId[tutorId])
        return d

    def closeAllSessions(self, code=7):
        d = self.db.db.runOperation("update session set time_end = %s, error_code = %d where time_end is null", (self._currentTimestamp(), code))
        return d

    def hasOpenSession(self, tutorId):
        return (tutorId in self.sessionId.keys())

    def _nextId(self):
        d = self.db.db.runQuery("select nextval('session_id_seq')")
        return d

    def _createSession(self, resId, tutorId, status, pupilId):
        self.sessionId[tutorId] = resId[0][0]
        if pupilId == "NULL":
            self.db.db.runOperation("insert into session(id, fk_tutor, session_type, time_start) values(%d, %d, %d, %s)", (self.sessionId[tutorId], int(tutorId), status, self._currentTimestamp()))
        else:
            self.db.db.runOperation("insert into session(id, fk_tutor, fk_pupil, session_type, time_start) values(%d, %d, %d, %d, %s)", (self.sessionId[tutorId], int(tutorId), int(pupilId), status, self._currentTimestamp()))

    def _currentTimestamp(self):
        date = strftime("%Y-%m-%d %H:%M:%S")
        return date
