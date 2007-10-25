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

from Tkinter import *
from Client import Client
from twisted.cred import credentials
from twisted.internet import reactor
from LoginDialogDemo import *
import tkMessageBox
from beppo.Strings import _
import sys
import sha

class LoginDialog(Toplevel):
    def __init__(self, master, callback, cancelCallback, host, port, factory, client, initialUser = "Achuni", initialPassword = "lala"):
        Toplevel.__init__(self, master=None)
        self.callback = callback
        self.cancelCallback = cancelCallback
        self.client = client
        self.factory = factory
        self.frame = Frame(self)
        self.master = master
        self.initialUser = initialUser
        self.initialPassword = initialPassword
        self.initialPort = port

        self.userlabel=Label(self.frame, text=_("Usuario") + ":")
        self.userlabel.pack(side=TOP, padx=5, pady=5)

        self.username = Entry(self.frame)
        self.username.insert(0, initialUser)
        self.username.pack(side=TOP, padx=5, pady=5)

        self.passlabel=Label(self.frame, text=_("Contraseña") + ":")
        self.passlabel.pack(side=TOP, padx=5, pady=5)

        self.password = Entry(self.frame, show='*')
        self.password.insert(0, initialPassword)
        self.password.pack(side=TOP, padx=5, pady=5)

        self.serverlabel = Label (self.frame, text=_("Servidor"))
        self.serverlabel.pack (side=TOP, padx=5, pady=5)

        self.server = Entry(self.frame)
        self.server.insert (0, host + ":" + str(port))
        self.server.pack(side=TOP, padx=5, pady=5)

        self.okbutton = Button(self.frame, text=_("Conectarse"))
        self.okbutton.bind("<Button-1>", self.login)
        self.okbutton.pack(side=LEFT, padx=5, pady=5)

        self.exitbutton = Button(self.frame, text=_("Cancelar"), command=self.quit)
        self.exitbutton.bind("<Button-1>", self.cancelCallback)
        self.exitbutton.pack(side=LEFT, padx=5, pady=5)

        self.protocol("WM_DELETE_WINDOW", self.cancelCallback)

        self.bind("<Return>", self.login)
        self.username.focus_set()

    def run(self):
        self.frame.pack()
        self.transient(self.master)
        self.focus_set()
        self.grab_set()

    def login(self, event):
        user = self.username.get()
        pswd = self.password.get()
        pswd = sha.new(pswd).hexdigest() #encrypting with sha-1
        server = self.server.get().split(':', 1)
        host = server[0]
        port = self.initialPort
        if len(server) == 2 and server[1].isdigit():
            port = int(server[1])
        self.con = reactor.connectTCP(host, port, self.factory)
        d = self.factory.login(credentials.UsernamePassword(user, pswd), client=self.client)
        d.addCallback(self.destroySelf)
        d.addCallback(self.callback)
        d.addErrback(self.loginError)
        return d

    def destroySelf(self, data):
        self.destroy()
        return data

    def loginError(self, failure):
        if failure.getErrorMessage()=='no_existe': 
            #solo se accede si se está corriendo en modo demo.
            self.askDemo()
        else:
            tkMessageBox.showerror(_("Error de login"), _("Error al conectarse") + ":\n "+failure.getErrorMessage())


    def askDemo(self):
        answer = tkMessageBox.askquestion(_("Error de login"), _("El usuario ingresado no existe. \n ¿Desea crear un usuario temporal?"))
        if answer == "yes":
            ask = LoginDialogDemo(self.master,self.callback, self.loginError, self.client, self.factory, self.username.get())
            ask.run()
            self.destroy()
