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

from beppo.Constants import GENERAL

class Queuer:
    def __init__(self):
        self.queue = {GENERAL:[]}

    def isEmpty(self, roomId):
        if len(self.queue[roomId]) == 0:
            return True
        else:
            return False

    def addQueue(self, roomId):
        assert(roomId not in self.queue.keys())
        self.queue[roomId] = []

    def removeQueue(self, roomId):
        assert(roomId in self.queue.keys())
        del(self.queue[roomId])

    def enterQueueFirst(self, roomId, clientId):
        self.queue[roomId].insert(0, clientId)

    def enterQueue(self, roomId, clientId):
        self.queue[roomId].append(clientId)

    def lenQueue(self, roomId):
        return len(self.queue[roomId])

    def popQueue(self, roomId):
        return self.queue[roomId].pop(0)

    def leaveQueue(self, roomId, clientId):
        self.queue[roomId].remove(clientId)

    def firstInQueue(self, roomId):
        return self.queue[roomId][0]

    def isClientInQueue(self, roomId, clientId):
        if clientId in self.queue[roomId]:
            return True
        else:
            return False

    def clientsWaiting(self, roomId):
        return self.queue[roomId]

    def roomList(self):
        return self.queue.keys()

    def getListQueues(self):
        ret = {}
        for key in self.queue.keys():
            ret[key] = self.lenQueue(key)
        return ret

    def nextClient(self, roomId):
        next = None
        if self.lenQueue(roomId) > 0:
            next = self.popQueue(roomId)
        elif self.lenQueue(GENERAL) > 0:
            next = self.popQueue(GENERAL)
        return next

    def whoIsNext(self, roomId):
        next = None
        if self.lenQueue(roomId) > 0:
            next = self.firstInQueue(roomId)
        elif self.lenQueue(GENERAL) > 0:
            next = self.firstInQueue(GENERAL)
        return next


