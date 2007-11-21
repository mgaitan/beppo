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
from twisted.internet import defer
from beppo.Strings import _

class ChatBox(Frame):
    ME_COLOR = "#a9a9a9"
    OTHER_COLOR = "#39b2c2"
    BACKGROUND = "#c098af"
    
    def __init__(self, cliente=None):
        Frame.__init__(self)
        self["bg"] = self.BACKGROUND        
        self.frame = Frame(bg=self.BACKGROUND)
        self.frame["bg"] = self.BACKGROUND
        
        self.client = cliente
        

        #log del chat con scroll vertical
        self.scroll = Scrollbar(self.frame)       
        self.logbox = Text(self.frame)       
        self.scroll.config(command=self.logbox.yview)
        self.logbox.config(font=('courier', 10, 'normal'), height=4, yscrollcommand=self.scroll.set)
        self.scroll.pack(side=RIGHT, fill=Y)
        
        self.logbox.bind("<FocusIn>", lambda e: self.lineinput.focus_set())
        
        self.logbox.pack(side=TOP, expand=YES, fill=Y)

        self.lineinput = Entry (self.frame, textvariable=StringVar())
        self.lineinput.config(font=('courier', 10, 'normal'))
        self.lineinput.bind("<Return>", lambda e: self.enviar())
        self.lineinput.pack(side=LEFT, expand=YES, fill=BOTH)   

        self.sendbutton = Button(self.frame, text=_('Enviar'))
        self.sendbutton.config(command=self.enviar)
        self.sendbutton.pack(side=RIGHT)
        
        #self.sendbutton = Button(self.frame, text=_('log'))
        #self.sendbutton.config(command=self.enviarLog)
        #self.sendbutton.pack(side=RIGHT)
        
        
        self.frame.pack(side=BOTTOM)
        
    def enviar(self):
        """si existe, envia la linea al servidor"""
        string =  self.lineinput.get()
        if string != "":
            result = self.client.broadcast_sendMsg(string)
        
    def recibir(self, string):
        """recibe e imprime la linea"""
        self.logbox.insert(END, string + '\n')
        self.logbox.yview(END)
        self.lineinput.delete(0, END)
        self.lineinput.focus_set()
                       
    def limpiarLog(self):   
        self.logbox.delete(0, END)
        
