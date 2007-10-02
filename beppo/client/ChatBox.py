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
from beppo.Strings import _

class ChatBox(Frame):
    ME_COLOR = "#a9a9a9"
    OTHER_COLOR = "#39b2c2"
    BACKGROUND = "#c098af"
    
    def __init__(self, parent):
        Frame.__init__(self)
        self.frame = Frame(self, parent)
        self.frame["bg"] = self.BACKGROUND

        #log del chat con scroll vertical
        self.scroll = Scrollbar(self.frame)       
        self.logbox = Text(self.frame)       
        self.scroll.config(command=self.logbox.yview)
        self.logbox.config(font=('courier', 10, 'normal'), height=4, yscrollcommand=self.scroll.set)
        self.scroll.pack(side=RIGHT, fill=Y)
        self.logbox.pack(side=TOP, expand=YES, fill=Y)


        for i in range(40): 
            self.logbox.insert(END, "This is line %d\n" % i)

        self.frame2 = Frame(self, parent)
        
        self.lineinput = Entry (self.frame2)
        self.lineinput.pack(side=LEFT, expand=YES, fill=BOTH)   

        self.sendbutton = Button(self.frame2, text=_('Enviar'))
        self.sendbutton.pack(side=RIGHT)

        self.frame2.pack(side=BOTTOM)
        
        #self.frame.pack(side=TOP)
