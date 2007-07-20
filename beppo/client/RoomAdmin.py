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
from beppo.Constants import TUTOR, GENERAL, IACLASS, PACLASS, EXTRA_IACLASS
from beppo.Constants import IN_QUEUE, IN_CLASS, IN_VIEW, OUT, IN_WAITING, IN_ASKING, IN_DECIDING
from Sounds import wav

class RoomAdmin:
    def __init__(self, avatar):
        self.avatar = avatar
        self.queueInfo = {}
        d = avatar.callRemote("whoami")
        d.addCallback(self.showDialog)
        d.addCallback(lambda a: self.getCurrentRooms())

    def showDialog(self, kind):
        if kind == TUTOR:
            self.dialog = RoomAdminDialogTutor(self)
        else:
            self.dialog = RoomAdminDialogPupil(self)

    def refresher(self):
        if self.dialog != None:
            self.dialog.refresh()

    def addEmptyQueue(self, queueId, queueName):
        self.queueInfo[queueId] = (queueName, 0)
        if self.dialog != None:
            self.dialog.refresh()

    def removeQueue(self, queueId):
        del(self.queueInfo[queueId])
        if self.dialog != None:
            self.dialog.refresh()

    def updateQueue(self, queueId, queueLen):
        queueInfo = self.queueInfo[queueId]
        queueInfo = (self.queueInfo[queueId][0], queueLen)
        self.queueInfo[queueId] = queueInfo
        if self.dialog != None:
            self.dialog.refresh()

    def setQueueInfo(self, queueInfo):
        self.queueInfo = queueInfo
        if self.dialog != None:
            self.dialog.refresh()

    def createRoom(self):
        d = self.avatar.callRemote("requestRoom")

    def removeRoom(self):
        d = self.avatar.callRemote("removeRoom")

    def proposeQuestion(self):
        d = self.avatar.callRemote("proposeQuestion")

    def unproposeQuestion(self):
        d = self.avatar.callRemote("unproposeQuestion")

    def enterRoom(self, room):
        d = self.avatar.callRemote("enterRoom", room)

    def viewRoom(self, room):
        d = self.avatar.callRemote("enterViewer", room)

    def leaveRoom(self):
        d = self.avatar.callRemote("leaveRoom")

    def offQuestion(self):
        d = self.avatar.callRemote("offQuestion")

    def getCurrentRooms(self):
        d = self.avatar.callRemote("getRooms")
        d.addCallback(self.setQueueInfo)

    def getRoomInfo(self, room):
        return self.avatar.callRemote("getRoomInfo", room)
        
    def rejectClient(self):
        d = self.avatar.callRemote("rejectClient")

    def acceptClient(self):
        d = self.avatar.callRemote("acceptClient")
    
    def discClient(self):
        d = self.avatar.callRemote("quitClient")


