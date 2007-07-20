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

import cPickle

class WBStatus:
    def __init__(self):
        self.wbStatus = {}
        self.wbOrder = []

    def add(self, key, box):
        assert(key not in self.wbStatus.keys())
        self.wbStatus[key] = box
        self.wbOrder.append(key)
    
    def statusReset(self):
        self.wbStatus = {}
        self.wbOrder = []
    
    def statusGetObject(self, boxId):
        assert(boxId in self.wbStatus.keys())
        return self.wbStatus[boxId]

    def statusMoveItems(self, itemsId, dx, dy, owner):
        for i in itemsId:
            for j in range(0, len(self.wbStatus[i]["points"])):
                if j % 2 == 0:
                    self.wbStatus[i]["points"][j] = self.wbStatus[i]["points"][j] + dx
                else:
                    self.wbStatus[i]["points"][j] = self.wbStatus[i]["points"][j] + dy

    def statusEraseItem(self, itemsId, owner):
        for i in itemsId:
            self.wbOrder.remove(i)
            del(self.wbStatus[i])

    def statusFillItem(self, itemId, color, owner):
        assert(itemId in self.wbStatus.keys())
        self.wbStatus[itemId]["fill"] = color

    def statusAddTextBox(self, boxId, points, color, owner):
        """
        Agrega un textBox al status, en la posicion dada por x e y
        y con el dueño owner
        """
        assert(boxId not in self.wbStatus.keys())
        string = u""
        string = string.encode("utf-8")
        self.wbStatus[boxId] = {"kind":"text", "points":points, "text":"", "line":color, "owner": owner}
        self.wbOrder.append(boxId)
        
    def statusSetField(self, boxId, field, value):
        """
        Setea el campo field del textBox boxId a value
        """
        assert(boxId in self.wbStatus)
        assert(field in self.wbStatus[boxId].keys())
        self.wbStatus[boxId][field] = value

    def statusGetField(self, boxId, field):
        """
        Devuelve el campo field del textBox boxId
        """
        assert(boxId in self.wbStatus)
        assert(field in self.wbStatus[boxId].keys())
        return self.wbStatus[boxId][field]

    def statusGetKeys(self):
        """
        Devuelve una lista con las claves de Status
        """
        return self.wbOrder

    def statusAddItem(self, itemId, kind, points, outline, fill, width, owner):
        assert(itemId not in self.wbStatus.keys())
        self.wbStatus[itemId] = {"kind":kind, "points":points, "outline":outline, "fill":fill, "width":width, "owner": owner}
        self.wbOrder.append(itemId)

    def pickle(self):
        return cPickle.dumps((self.wbStatus, self.wbOrder))

    def unpickle(self, pkl):
        wbStatus, wbOrder = cPickle.loads(pkl)
        self.wbStatus = wbStatus
        self.wbOrder = wbOrder
