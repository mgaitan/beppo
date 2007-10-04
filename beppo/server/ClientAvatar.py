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

class ClientAvatar(pb.Avatar):
    def __init__(self, avId, server):
        self.avId = str(avId)
        self.server = server
        self.db = DBConnect()
        self.roomId = None
        self.selectedSubject = None
        self.mySubjects = {}
        self.name = None


    def attached(self, mind):
        """Toma nota de una referencia al clientConnection actual"""
        self.remote = mind

    def detached(self, mind):
        """Toma nota de que no hay ninguna conexion actual al cliente"""
        self.remote = None

    def setMyWBColor(self):
        raise NotImplementedError

    def perspective_whoami(self):
        raise NotImplementedError

    def _loadSubjects(self, subjects):
        self.selectedSubject = None
        for row in subjects:
            self.mySubjects[row[0]] = False

    def getSelectedSubjects(self):
        ret = []
        for s in self.mySubjects.keys():
            if self.mySubjects[s]:
                ret.append(s)
        return ret

    def getSubjects(self):
        return self.mySubjects

    def perspective_getSubjects(self):
        return self.getSubjects()

    def perspective_setSubjects(self, subjects):
        self.selectedSubject = None
        for s in self.mySubjects:
            if s in subjects:
                self.mySubjects[s] = True
                self.selectedSubject = s
            else:
                self.mySubjects[s] = False

    def getName(self, nombre):
        self.name = nombre
        return nombre

    def perspective_myName(self):
        if self.name==None:
            d = self._searchClientName()
            d.addCallback(lambda res: res[0][0])
            d.addCallback(lambda x: self.getName(x))
            
        else:
            d = defer.Deferred()
            d.addCallback(lambda: self.name) 
        return d

    def _searchClientName(self):
        query = """select username from person where id = %d"""
        d = self.db.db.runQuery(query, (int(self.avId),))
        return d

    def perspective_getWbServer(self):
        return self.server

    def perspective_getRooms(self):
        return self.server.wbQueues.getTutorQueuesInfo()

    def perspective_getRoomInfo(self, room):
        d = self.server.roomInfo(room)
        return d

    def cleanExtraWhiteBoard(self):
        self.remote.callRemote("wbCleanExtraWhiteBoard")

    def cleanWhiteBoard(self):
        self.hasQuestion = False
        self.server.wbClientStatus[self.avId].statusReset()
        self.remote.callRemote("wbCleanWhiteBoard")

    def lockWhiteBoard(self):
        self.remote.callRemote("wbLockWhiteBoard")

    def unlockWhiteBoard(self):
        self.remote.callRemote("wbUnlockWhiteBoard")
