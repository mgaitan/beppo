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

class Client:
    def __init__(self, master, selectionGet):
        self.swb = ScrolledWB(1120,6000) # Tamaño del board.
        self.swb.wb.client = self
        self.cc = ClientConnection(master, self.swb.wb)
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
        def1 = self.root.callRemote("copyItems", items)
        def1.addErrback(self.check_everything, "Error in broadcast_copyItems")
        return def1

    def broadcast_paste(self):
        def1 = self.root.callRemote("paste")
        def1.addErrback(self.check_everything, "Error in broadcast_paste")
        return def1

    def broadcast_addItem(self, itemId, kind, points, outline, fill, width):
        def1 = self.root.callRemote("addItem", itemId, kind, points, outline, fill, width)
        def1.addErrback(self.check_everything, "Error in broadcast_addItem")
        return def1

    def broadcast_moveItems(self, items, dx, dy):
        def1 = self.root.callRemote("moveItems", items, dx, dy)
        def1.addErrback(self.check_everything, "Error in broadcast_moveItems")
        return def1

    def broadcast_eraseItem(self, items):
        def1 = self.root.callRemote("eraseItem", items)
        def1.addErrback(self.check_everything, "Error in broadcast_eraseItem")
        return def1

    def broadcast_fillItem(self, item, color):
        def1 = self.root.callRemote("fillItem", item, color)
        def1.addErrback(self.check_everything, "Error in broadcast_fillItem")
        return def1

    def broadcast_addTextBox(self, textbox, points, color):
        def1 = self.root.callRemote("addTextBox", textbox, points, color)
        def1.addErrback(self.check_everything, "Error in broadcast_addTextBox")
        return def1

    def broadcast_insertChars(self, textbox, index, string):
        string = string.encode('utf-8')
        def1 = self.root.callRemote("insertChars", textbox, index, string)
        def1.addErrback(self.check_everything, "Error in broadcast_insertChars")
        return def1
    
    def broadcast_deleteChars(self, textbox, startIndex, endIndex):
        def1 = self.root.callRemote("deleteChars", textbox, startIndex, endIndex)
        def1.addErrback(self.check_everything, "Error in broadcast_deleteChars")
        return def1

    def check_everything(self, failure, msg):
        print msg
        log.err(failure)
        return None
