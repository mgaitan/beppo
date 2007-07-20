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

class WBClipboard:
    def __init__(self):
        self.wbClipboard = []

    def clipboardEmpty(self):
        self.wbClipboard = []
    
    def clipboardAddItem(self, kind, points, outline, fill, width, text=None):
        item = {"kind":kind, "points":points, "outline":outline, "fill":fill, "width":width, "text": text}
        self.wbClipboard.append(item)

    def clipboardGetItems(self):
        return self.wbClipboard
