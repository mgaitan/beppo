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
from Queuer import Queuer
#from Strings import _
from beppo.Constants import GENERAL

class WBQueuer(Queuer):
    def __init__(self, clientList):
        Queuer.__init__(self)
        self.db = DBConnect()
        self.clients = clientList

    def addQueue(self, roomId):
        Queuer.addQueue(self, roomId)
        query = "select id, first_name, last_name from person where id = %s"
        d = self.db.db.runQuery(query, (roomId,))
        d.addCallback(lambda res: res[0][1] + " " + res[0][2])
        d.addCallback(self._broadcastNewQueue, roomId)

    def _broadcastNewQueue(self, queueName, queueId):
        for clientId in self.clients.keys():
            try:
                d = self.clients[clientId].remote.callRemote("addQueueDialog", queueId, queueName)
            except (pb.DeadReferenceError):
                pass

    def removeQueue(self, roomId):
        assert(roomId in self.queue.keys())
        Queuer.removeQueue(self, roomId)
        d = self._broadcastRemoveQueue(roomId)

    def _broadcastRemoveQueue(self, queueId):
        for clientId in self.clients.keys():
            try:
                d = self.clients[clientId].remote.callRemote("removeQueueDialog", queueId)
            except (pb.DeadReferenceError):
                pass

    def enterQueueFirst(self, roomId, clientId):
        Queuer.enterQueueFirst(self, roomId, clientId)
        d = self._broadcastUpdateQueue(roomId)

    def enterQueue(self, roomId, clientId):
        Queuer.enterQueue(self, roomId, clientId)
        d = self._broadcastUpdateQueue(roomId)

    def _broadcastUpdateQueue(self, queueId):
        for clientId in self.clients.keys():
            try:
                lenQueue = self.lenQueue(queueId)
                d = self.clients[clientId].remote.callRemote("updateQueueDialog", queueId, lenQueue)
            except (pb.DeadReferenceError):
                pass

    def popQueue(self, roomId):
        first = Queuer.popQueue(self, roomId)
        d = self._broadcastUpdateQueue(roomId)
        return first

    def leaveQueue(self, roomId, clientId):
        Queuer.leaveQueue(self, roomId, clientId)
        d = self._broadcastUpdateQueue(roomId)

    def getTutorQueuesInfo(self):
        tutors = [t for t in  self.roomList() if t != GENERAL]
        d = self._getTutorNames(tutors)
        d.addCallback(self._buildQueueList)
        return d

    def _getTutorNames(self, tutors):
        if len(tutors) > 0:
            roomIds = tuple(tutors + [0])
            query = "select id, first_name, last_name from person where id in %s"
            d = self.db.db.runQuery(query, (roomIds,))
        else:
            d = defer.maybeDeferred(lambda: [])
        return d

    def _buildQueueList(self, queueInfo):
        queues = {}
        lenQueue = self.lenQueue(GENERAL)
        queues[GENERAL] = ("Cola General", lenQueue)
        for row in queueInfo:
            queueId = str(row[0])
            lenQueue = self.lenQueue(queueId)
            nameQueue = row[1] + " " + row[2]
            queues[queueId] = (nameQueue, lenQueue)
        return queues

    def queueInfo(self, roomId):
        if roomId != GENERAL:
            d = self._getQueueInfo(roomId)
        else:
            d = defer.maybeDeferred(lambda: ("Cola general", GENERAL))
        return d

    def _getQueueInfo(self, roomId):
        query = "select id, first_name, last_name from person where id = %s"
        d = self.db.db.runQuery(query, (roomId,))
        return d

    def nextClient(self, roomId):
        next = None
        if self.lenQueue(roomId) > 0:
            next = self.popQueue(roomId)
        else:
            gen = self.clientsWaiting(GENERAL)
            for c in gen:
                if self.clients[c].getSubject() in self.clients[roomId].getSelectedSubjects():
                    self.leaveQueue(GENERAL, c)
                    return c
        return next
