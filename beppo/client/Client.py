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

from ClientConnection import ClientConnection
from ScrolledWB import ScrolledWB
from twisted.spread import pb
from twisted.python import log
from twisted.internet import defer

class Client:
    def __init__(self, master, selectionGet):
        self.swb = ScrolledWB(1120,6000, self) # Tamaño del board.
        #self.swb.wb.client = self
        self.cc = ClientConnection(master, self.swb)
        self.root = None
        self.name = None
        self.selectionGet = selectionGet

    def setName(self, name):
        self.name = name

    def setRoot(self, root):
        self.root = root

    def setAvatar(self, avatar):
        self.avatar = avatar
        self.cc.avatar = avatar

    def pack(self):
        self.swb.pack()

    def getSystemClipboard(self):
        try:
            ret = self.selectionGet(selection="CLIPBOARD")
        except:
            ret = ""
        return ret

    def showSubjects(self):
        self.cc.subjectAdminCreate(self.avatar)

    def showPost(self):
        self.cc.postAdminCreate(self.avatar)

    def showQuestions(self):
        self.cc.questionAdminCreate(self.avatar)

    def showRooms(self):
        self.cc.roomAdminCreate(self.avatar)

    def disconnect(self):
        return self.root.callRemote("removeClient")

    def broadcast_copyItems(self, items):
        deferred = self.root.callRemote("copyItems", items)
        deferred.addErrback(self.check_everything, "Error in broadcast_copyItems")
        return deferred

    def broadcast_paste(self):
        deferred = self.root.callRemote("paste")
        deferred.addErrback(self.check_everything, "Error in broadcast_paste")
        return deferred

    def broadcast_addItem(self, itemId, kind, points, outline, fill, width, graph=None):
        deferred = self.root.callRemote("addItem", itemId, kind, points, outline, fill, width, graph=graph)
        deferred.addErrback(self.check_everything, "Error in broadcast_addItem")
        return deferred

    def broadcast_moveItems(self, items, dx, dy):
        deferred = self.root.callRemote("moveItems", items, dx, dy)
        deferred.addErrback(self.check_everything, "Error in broadcast_moveItems")
        return deferred

    def broadcast_eraseItem(self, items):
        deferred = self.root.callRemote("eraseItem", items)
        deferred.addErrback(self.check_everything, "Error in broadcast_eraseItem")
        return deferred

    def broadcast_fillItem(self, item, color):
        deferred = self.root.callRemote("fillItem", item, color)
        deferred.addErrback(self.check_everything, "Error in broadcast_fillItem")
        return deferred

    def broadcast_addTextBox(self, textbox, points, color):
        if self.root is None:
            return defer.succeed(None)
        deferred = self.root.callRemote("addTextBox", textbox, points, color)
        deferred.addErrback(self.check_everything, "Error in broadcast_addTextBox")
        return deferred

    def broadcast_insertChars(self, textbox, index, string):
        string = string.encode('utf-8')
        deferred = self.root.callRemote("insertChars", textbox, index, string)
        deferred.addErrback(self.check_everything, "Error in broadcast_insertChars")
        return deferred

    def broadcast_deleteChars(self, textbox, startIndex, endIndex):
        deferred = self.root.callRemote("deleteChars", textbox, startIndex, endIndex)
        deferred.addErrback(self.check_everything, "Error in broadcast_deleteChars")
        return deferred
    
    def broadcast_sendMsg(self, string):
        string = string.encode('utf-8')
        deferred = self.root.callRemote("sendMsg", string)
        deferred.addErrback(self.check_everything, "Error in broadcast_sendMsg")
        return deferred

    def check_everything(self, failure, msg):
        print msg
        log.err(failure)
        return None