class RoomAdminDialog(Toplevel):
    def __init__(self, admin):
        Toplevel.__init__(self, master=None)
        self.admin = admin
        self.roomId = {}
        self.title(_("Lista de aulas"))

        self.protocol("WM_DELETE_WINDOW", self.closeDialog)

        self.frame = Frame(self)
        self.scrollbar = Scrollbar(self.frame, orient=VERTICAL)
        self.roomLabel=Label(self.frame, text=_("Aulas disponibles") + ":")
        self.roomLabel.pack(side=TOP, padx=5, pady=5)

        self.listbox = Listbox(self.frame, yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side=TOP, padx=5, pady=5)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=1, padx=5, pady=5)
        self.frame.pack(side=TOP, fill=BOTH, expand=1, padx=5, pady=5)
        self.refresh()

    def closeDialog(self, event=None):
        self.withdraw()

    def _roomIdFromList(self):
        roomId = None
        current = self.listbox.curselection()
        if len(current) > 0:
            current = int(current[0])
            roomId = self.roomId[current]
        return roomId

    def roomInfo(self, event=None):
        room = self._roomIdFromList()
        if room != None:
            d = self.admin.getRoomInfo(room)
            d.addCallback(self.showRoomInfo)
    
    def showRoomInfo(self, info):
        if info[1] == GENERAL:
            msg = _("Cola General")
            tkMessageBox.showinfo(_("Informacion"), msg)
            return
        msg = _("Tutor") + ": " + info[0]
        if info[1] == IACLASS:
            end = info[2]
            msg = msg + "\n" + _("Tipo de clase") + ": " + _("Acceso instantaneo") + "\n" + _("Hora de cierre") + ": " + end
        elif info[1] == PACLASS:
            end = info[2]
            msg = msg + "\n" + _("Tipo de clase") + ": " + _("Precoordinada") + "\n" + _("Hora de cierre") + ": " + end
        elif info[1] == EXTRA_IACLASS:
            msg = msg + "\n" + _("Tipo de clase") + ": " + _("Acceso instantaneo (extra)")
        msg = msg + "\n" + _("Materias") + ":\n"
        subjects = info[3]
        for s in subjects:
            msg = msg + "\t" + s + "\n"
        tkMessageBox.showinfo(_("Informacion"), msg)

    def showInfo(self, msg):
        tkMessageBox.showinfo(_("Informacion"), msg)

    def refresh(self):
        self.listbox.delete(0, END)
        for roomId, roomInfo in self.admin.queueInfo.iteritems():
            if roomId == GENERAL:
                roomInfo = (_(roomInfo[0]), roomInfo[1])
            self.roomId[self.listbox.index(END)] = roomId
            self.listbox.insert(END, ("%s (%d " + _("en cola") + ")") % roomInfo)

    def _enableButton(self, btn, cback):
        btn.bind("<Button-1>", cback)
        btn["state"] = NORMAL

    def _disableButton(self, btn):
        btn.unbind("<Button-1>")
        btn["state"] = DISABLED

    def _changeButton(self, btn, newText, newCback):
        btn.unbind("<Button-1>")
        btn.bind("<Button-1>", newCback)
        btn["text"] = newText


class RoomAdminDialogPupil(RoomAdminDialog):
    def __init__(self, admin):
        RoomAdminDialog.__init__(self, admin)

        frameButtons = Frame(self)
        frameButtons2 = Frame(self)
        #self.propButton = Button(frameButtons, text=_("Proponer"), width=7)
        #self.propButton.bind("<Button-1>", self.proposeQuestion)
        #self.propButton.pack(side=LEFT, padx=5, pady=5)
        self.listbox.bind("<Double-Button-1>", self.enterRoom)
        self.propButton = Button(frameButtons, text=_("Entrar"), width=7)
        self.propButton.bind("<Button-1>", self.enterRoom)
        self.propButton.pack(side=LEFT, padx=5, pady=5)
        self.offButton = Button(frameButtons, text=_("Preguntar"), width=7)
        self.offButton.bind("<Button-1>", self.offQuestion)
        self.offButton.pack(side=LEFT, padx=5, pady=5)
        self.viewButton = Button(frameButtons2, text=_("Ver"), width=7)
        self.viewButton.bind("<Button-1>", self.viewRoom)
        self.viewButton.pack(side=LEFT, padx=5, pady=5)
        self.infoButton = Button(frameButtons2, text=_("Informacion"), width=7)
        self.infoButton.bind("<Button-1>", self.roomInfo)
        self.infoButton.pack(side=LEFT, padx=5, pady=5)
        frameButtons.pack()
        frameButtons2.pack()

    def proposeQuestion(self, event=None):
        self.admin.proposeQuestion()
        
    def unproposeQuestion(self, event=None):
        self.admin.leaveRoom()
        self.admin.unproposeQuestion()

    def enterRoom(self, event=None):
        current = self._roomIdFromList()
        if current != None:
            self.admin.enterRoom(current)
        else:
            self.showInfo(_("Seleccionar un aula"))

    def viewRoom(self, event=None):
        current = self._roomIdFromList()
        if current != None:
            self.admin.viewRoom(current)
        else:
            self.showInfo(_("Seleccionar un aula"))

    def leaveRoom(self, event=None):
        self.admin.leaveRoom()
        
    def offQuestion(self, event=None):
        self.admin.offQuestion()

    def changeTo(self, status):
        if status == OUT:
            self.listbox.bind("<Double-Button-1>", self.enterRoom)
            self._enableButton(self.propButton, self.enterRoom)
            self._enableButton(self.viewButton, self.viewRoom)
            self._changeButton(self.offButton, _("Preguntar"), self.offQuestion)
        elif status == IN_ASKING:
            self.listbox.bind("<Double-Button-1>", self.enterRoom)
            self._disableButton(self.viewButton)
        elif status == IN_QUEUE:
            self.listbox.unbind("<Double-Button-1>")
            self._changeButton(self.offButton, _("Abandonar"), self.leaveRoom)
            self._disableButton(self.propButton)
            self._disableButton(self.viewButton)
        elif status == IN_CLASS:
            self.listbox.unbind("<Double-Button-1>")
            self._disableButton(self.propButton)
            self._disableButton(self.viewButton)
        elif status == IN_VIEW:
            self.listbox.unbind("<Double-Button-1>")
            self._changeButton(self.offButton, _("Abandonar"), self.leaveRoom)
            self._disableButton(self.propButton)
            self._disableButton(self.viewButton)
    
