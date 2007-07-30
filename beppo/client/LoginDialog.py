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
import tkMessageBox
from beppo.Strings import _
import sys

class LoginDialog(Toplevel):
    def __init__(self, master, callback, cancelCallback, host, port, factory, client, initialUser = "Guest", initialPassword = "guest"):
        Toplevel.__init__(self, master=None)
        self.callback = callback
        self.cancelCallback = cancelCallback
        self.client = client
        self.factory = factory
        self.frame = Frame(self)
        self.host = host
        self.port = port
        self.master = master
        self.initialUser = initialUser
        self.initialPassword = initialPassword

        self.userlabel=Label(self.frame, text=_("Usuario") + ":")
        self.userlabel.pack(side=TOP, padx=5, pady=5)

        self.username = Entry(self.frame)
        self.username.insert(0, initialUser)
        self.username.pack(side=TOP, padx=5, pady=5)

        self.passlabel=Label(self.frame, text=_("Contraseña"))
        self.passlabel.pack(side=TOP, padx=5, pady=5)

        self.password = Entry(self.frame, show='*')
        self.password.insert(0, initialPassword)
        self.password.pack(side=TOP, padx=5, pady=5)

        self.okbutton = Button(self.frame, text=_("Conectarse"))
        self.okbutton.bind("<Button-1>", self.login)
        self.okbutton.pack(side=LEFT, padx=5, pady=5)

        self.exitbutton = Button(self.frame, text=_("Cancelar"))
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
        self.con = reactor.connectTCP(self.host, self.port, self.factory)
        d = self.factory.login(credentials.UsernamePassword(user, pswd), client=self.client)
        d.addCallback(self.destroySelf)
        d.addCallback(self.callback)
        d.addErrback(self.loginError)
        return d

    def destroySelf(self, data):
        self.destroy()
        return data

    def loginError(self, failure):
        tkMessageBox.showerror(_("Error de login"), _("Error al conectarse") + ":\n "+failure.getErrorMessage())
