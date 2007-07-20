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
from RoomAdmin import RoomAdmin
from WBPost import PostAdmin
from WBQuestions import QuestionAdmin
from WBSubjects import SubjectAdmin
import tkMessageBox
import tkSimpleDialog
from beppo.Strings import _

class ClientConnection(pb.Referenceable):

    def __init__(self, master, wb):
        self.wb = wb
        self.master = master
        self.roomAdmin = None
        self.postAdmin = None
        self.questionAdmin = None
        self.subjectAdmin = None

    def remote_wbPing(self):
        pass

    def remote_wbAddItem(self, tagId, kind, points, outline, fill, width):
        self.wb.addItem(kind, points, outline, fill, width, foreignId=tagId)

    def remote_wbMoveItems(self, tagId, selection, dx, dy):
        self.wb.moveItems(selection, dx, dy, foreignId=tagId)

    def remote_wbEraseItem(self, tagId, selection):
        self.wb.eraseSelectedItems(selection, foreignId=tagId)

    def remote_wbFillItem(self, tagId, color):
        self.wb.fillItem(tagId, color, foreignId=tagId)

    def remote_wbAddTextBoxFull(self, tagId, points, text, color):
        self.wb.addTextBoxFull(points, text, color, foreignId=tagId)

    def remote_wbAddTextBox(self, tagId, points, color):
        self.wb.addTextBox(points, color, foreignId=tagId)

    def remote_wbInsertChars(self, tagId, index, string):
        string = string.decode("utf-8")
        self.wb.insertChars(None, index, string, foreignId=tagId)
    
    def remote_wbDeleteChars(self, tagId, startIndex, endIndex):
        self.wb.deleteChars(None, startIndex, endIndex, foreignId=tagId)

    def remote_wbPSWhiteBoard(self):
        self.wb.clearSelection()
        ps = self.wb.postscript(x=0, y=0, width=1120, height=6000)
        return ps

    def remote_wbCleanExtraWhiteBoard(self):
        self.wb.cleanExtra()

    def remote_wbCleanWhiteBoard(self):
        self.wb.reset()

    def remote_serverClientWindow(self, desc):
        self.master.setWindowStatus(desc)
        if self.postAdmin != None:
            self.postAdmin.dialog.changeTo(desc)
        if self.questionAdmin != None:
            self.questionAdmin.dialog.changeTo(desc)
        if self.roomAdmin != None:
            self.roomAdmin.dialog.changeTo(desc)

    def remote_serverMessage(self, msg):
        tkMessageBox.showinfo(_("Informacion"), _(msg))

    def remote_serverQuestion(self, title, question):
        answer = tkMessageBox.askyesno(_(title), _(question))
        return answer

    def remote_serverStringQuestion(self, title, question, initial):
        string = tkSimpleDialog.askstring(_(title), _(question), initialvalue=initial)
        if string != None:
            answer = string.encode("utf-8")
        else:
            answer = None
        return answer

    def postAdminCreate(self, avatar):
        if self.postAdmin == None:
            self.postAdmin = PostAdmin(avatar)
        else:
            self.postAdmin.dialog.deiconify()
            self.postAdmin.dialog.focus_set()

    def questionAdminCreate(self, avatar):
        if self.questionAdmin == None:
            self.questionAdmin = QuestionAdmin(avatar)
        else:
            self.questionAdmin.dialog.deiconify()
            self.questionAdmin.dialog.focus_set()

    def roomAdminCreate(self, avatar):
        if self.roomAdmin == None:
            self.roomAdmin = RoomAdmin(avatar)
        else:
            self.roomAdmin.dialog.deiconify()
            self.roomAdmin.dialog.focus_set()

    def subjectAdminCreate(self, avatar):
        if self.subjectAdmin == None:
            self.subjectAdmin = SubjectAdmin(avatar)
        else:
            self.subjectAdmin.dialog.deiconify()
            self.subjectAdmin.dialog.focus_set()

    def remote_addQueueDialog(self, queueId, queueName):
        if self.roomAdmin != None:
            self.roomAdmin.addEmptyQueue(queueId, queueName)

    def remote_removeQueueDialog(self, queueId):
        if self.roomAdmin != None:
            self.roomAdmin.removeQueue(queueId)

    def remote_updateQueueDialog(self, queueId, queueLen):
        if self.roomAdmin != None:
            self.roomAdmin.updateQueue(queueId, queueLen)

    def remote_wbMyColor(self, color):
        self.wb.setMyColor(color)

    def remote_wbLockWhiteBoard(self):
        self.wb.setROMode()

    def remote_wbUnlockWhiteBoard(self):
        self.wb.unsetROMode()

    def remote_wbShowSubjects(self):
        self.subjectAdminCreate(self.avatar)