class RoomAdminDialogTutor(RoomAdminDialog):
    import base64
    alarm = base64.decodestring(wav)
    def __init__(self, admin):
        RoomAdminDialog.__init__(self, admin)
        self.subjectAdmin = None
        
        frameButtons = Frame(self)
#        frameButtons2 = Frame(self)

        self.createButton = Button(frameButtons, text=_("Crear"), width=12)
        self.createButton.pack(side=LEFT, padx=5, pady=5)
#        self.acceptButton = Button(frameButtons2, text="Aceptar Cliente", width=12)
#        self.acceptButton.pack(side=LEFT, padx=5, pady=5)
#        self.rejectButton = Button(frameButtons2, text="Rechazar Cliente", width=12)
#        self.rejectButton.pack(side=LEFT, padx=5, pady=5)
        self.discButton = Button(frameButtons, text=_("Terminar clase"), width=12)
        self.discButton.pack(side=LEFT, padx=5, pady=5)

        self.createButton.bind("<Button-1>", self.createRoom)
#        self._disableButton(self.acceptButton)
#        self._disableButton(self.rejectButton)
        self._disableButton(self.discButton)

#        frameButtons2.pack(side=BOTTOM)
        frameButtons.pack(side=BOTTOM)
        
    def createRoom(self, event=None):
        self.admin.createRoom()

    def removeRoom(self, event=None):
        self.admin.removeRoom()

    def reject(self, event=None):
        self.admin.rejectClient()

    def accept(self, event=None):
        self.admin.acceptClient()

    def disconnect(self, event=None):
        self.admin.discClient()

    def changeTo(self, status):
        if status == OUT:
            self._changeButton(self.createButton, _("Crear"), self.createRoom)
#            self._disableButton(self.acceptButton)
#            self._disableButton(self.rejectButton)
            self._disableButton(self.discButton)
        elif status == IN_DECIDING:
            self._changeButton(self.createButton, _("Eliminar"), self.removeRoom)
            answer = tkMessageBox.askyesno(_("Nuevo alumno"), _("Aceptar alumno?"))
            if answer:
                self.accept()
            else:
                self.reject()
#            self._enableButton(self.acceptButton, self.accept)
#            self._enableButton(self.rejectButton, self.reject)
            self._disableButton(self.discButton)
            try:
                import winsound
                winsound.PlaySound(self.alarm, winsound.SND_MEMORY)
            except ImportError:
                pass
        elif status == IN_CLASS:
            self._enableButton(self.discButton, self.disconnect)
#            self._disableButton(self.acceptButton)
#            self._disableButton(self.rejectButton)
        elif status == IN_WAITING:
            self._changeButton(self.createButton, _("Eliminar"), self.removeRoom)
#            self._disableButton(self.acceptButton)
#            self._disableButton(self.rejectButton)
            self._disableButton(self.discButton)
