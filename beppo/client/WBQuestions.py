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
from Tkinter import *
import tkMessageBox
from beppo.Strings import _
from beppo.Constants import IN_QUEUE, IN_CLASS, IN_VIEW, OUT, IN_ANSWERING

class QuestionAdmin:
    def __init__(self, avatar):
        self.avatar = avatar
        self.dialog = QuestionDialog(self)
        self.questions = {}
        self.getQuestions()

    def loadQuestions(self, questions):
        self.questions = questions
        self.dialog.refresh()

    def getQuestions(self):
        d = self.avatar.callRemote("getOfflineQuestions")
        d.addCallback(self.loadQuestions)

    def acceptQuestion(self, idQ):
        d = self.avatar.callRemote("acceptOfflineQuestion", idQ)

    def rejectQuestion(self):
        d = self.avatar.callRemote("rejectQuestion")

    def answerQuestion(self):
        d = self.avatar.callRemote("answerOfflineQuestion")

class QuestionDialog(Toplevel):
    def __init__(self, admin):
        Toplevel.__init__(self, master=None)
        self.admin = admin
        self.questions = {}
        self.title(_("Preguntas offline"))
        self.protocol("WM_DELETE_WINDOW", self.closeDialog)
        
        self.frame = Frame(self)
        self.scrollbar = Scrollbar(self.frame, orient=VERTICAL)
        self.roomLabel=Label(self.frame, text=_("Preguntas offline") + ":")
        self.roomLabel.pack(side=TOP, padx=5, pady=5)

        self.listbox = Listbox(self.frame, yscrollcommand=self.scrollbar.set)
        self.listbox.bind("<Double-Button-1>", self.getQuestion)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=1, padx=5, pady=5)
        self.frame.pack(side=TOP, fill=BOTH, expand=1, padx=5, pady=5)

        frameButtons = Frame(self)
        self.acceptButton = Button(frameButtons, text=_("Aceptar"), width=10)
        self.acceptButton.bind("<Button-1>", self.getQuestion)
        self.acceptButton.pack(side=LEFT, padx=5, pady=5)
        self.updateButton = Button(frameButtons, text=_("Actualizar"), width=10)
        self.updateButton.bind("<Button-1>", self.update)
        self.updateButton.pack(side=LEFT, padx=5, pady=5)
        frameButtons.pack()

    def update(self, event=None):
        self.admin.getQuestions()

    def rejectQuestion(self, event=None):
        self.admin.rejectQuestion()

    def answerQuestion(self, event=None):
        self.admin.answerQuestion()
    
    def getQuestion(self, event=None):
        current = self.listbox.curselection()
        if len(current) > 0:
            current = current[0]
            idQ = self.questions[current]
            self.admin.acceptQuestion(idQ)

    def refresh(self, event=None):
        self.listbox.delete(0, END)
        for idQ, question in self.admin.questions.iteritems():
            index = self.listbox.index(END)
            self.listbox.insert(END, "%s %s - %s" % question)
            self.questions[str(index)] = idQ

    def closeDialog(self, event=None):
        self.withdraw()
        
    def changeTo(self, status):
        if status == OUT:
            self.acceptButton.unbind("<Button-1>")
            self.acceptButton["text"] = _("Aceptar")
            self.acceptButton.bind("<Button-1>", self.getQuestion)
            self.updateButton.unbind("<Button-1>")
            self.updateButton["text"] = _("Actualizar")
            self.updateButton.bind("<Button-1>", self.update)
        elif status == IN_ANSWERING:
            self.acceptButton.unbind("<Button-1>")
            self.acceptButton["text"] = _("Rechazar")
            self.acceptButton.bind("<Button-1>", self.rejectQuestion)
            self.updateButton.unbind("<Button-1>")
            self.updateButton["text"] = _("Responder")
            self.updateButton.bind("<Button-1>", self.answerQuestion)
