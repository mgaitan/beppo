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
from WBToolbar import WBToolbar
from WhiteBoard import WhiteBoard
from ChatBox2 import ChatBox

class ScrolledWB:
    VIEWPORT_WIDTH = 700 # Porción del canvas visible
    VIEWPORT_HEIGHT = 500
    def __init__(self, wbWidth=400, wbHeight=400):
        
        self.frame = Frame(width=self.VIEWPORT_WIDTH, height=self.VIEWPORT_HEIGHT)
        self.wb = WhiteBoard(self.frame, width=self.VIEWPORT_WIDTH, height=self.VIEWPORT_HEIGHT)
        self.tbar = WBToolbar(self.wb.changeTool, self.wb.changeColor, self.wb.changeWidth, self.wb.imgs, self.wb.putImg)
        self.chat = ChatBox(self.frame)
        self.vscroll = Scrollbar(self.frame, orient=VERTICAL, command=self.wb.yview)
        self.hscroll = Scrollbar(self.frame, orient=HORIZONTAL, command=self.wb.xview)
        self.wb.config(xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set)
        self.wb.config(scrollregion=(0,0,wbWidth,wbHeight)) #limitar scroll
        self.wb.maxWidth = wbWidth
        self.wb.maxHeight = wbHeight

        
    def focus_set(self):
        self.wb.focus_set()
    
    def pack(self):
        self.tbar.pack(side=LEFT)
        self.hscroll.pack(side=BOTTOM, fill=X)
        self.chat.pack(side=BOTTOM, fill=X)
        self.vscroll.pack(side=RIGHT, fill=Y)
        self.wb.pack(fill=BOTH, expand=YES)
        self.frame.pack(side=LEFT, fill=BOTH, expand=YES)
