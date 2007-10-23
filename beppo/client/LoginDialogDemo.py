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
import tkMessageBox
from beppo.Strings import _
from beppo.Constants import APP_NAME
from twisted.spread import pb
from DemoMaker import demo
from beppo.Constants import TUTOR, PUPIL
import sha
from twisted.trial.util import deferredResult


class LoginDialogDemo(Toplevel):
    def __init__(self, master, callback, errback, client, factory, username):
        Toplevel.__init__(self, master=None)
        self.title(APP_NAME +": " + _("Demo Mode"))
        self.frame = Frame(self)
        self.master = master
        self.callback = callback
        self.errback = errback
        self.client = client
        self.factory = factory
        self.username = username
        
        self.label=Label(self.frame, text=_("Tipo de acceso temporal") + " :")
        self.label.pack(side=TOP, padx=5, pady=5)

        self.opciones = Radiobar(self.frame, ['Tutor','Alumno'])
        self.opciones.pack(side=LEFT, fill=Y)
        self.opciones.config(relief=RIDGE,  bd=2)

        self.okbutton = Button(self.frame, text=_("Crear"))
        self.okbutton.bind("<Button-1>", self.crear)
        self.okbutton.pack(side=LEFT, padx=5, pady=5)

        self.exitbutton = Button(self.frame, text=_("Cancelar"), command=self.destroy)
        self.exitbutton.pack(side=LEFT, padx=5, pady=5)

        self.protocol("WM_DELETE_WINDOW", self.destroy)


    def run(self):
        self.frame.pack()
        self.transient(self.master)
        self.focus_set()
        self.grab_set()

    def crear(self, event):
        if self.opciones.state()=='Tutor':
            de = demo(self.username, TUTOR)
        else:
            de = demo(self.username, PUPIL)
        
        d = de.run()
        d.addCallback(lambda a: self.destroy())
        #d.addCallback(self.callback, None, self.username, 'demo')
        
        #self.client.callRemote("makeDemoUser", self.opciones.state())
        #d = self.factory.getRootObject()
        #d.addCallback(lambda object: object.callRemote("echo", self.opciones.state()))
        
    def login(self, d, user, pswd):
        #recibe el de def el user y el pass y decuelve el avatar al callback o errback(loginSuccess o loginError)
        d.addCallback(lambda a: self.factory.login(credentials.UsernamePassword(user, pswd), client=self.client))
        
        
        d.addCallback(lambda a: self.destroy())
        d.addCallback(self.callback)
        d.addErrback(self.errback)
        return d
   

       
class Radiobar(Frame):
    def __init__(self, parent=None, opciones=[], side=LEFT, anchor=W):
        Frame.__init__(self, parent)
        self.var = StringVar()
        self.var.set(opciones[0])
        for tipo in opciones:
            rad = Radiobutton(self, text=tipo, value=tipo, variable=self.var)
            rad.pack(side=side, anchor=anchor, expand=YES)
    def state(self):
        return self.var.get()
