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
from beppo.Constants import TUTOR

class SubjectAdmin:
    def __init__(self, avatar):
        self.avatar = avatar
        self.subjects = {}
        d = avatar.callRemote("whoami")
        d.addCallback(self.showDialog)
        d.addCallback(lambda a: self.getSubjects())
        
    def showDialog(self, kind):
        self.kind = kind
        self.dialog = SubjectDialog(self, kind)

    def loadSubjects(self, subjects):
        self.subjects = subjects

    def updateSubjects(self, subjects):
        for s in self.subjects:
            if s in subjects:
                self.subjects[s] = True
            else:
                self.subjects[s] = False
        d = self.avatar.callRemote("setSubjects", subjects)

    def getSubjects(self):
        d = self.avatar.callRemote("getSubjects")
        d.addCallback(self.loadSubjects)
        d.addCallback(self.dialog.refresh)

class SubjectDialog(Toplevel):
    def __init__(self, admin, kind):
        Toplevel.__init__(self, master=None)
        self.admin = admin
        self.subjects = {}
        self.title(_("Lista de materias"))
        self.protocol("WM_DELETE_WINDOW", self.closeDialog)
        self.protocol("WM_TAKE_FOCUS", self.refresh)
        
        self.frame = Frame(self)
        self.scrollbar = Scrollbar(self.frame, orient=VERTICAL)
        self.roomLabel=Label(self.frame, text=_("Materias") + ":")
        self.roomLabel.pack(side=TOP, padx=5, pady=5)

        selmode = BROWSE
        if kind == TUTOR:
            selmode = MULTIPLE
        
        self.listbox = Listbox(self.frame, selectmode=selmode, yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side=TOP, padx=5, pady=5)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=1, padx=5, pady=5)
        self.frame.pack(side=TOP, fill=BOTH, expand=1, padx=5, pady=5)

        frameButtons = Frame(self)
        self.updateButton = Button(frameButtons, text=_("Aceptar"))
        self.updateButton.bind("<Button-1>", self.update)
        self.updateButton.pack(side=LEFT, padx=5, pady=5)
        self.cancelButton = Button(frameButtons, text=_("Cancelar"))
        self.cancelButton.bind("<Button-1>", self.closeDialog)
        self.cancelButton.pack(side=LEFT, padx=5, pady=5)
        frameButtons.pack()

    def update(self, event=None):
        current = self.listbox.curselection()
        if len(current) == 0:
            tkMessageBox.showinfo(_("Informacion"), _("Elegir al menos una materia"))
        else:
            subjects = [self.subjects[str(i)] for i in current]
            self.admin.updateSubjects(subjects)
            self.closeDialog()

    def refresh(self, event=None):
        self.listbox.delete(0, END)
        for subject, selected in self.admin.subjects.iteritems():
            index = self.listbox.index(END)
            self.listbox.insert(END, "%s" % subject)
            self.subjects[str(index)] = subject
            if selected:
                self.listbox.select_set(index)

    def closeDialog(self, event=None):
        self.withdraw()
        
