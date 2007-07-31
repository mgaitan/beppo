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
from twisted.cred import credentials
from twisted.internet import reactor
from twisted.internet import tksupport
from twisted.python import util
from Tkinter import *
from Client import Client
from LoginDialog import LoginDialog
from beppo.Constants import REMOTE_SERVER
from beppo.Constants import TUTOR, PUPIL
from beppo.Constants import EMOTIC, SYMBOL, MATH, APP_URL, APP_NAME
from beppo.Constants import statusMsg, OUT
from beppo.Strings import _
import webbrowser

class Login:
    PORTNO = 10102
    #BACKGROUND = "#c0a9cf"
    BACKGROUND = "#c098af"

    def __init__(self):
        self.window = Tk()
        self.window["bg"] = self.BACKGROUND
        self.window.title(APP_NAME)
        self.window.minsize(700, 550)

        tksupport.install(self.window)
        self.window.protocol("WM_DELETE_WINDOW", self.application_quit)

        self.createMenu()

        selectionGet = self.window.selection_get
        self.client = Client(self, selectionGet)
        self.client.pack()

        self.factory = pb.PBClientFactory()
        self.window.wait_visibility()
        self.logindialog = LoginDialog(self.window, self.loginSuccess, self.application_quit, REMOTE_SERVER, self.PORTNO, self.factory, self.client.cc)
        reactor.callWhenRunning(self.logindialog.run)
        reactor.run()

    def loginSuccess(self, avatar):
        self.client.setAvatar(avatar)
        #self.client.swb.focus_set()
        self.window.bind("<FocusIn>", lambda e: self.client.swb.focus_set())
        df = avatar.callRemote("getWbServer")
        df.addCallback(self.gotRootObject)
        df2 = avatar.callRemote("whoami")
        df2.addCallback(self.updateMenu)
        df3 = avatar.callRemote("myName")
        df3.addCallback(self.client.setName)
        df3.addCallback(lambda a: self.setWindowStatus())

    def setWindowStatus(self, desc=OUT):
        self.window.title(APP_NAME + " - " + self.client.name + " (" + statusMsg[desc] +")")

    def showRoomAdmin(self, event=None):
        self.client.showRooms()

    def showPostAdmin(self, event=None):
        self.client.showPost()

    def showQuestionAdmin(self, event=None):
        self.client.showQuestions()

    def showSubjectAdmin(self, event=None):
        self.client.showSubjects()

    def gotRootObject(self, root):
        self.client.setRoot(root)

    def createMenu(self):
        menubar = Menu(self.window)

        self.fileMenu = Menu(menubar, tearoff=0)
        self.fileMenu.add_command(label=_("Lista de aulas"), command=self.showRoomAdmin)
        self.fileMenu.add_command(label=_("Lista de materias"), command=self.showSubjectAdmin)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label=_("Imprimir"))
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label=_("Salir"), command=self.application_quit)
        menubar.add_cascade(label=_("Archivo"), menu=self.fileMenu)

        self.editMenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("Edicion"), menu=self.editMenu)

        self.emoticMenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("Emoticonos"), menu=self.emoticMenu)

        self.symbolMenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label=_("Simbolos"), menu=self.symbolMenu)

        self.mathMenu = Menu(self.symbolMenu, tearoff=0)
        self.symbolMenu.add_cascade(label=_("Matematica"), menu=self.mathMenu)

        self.greekMenu = Menu(self.symbolMenu, tearoff=0)
        self.symbolMenu.add_cascade(label=_("Griego"), menu=self.greekMenu)

        self.helpMenu = Menu(menubar, tearoff=0)
        self.helpMenu.add_command(label=_("Manual de instrucciones"), command=self.showHelp)
        self.helpMenu.add_command(label=_("Acerca de..."), command=self.showAbout)
        menubar.add_cascade(label=_("Ayuda"), menu=self.helpMenu)

        self.linksMenu = Menu(menubar, tearoff=0)
        self.linksMenu.add_command(label=_("Links utiles"), command=self.showLinks)
        menubar.add_cascade(label=_("Links"), menu=self.linksMenu)

        self.window.config(menu=menubar)

    def showHelp(self):
        webbrowser.open(APP_URL + '/content/help.html', new=0)

    def showLinks(self):
        webbrowser.open(APP_URL + '/content/links.html', new=0)

    def showAbout(self):
        pass

    def updateMenu(self, whoami):
        if whoami == TUTOR:
            self.fileMenu.insert_command(1, label=_("Preguntas offline"), command=self.showQuestionAdmin)
            self.fileMenu.insert_command(2, label=_("Postprocesado de pizarras"), command=self.showPostAdmin)
        self.editMenu.add_command(label=_("Cortar"), accelerator="Ctrl-X", command=self.client.swb.wb.cutSelection)
        self.editMenu.add_command(label=_("Copiar"), accelerator="Ctrl-C", command=self.client.swb.wb.copySelection)
        self.editMenu.add_command(label=_("Pegar"), accelerator="Ctrl-V", command=self.client.swb.wb.paste)
        self.editMenu.add_separator()
        self.editMenu.add_command(label=_("Importar texto"), accelerator="Ctrl-B", command=self.client.swb.wb.pasteForeign)
        self._loadImgMenu(self.emoticMenu, EMOTIC)
        self._loadImgMenu(self.greekMenu, SYMBOL)
        self._loadImgMenu(self.mathMenu, MATH)

    def _loadImgMenu(self, menu, kind):
        first = self.client.swb.wb.imgs.firstKind(kind)
        q = self.client.swb.wb.imgs.getQKind(kind)
        for x in range(first, first + q):
            self._createImgOption(menu, x)

    def _createImgOption(self, menu, imgNumber):
        menu.add_command(image=self.client.swb.wb.imgs.getImg(imgNumber), command=lambda: self.client.swb.wb.putImg(imgNumber))

    def application_quit(self, widget=None):
        if reactor.running:
            reactor.stop()
        self.logindialog.destroy()
        self.window.quit()

if __name__ == '__main__':
    login = Login()
