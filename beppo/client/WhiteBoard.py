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
from WBClipboard import WBClipboard
from beppo.Constants import FINE, MEDIUM, BIG, XBIG
from beppo.Constants import BLACK, SELECTION, STIPPLE
from beppo.Constants import TEXT, LINE, RECTANGLE, CIRCLE, SQRT, INTEGRAL, FREEHAND, SYMBOL, AXES, DARROW
from beppo.Constants import FILL, HIGHLIGHT, ERASE_ITEM, ERASE_SELECTION, SELECT, MOVE, PASTE, ARROW, DASH, POST
from beppo.Constants import colorPalette
from ImgsGif import Imgs
import tkFont

class WhiteBoard(Canvas):
    NEAR_RADIO = 5
    NEAR_REMOVE_RADIO = 10
    WHITEBOARD_BORDER = 5
    RW = 1
    RO = 2

    def __init__(self, parent=None, width=450, height=450, color="#FFFFFF"):
        """Inicializa un WhiteBoard con un Canvas de width por height y color de fondo.
        En wbCurrentText se mantiene el id del TextBox de trabajo actual
        Liga los eventos de click del mouse y de presion de teclas a las funciones 
        onClick y onKey, respectivamente, y le da foco al WhiteBoard para poder trabajar.
        """
        Canvas.__init__(self, parent, width=width, height=height, bg=color)
        self.bind("<Button-1>", self.click)
        self.bind("<B1-Motion>", self.mouseMove)
        self.bind("<ButtonRelease-1>", self.release)
        self.bind("<Key>", self.onKey)
        self.bind("<Control-x>", self.cutSelection)
        self.bind("<Control-c>", self.copySelection)
        self.bind("<Control-v>", self.paste)
        self.bind("<Control-b>", self.pasteForeign)
        #self.bind("<FocusOut>", lambda e: self.focus_set())
        #self.focus_set()
        self.maxWidth = width
        self.maxHeight = height
        self.tool = TEXT
        self.color = colorPalette[BLACK]
        self.myColor = colorPalette[BLACK]
        self.lineWidth = FINE
        self.clipboard = WBClipboard()
        self.imgs = Imgs()
        self.mode = self.RW
        self.reset()
        self.font = ('Arial', 14, 'bold')
        self.tk.call('encoding', 'system', 'utf-8')

    def putImg(self, number):
        self.img = number

    def setMyColor(self, color):
        self.myColor = colorPalette[color]

    def setROMode(self):
        self.mode = self.RO
        self.focus("")
        self.wbCurrentText = None
        self.wbCurrentObject = None
        self.clearSelection()

    def unsetROMode(self):
        self.mode = self.RW
        
    def changeTool(self, tool):
        self.tool = tool
        if tool==TEXT:
            self.focus_set()
        else:
            self.focus("")
            


    def changeColor(self, color):
        self.color = colorPalette[color]

    def changeWidth(self, width):
        self.lineWidth = width

    def _updateDelta(self, x1, y1):
        y0 = self.pointList.pop()
        x0 = self.pointList.pop()
        self.pointList.append(x1)
        self.pointList.append(y1)
        dx = x1 - x0
        dy = y1 - y0
        self.dx = self.dx + dx
        self.dy = self.dy + dy
        return (dx, dy)

    def mouseMove(self, event):
        x1 = self.canvasx(event.x)
        y1 = self.canvasy(event.y)
        if self.tool == MOVE:
            delta = self._updateDelta(x1, y1)
            for x in self.selectedItems:
                self.move(x, *delta)
            self.move(self.selectionBox, *delta)
        elif self.wbCurrentObject != None and self.tool != FREEHAND and self.tool != HIGHLIGHT:
            x0 = self.pointList[0]
            y0 = self.pointList[1]
            self.coords(self.wbCurrentObject, x0, y0, x1, y1)
        elif self.wbCurrentObject != None and (self.tool == FREEHAND or self.tool == HIGHLIGHT):
            self.pointList.append(x1)
            self.pointList.append(y1)
            self.coords(self.wbCurrentObject, *self.pointList)
    
    def release(self, event):
        if self.mode == self.RO:
            return
        x1 = self.canvasx(event.x)
        y1 = self.canvasy(event.y)
        self.pointList.append(x1)
        self.pointList.append(y1)
        x0 = self.pointList[0]
        y0 = self.pointList[1]
        if self.tool == SQRT or self.tool == INTEGRAL or self.tool == AXES:
            self.delete(self.wbCurrentObject)
        if self.img != None:
            self.addItem(SYMBOL, self.pointList, self.myColor, "", self.img)
            self.img = None
        elif ((x0 == x1 and y0 == y1) and self.tool != SELECT \
          and self.tool != MOVE and self.tool != ERASE_ITEM \
          and self.tool != ERASE_SELECTION and self.tool != FILL) or self.tool == TEXT:
            self.delete(self.wbCurrentObject)
            self.createTextBox(self.pointList, self.myColor)
        elif self.tool == ERASE_SELECTION:
            self.delete(self.wbCurrentObject)
            if (x0 != x1) or (y0 != y1):
                self.doSelection(x0, y0, x1, y1)
                self.eraseSelectedItems(self.selectedItems)
                self.clearSelection()
        elif self.tool == ERASE_ITEM:
            self.doSelection(x1, y1, x1, y1)
            if self.selectedItems != [] and self._getItemKind(self.selectedItems[0]) != TEXT:
                self.eraseSelectedItems(self.selectedItems)
            self.clearSelection()
        elif self.tool == SELECT:
            self.delete(self.wbCurrentObject)
            self.doSelection(x0, y0, x1, y1)
            if self.selectedItems != []:
                bbox = self.bbox(*self.selectedItems)
                self.selectionBox = self.create_rectangle(bbox, fill=colorPalette[SELECTION], stipple=colorPalette[STIPPLE])
        elif self.tool == MOVE:
            self.moveItems(self.selectedItems, self.dx, self.dy)
            self.tool = SELECT
            self.dx = 0
            self.dy = 0
        elif self.tool == SQRT or self.tool == INTEGRAL or self.tool == AXES:
            self.addItem(self.tool, self.pointList, self.myColor, "", FINE)
        elif self.tool != TEXT and self.tool != FILL:
            self.addItem(self.tool, self.pointList, self.color, "", self.lineWidth)
        self.wbCurrentObject = None
        self.pointList = []

    def click(self, event):
        """Borra el último TextBox en caso de ser necesario (es decir, si no tiene texto).
        Además llama a las funciones onClick que reacciona a eventos del boton 1 del mouse,
        y a moveCursor, que posiciona el cursor dentro del TextBox actual
        """
        if self.mode == self.RO:
            return
        x0 = self.canvasx(event.x)
        y0 = self.canvasy(event.y)
        self.pointList.append(x0)
        self.pointList.append(y0)

        self.sendMsg("lalala")
        self._onClick()

    def foreignObjectsCount(self):
        return len(self.foreignObjects)
                   
    def moveCursor(self, x, y):
        """Mueve el cursor hasta la posicion indicada por el evento
        """
        if self.wbCurrentText:
            self.icursor(self.wbCurrentText, "@%d,%d" % (x, y))

    def _onClick(self):
        """
        Callback que reacciona ante el click del mouse y, dependiendo
        de si hay un TextBox cerca o no, cambia el valor de wbCurent
        o crea un nuevo TextBox, respectivamente
        """
        x0 = self.pointList[0]
        y0 = self.pointList[1]
        if self.tool == SELECT and self.clickOnSelection():
            self.tool = MOVE
        else:
            self.clearSelection()
        if self.tool == TEXT or self.img != None:
            pass
        elif self.tool == LINE:
            newLine = self.create_line(x0, y0, x0, y0, fill=self.color, width=self.lineWidth)
            self.itemconfig(newLine, tags=self.tool)
            self.wbCurrentObject = newLine
        elif self.tool == ARROW:
            newLine = self.create_line(x0, y0, x0, y0, fill=self.color, width=self.lineWidth, arrow=LAST)
            self.itemconfig(newLine, tags=self.tool)
            self.wbCurrentObject = newLine
        elif self.tool == DARROW:
            newLine = self.create_line(x0, y0, x0, y0, fill=self.color, width=self.lineWidth, arrow=BOTH)
            self.itemconfig(newLine, tags=self.tool)
            self.wbCurrentObject = newLine
        elif self.tool == DASH:
            newLine = self.create_line(x0, y0, x0, y0, fill=self.color, width=self.lineWidth, dash=10)
            self.itemconfig(newLine, tags=self.tool)
            self.wbCurrentObject = newLine
        elif self.tool == RECTANGLE:
            newRect = self.create_rectangle(x0, y0, x0, y0, outline=self.color, width=self.lineWidth)
            self.itemconfig(newRect, tags=self.tool)
            self.wbCurrentObject = newRect
        elif self.tool == CIRCLE:
            newCircle = self.create_oval(x0, y0, x0, y0, outline=self.color, width=self.lineWidth)
            self.itemconfig(newCircle, tags=self.tool)
            self.wbCurrentObject = newCircle
        elif self.tool == SQRT or self.tool == INTEGRAL or self.tool == AXES:
            newItem = self.create_rectangle(x0, y0, x0, y0, outline=self.myColor)
            self.wbCurrentObject = newItem
        elif self.tool == FREEHAND:
            newLine = self.create_line(x0, y0, x0, y0, fill=self.color, width=self.lineWidth)
            self.itemconfig(newLine, tags=self.tool)
            self.wbCurrentObject = newLine
        elif self.tool == HIGHLIGHT:
            newLine = self.create_line(x0, y0, x0, y0, fill=self.color, width=self.lineWidth)
            self.itemconfig(newLine, tags=self.tool)
            self.lower(newLine, self.rBase)
            self.wbCurrentObject = newLine
        elif self.tool == FILL:
            item = self.findItem(x0, y0)
            if item != None:
                self.fillItem(item, self.color)
        elif self.tool == ERASE_SELECTION or self.tool == SELECT:
            if self.wbCurrentText != None:
                if self.itemcget(self.wbCurrentText, "text") == "":
                    self.eraseSelectedItems([self.wbCurrentText])
            self.wbCurrentText = None
            self.focus("")
            newSelection = self.create_rectangle(x0, y0, x0, y0, fill=colorPalette[SELECTION], stipple=colorPalette[STIPPLE])
            self.wbCurrentObject = newSelection

    def onKey(self, event):
        """
        Callback que reacciona ante el pulsado de una tecla
        y llama a la funcion insertChar para el TextBox actual
        """
        c = event.char
        sym = event.keysym
        if self.wbCurrentText != None:
            insert = self.index(self.wbCurrentText, INSERT)
            # Vemos que tipo de tecla es y actuamos en consecuencia
            if sym == "Left":
                self.icursor(self.wbCurrentText, insert - 1)
            elif sym == "Right":
                self.icursor(self.wbCurrentText, insert + 1)
            elif sym == "Home":
                self.icursor(self.wbCurrentText, 0)
            elif sym == "End":
                self.icursor(self.wbCurrentText, END)
            elif sym == "Delete":
                self.deleteChars(self.wbCurrentText, insert, insert)
            elif sym == "BackSpace":
                if insert > 0:
                    self.deleteChars(self.wbCurrentText, insert - 1, insert - 1)
                elif self.itemcget(self.wbCurrentText, "text") == "":
                    self._removeNext()
            elif sym == "Return":
                self.insertChars(self.wbCurrentText, insert, "\n")
            else:
                self.insertChars(self.wbCurrentText, insert, c)

    def _removeNext(self):
        delete = None
        coords = self.coords(self.wbCurrentText)
        next = self.nextTextBox(coords[0], coords[1], self.NEAR_REMOVE_RADIO, self.wbCurrentText)
        if next != None:
            coords2 = self.coords(next)
            h = abs(coords2[1] - coords[1])/2
            self.focus(next)
            delete = self.wbCurrentText
            self.eraseSelectedItems([self.wbCurrentText])
            self.wbCurrentText = next
            self.moveCursor(coords[0], coords2[1] + h)
        else:
            next = self.nearestImage(coords[0], coords[1], self.NEAR_REMOVE_RADIO)
            if next != None:
                coords2 = list(self.coords(next))
                delete = next
                self.eraseSelectedItems([next])
                self.createTextBox(coords2, self.myColor)
#        if delete in self.selectedItems:
#            self.selectedItems.remove(delete)

    def cutSelection(self, event=None):
        if self.mode == self.RO:
            return
        if self.tool == SELECT:
            self.copySelection(event)
            self.eraseSelectedItems(self.selectedItems)
            self.clearSelection()

    def copySelection(self, event=None):
        if self.mode == self.RO:
            return
        if self.tool == SELECT and self.selectedItems != []:
            objectsId = self._filterItemsId(self.selectedItems)
            self.clipboard.clipboardEmpty()
            for x in objectsId:
                tags = self.gettags(x)
                kind = self._getItemKind(x)
                coords = list(self.coords(x))
                text = None
                outline = None
                fill = None
                width = None
                if kind == SYMBOL:
                    width = int(tags[1])
                if kind == LINE or kind == ARROW or kind == DARROW \
                  or kind == DASH or kind == FREEHAND or kind == HIGHLIGHT:
                    outline = self.itemcget(x, "fill")
                    width = self.itemcget(x, "width")
                if kind == RECTANGLE or kind == CIRCLE:
                    outline = self.itemcget(x, "outline")
                    fill = self.itemcget(x, "fill")
                    width = self.itemcget(x, "width")
                if kind == INTEGRAL:
                    coords = self._getIntegralCoords(x, float(tags[2]))
                    outline = self.itemcget(x, "fill")
                if kind == SQRT:
                    coords = self._getSqrtCoords(x, float(tags[2]))
                    outline = self.itemcget(x, "fill")
                if kind == AXES:
                    coords = self._getAxesCoords(x, float(tags[2]), float(tags[3]))
                    outline = self.itemcget(x, "fill")
                if kind == TEXT:
                    text = self.itemcget(x, "text")
                    outline = self.itemcget(x, "fill")
                self.clipboard.clipboardAddItem(kind, coords, outline, fill, width, text)

    def paste(self, event=None):
        if self.mode == self.RO:
            return
        if self.tool == SELECT:
            self.clearSelection()
            for x in self.clipboard.clipboardGetItems():
                if x["kind"] == TEXT:
                    self.addTextBox(x["points"], x["outline"])
                    self.insertChars(self.wbCurrentText, 0, x["text"])
                    self.addToSelection(self.wbCurrentText)
                    self.focus("")
                    self.wbCurrentText = None
                else:
                    self.addItem(x["kind"], x["points"], x["outline"], x["fill"], x["width"], PASTE)

    def pasteForeign(self, event=None):
        if self.mode == self.RO:
            return
        if self.wbCurrentText != None:
            insert = self.index(self.wbCurrentText, INSERT)
            txt = self.client.getSystemClipboard()
            self.insertChars(self.wbCurrentText, insert, txt)

    def addToSelection(self, item):
        items = self._findItemsTag(item)
        if self.selectedItems == []:
            self.selectedItems = items
            bbox = self.bbox(*self.selectedItems)
            self.selectionBox = self.create_rectangle(bbox, fill=colorPalette[SELECTION], stipple=colorPalette[STIPPLE])
            #self.lower(self.selectionBox, self.rBase)
        else:            
            self.selectedItems = self.selectedItems + items
            bbox = self.bbox(*self.selectedItems)
            self.coords(self.selectionBox, *bbox)

    def clickOnSelection(self):
        ret = False
        x1 = self.pointList[0]
        y1 = self.pointList[1]
        if self.selectionBox != None:
            box = self.coords(self.selectionBox)
            if box[0] <= x1 <= box[2] and box[1] <= y1 <= box[3]:
                ret = True
        return ret

    def clearSelection(self):
        if self.selectionBox != None:
            self.delete(self.selectionBox)
            self.selectionBox = None
        self.selectedItems = []

    def _getItemId(self, item):
        itemId = item
        itemTag = self.gettags(item)
        kind = self._getItemKind(itemId)
        if kind == INTEGRAL or kind == SQRT or kind == AXES:
            itemId = int(itemTag[1][4:])
        return itemId

    def _getItemKind(self, item):
        itemTag = self.gettags(item)
        kind = int(itemTag[0])
        return kind

    def _filterItemsId(self, items):
        res = []
        for x in items:
            itemId = self._getItemId(x)
            if itemId not in res:
                res.append(itemId)
        return res

    def _findItemsTag(self, item):
        ret = None
        itemTag = self.gettags(item)
        kind = self._getItemKind(item)
        if kind == INTEGRAL or kind == SQRT or kind == AXES:
            res = self.find_withtag(itemTag[1])
            res = list(res)
        else:
             res = [item]
        return res

    def findItem(self, x, y):
        ret = None
        res = self.find_overlapping(x, y, x, y)
        res = filter(lambda x: not self._getItemId(x) in self.foreignObjects.values(), res)
        if(len(res) > 0):
            ret = res[0]
        return ret

    def findItemsEnclosed(self, x0, y0, x1, y1):
        res = self.find_enclosed(x0, y0, x1, y1)
        res = list(res)
        res = self._filterSearch(res)
        #res = filter(lambda x: not self._getItemId(x) in self.foreignObjects.values(), res)
        return res

    def _filterSearch(self, search):
        remove = []
        for x in search:
            if self._getItemId(x) in self.foreignObjects.values():
                remove.append(x)
            else:
                isComplete = True
                itemTag = self.gettags(x)
                kind = self._getItemKind(x)
                if kind == INTEGRAL or kind == SQRT or kind == AXES:
                    res = self.find_withtag(itemTag[1])
                    res = list(res)
                    for y in res:
                        if y not in search:
                            isComplete = False
                if not isComplete:
                    remove.append(x)
        for x in remove:
            search.remove(x)
        return search
        
    def doSelection(self, x0, y0, x1, y1):
        if x0 == x1 and y0 == y1:
            item = self.findItem(x0,y0)
            if item != None:
                self.selectedItems = self._findItemsTag(item)
        else:
            self.selectedItems = self.findItemsEnclosed(x0,y0,x1,y1)

    def moveItems(self, selection, dx, dy, foreignId=None):
        if foreignId is None:
            objectsId = self._filterItemsId(selection)
            result = self.client.broadcast_moveItems(objectsId, dx, dy)
        else:
            for i in selection:
                to_move = self._findItemsTag(self.foreignObjects[i])
                for x in to_move:
                    self.move(x, dx, dy)
            result = defer.Deferred()
        return result

    def eraseSelectedItems(self, selection, foreignId=None):
        if foreignId is None:
            objectsId = self._filterItemsId(selection)
            self.wbCurrentText = None
            self.delete(*selection)
            result = self.client.broadcast_eraseItem(objectsId)
        else:
            to_remove = []
            for i in selection:
                to_remove = to_remove + self._findItemsTag(self.foreignObjects[i])
                del(self.foreignObjects[i])
            self.delete(*to_remove)
            result = defer.Deferred()
        return result

    def fillItem(self, item, color, foreignId=None):
        if foreignId is None:
            itemId = self._getItemId(item)
            kind = self._getItemKind(itemId)
            if kind == INTEGRAL or kind == SQRT or \
              kind == AXES or kind == TEXT or kind == SYMBOL:
                return
            items = self._findItemsTag(item)
            for x in items:
                self.itemconfigure(x, fill=color)
            result = self.client.broadcast_fillItem(itemId, color)
        else:
            itemId = self.foreignObjects[foreignId]
            items = self._findItemsTag(itemId)
            for x in items:
                self.itemconfigure(x, fill=color)
            result = defer.Deferred()
        return result

    def createItem(self, kind, points, outline, fill, width):
        if kind == LINE:
            newItem = self.create_line(points, fill=outline, width=width)
            self.itemconfig(newItem, tags=(LINE,))
        elif kind == ARROW:
            newItem = self.create_line(points, fill=outline, width=width, arrow=LAST)
            self.itemconfig(newItem, tags=(ARROW,))
        elif kind == DARROW:
            newItem = self.create_line(points, fill=outline, width=width, arrow=BOTH)
            self.itemconfig(newItem, tags=(DARROW,))
        elif kind == DASH:
            newItem = self.create_line(points, fill=outline, width=width, dash=10)
            self.itemconfig(newItem, tags=(DASH,))
        elif kind == RECTANGLE:
            newItem = self.create_rectangle(points, outline=outline, fill=fill, width=width)
            self.itemconfig(newItem, tags=(RECTANGLE,))
        elif kind == CIRCLE:
            newItem = self.create_oval(points, outline=outline, fill=fill, width=width)
            self.itemconfig(newItem, tags=(CIRCLE,))
        elif kind == SQRT:
            newItem = self.createSqrt(points, outline)
        elif kind == INTEGRAL:
            newItem = self.createIntegral(points, outline)
        elif kind == AXES:
            newItem = self.createAxesBox(points, outline)
        elif kind == FREEHAND:
            newItem = self.create_line(points, fill=outline, width=width)
            self.itemconfig(newItem, tags=(FREEHAND,))
        elif kind == HIGHLIGHT:
            newItem = self.create_line(points, fill=outline, width=width)
            self.itemconfig(newItem, tags=(HIGHLIGHT,))
            self.lower(newItem, self.rBase)
        elif kind == SYMBOL:
            newItem = self.createImg(points, width)
        return newItem
    
    def addItem(self, kind, points, outline, fill, width, foreignId=None):
        if foreignId == None:
            if kind == SQRT or kind == INTEGRAL or kind == SYMBOL or kind == AXES:
                self.wbCurrentObject = self.createItem(kind, points, outline, fill, width)
            result = self.client.broadcast_addItem(self.wbCurrentObject, kind, points, outline, fill, width)
        elif foreignId == PASTE or foreignId == POST:
            newItem = self.createItem(kind, points, outline, fill, width)
            result = self.client.broadcast_addItem(newItem, kind, points, outline, fill, width)
            if foreignId == PASTE:
                self.addToSelection(newItem)
        else:
            newItem = self.createItem(kind, points, outline, fill, width)
            self.foreignObjects[foreignId] = newItem
            result = defer.Deferred()

    def createImg(self, points, number, foreignId=None):
        newImg = self.create_image(points[0], points[1], image=self.imgs.getImg(number))
        self.itemconfig(newImg, tags=(SYMBOL, number))
        return newImg

    def createSqrt(self, points, color, foreignId=None):
        x0 = points[0]
        y0 = points[1]
        x1 = points[2]
        y1 = points[3]
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        h = y1 - y0
        y2 = y0 + h/2
        x2 = x0 + h/5
        dx = x1 + h/5
        newLine1 = self.create_line(x0, y2, x2, y1, fill=color)
        newLine2 = self.create_line(x2, y1, x2, y0, fill=color)
        newLine3 = self.create_line(x2, y0, dx, y0, fill=color)
        newLine4 = self.create_line(dx, y0, dx, y0 + h/10, fill=color)
        tag = "sqrt" + str(newLine2)
        self.itemconfig(newLine2, tags=(SQRT, tag, x1 - x0))
        self.itemconfig(newLine3, tags=(SQRT, tag, x1 - x0))
        self.itemconfig(newLine1, tags=(SQRT, tag, x1 - x0))
        self.itemconfig(newLine4, tags=(SQRT, tag, x1 - x0))
        return newLine2

    def createIntegral(self, points, color, foreignId=None):
        x0 = points[0]
        y0 = points[1]
        x1 = points[2]
        y1 = points[3]
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        h = y1 - y0
        w = h/10
        x2 = x0 + w
        newLine1 = self.create_arc(x2, y0 + h/5, x2+w, y0, start=180, extent=-180, style=ARC, outline=color)
        newLine2 = self.create_line(x2, y1-h/10, x2, y0+h/10, fill=color)
        newLine3 = self.create_arc(x2, y1-h/5, x0, y1, start=0, extent=-180, style=ARC, outline=color)
        tag = "intg" + str(newLine2)
        self.itemconfig(newLine2, tags=(INTEGRAL, tag, h))
        self.itemconfig(newLine3, tags=(INTEGRAL, tag, h))
        self.itemconfig(newLine1, tags=(INTEGRAL, tag, h))
        return newLine2

    def createAxesBox(self, points, color, foreignId=None):
        x0 = points[0]
        y0 = points[1]
        x1 = points[2]
        y1 = points[3]
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        h = y1 - y0
        w = x1 - x0
        hs = w / 12
        vs = h / 12
        orig = self.create_line(x0 + w/2, y0 + h/2, x0 + w/2, y0 + h/2, fill=color)
        tag = "axes" + str(orig)
        for i in range(0, 13):
            hLine = self.create_line(x0, y0 + i*vs, x1, y0 + i*vs, fill=color)
            vLine = self.create_line(x0 + i*hs, y0, x0 + i*hs, y1, fill=color)
            self.itemconfig(hLine, tags=(AXES, tag, h, w))
            self.itemconfig(vLine, tags=(AXES, tag, h, w))
        self.itemconfig(orig, tags=(AXES, tag, h, w))
        return orig

    def _getIntegralCoords(self, integralId, h):
        coords = self.coords(integralId)
        res = [coords[0] - h/10, coords[3] - h/10, coords[0] - h/10, coords[1] + h/10]
        return res

    def _getSqrtCoords(self, sqrtId, w):
        coords = self.coords(sqrtId)
        h = coords[1] - coords[3]
        res = [coords[0]-h/5, coords[1], coords[0]-h/5 + w, coords[3]]
        return res

    def _getAxesCoords(self, axesId, h, w):
        coords = self.coords(axesId)
        x0 = coords[0] - w/2
        y0 = coords[1] - h/2
        res = [x0, y0, x0 + w, y0 + h]
        return res

    def createTextBox(self, points, color, foreignId=None):
        if self.wbCurrentText != None:
            if self.itemcget(self.wbCurrentText, "text") == "":
                self.eraseSelectedItems([self.wbCurrentText])
                self.wbCurrentText = None
        near = self.nearestTextBox(points[0], points[1], self.NEAR_RADIO)
        if near != None:
            self.focus(near)
            self.wbCurrentText = near
            self.moveCursor(points[0], points[1])
        else:
            self.addTextBox(points, color)

    def addTextBox(self, points, color, foreignId=None):
        """
        Crea un nuevo TextBox en la posicion (x,y)
        """
        x = points[0]
        y = points[1]
        newText = self.create_text(x, y, fill=color, font=self.font)
        self.itemconfig(newText, justify=LEFT)
        self.itemconfig(newText, anchor=NW)
        self.itemconfig(newText, width=self.maxWidth - x - self.WHITEBOARD_BORDER)
        self.itemconfig(newText, tags=(TEXT, ))
        if foreignId is None:
            self.wbCurrentText = newText
            self.focus(newText)
            result = self.client.broadcast_addTextBox(newText, points, color)
        else:
            self.foreignObjects[foreignId] = newText
            result = defer.Deferred()
        return result

    def insertChars(self, textbox, index, string, foreignId=None):
        """
        Inserta string desde index en la caja de texto con id dado por
        textbox.
        """
        if foreignId is None:
            try:
                string = unicode(string, 'utf-8')
            except TypeError:
                pass
            result = self.client.broadcast_insertChars(textbox, index, string)
        else:
            textbox = self.foreignObjects[foreignId]
            result = defer.Deferred()
        self.insert(textbox, index, string)
        return result

    def sendMsg(self, string):
        """
        envia string al chat cliente
        """
        try:
            string = unicode(string, 'utf-8')
        except TypeError:
            pass
        result = self.client.broadcast_sendMsg(string)        
        
        

    def addTextBoxFull(self, points, text, color, foreignId=None):
        self.addTextBox(points, color, foreignId)
        self.insertChars(self.wbCurrentText, 0, text, foreignId)

    def deleteChars(self, textbox, startIndex, endIndex, foreignId=None):
        """
        Borra el texto entre startIndex y endIndex de la caja de texto 
        con id dado por textbox.
        """
        if foreignId is None:
            result = self.client.broadcast_deleteChars(textbox, startIndex, endIndex)
        else:
            textbox = self.foreignObjects[foreignId]
            result = defer.Deferred()
        self.dchars(textbox, startIndex, endIndex)
        return result

    def nearestTextBox(self, x0, y0, dist):
        """
        Chequea si hay un TextBox a menos de dist pixeles
        a partir de la posicion (x,y).
        Devuelve: None -> si no existe
                  ret -> id de uno de los TextBoxes que se encuentren
        """
        res = self.find_overlapping(x0 - dist, y0 - dist + self.NEAR_RADIO, x0 + dist, y0 + dist + self.NEAR_RADIO)
        res = filter(lambda x: not x in self.foreignObjects.values() and self.type(x) == "text", res)
        ret = None
        if(len(res) > 0):
            ret = res[0]
        return ret

    def nextTextBox(self, x0, y0, dist, tbox=None):
        res = self.find_overlapping(x0 - dist, y0 - dist + self.NEAR_RADIO, x0 + dist, y0 + dist + self.NEAR_RADIO)
        res = filter(lambda x: not x in self.foreignObjects.values() and self.type(x) == "text" and x != tbox, res)
        ret = None
        if(len(res) > 0):
            ret = res[0]
        return ret

    def nearestImage(self, x0, y0, dist):
        """
        Chequea si hay un TextBox a menos de dist pixeles
        a partir de la posicion (x,y).
        Devuelve: None -> si no existe
                  ret -> id de uno de los TextBoxes que se encuentren
        """
        res = self.find_overlapping(x0 - dist, y0 - dist, x0 + dist, y0 + dist)
        res = filter(lambda x: not x in self.foreignObjects.values() and self.type(x) == "image", res)
        ret = None
        if(len(res) > 0):
            ret = res[0]
        return ret

    def cleanExtra(self):
        self.delete(self.rBase, self.hdelimiter, self.vdelimiter)

    def reset(self):
        self.wbCurrentText = None
        self.wbCurrentObject = None
        self.pointList = []
        objects = self.find_all()
        for i in range(0, len(objects)):
            self.delete(objects[i])
        self.rBase = self.create_rectangle(0, 0, 0, 0)
        self.itemconfig(self.rBase, tags=(RECTANGLE,))
        self.hdelimiter = self.create_line(0, 500, 700, 500, fill="black", width=1, dash=10)
        self.vdelimiter = self.create_line(700, 0, 700, 500, fill="black", width=1, dash=10)
        self.itemconfig(self.hdelimiter, tags=(DASH,))
        self.itemconfig(self.vdelimiter, tags=(DASH,))
        self.foreignObjects = {"1":self.rBase, "2":self.hdelimiter, "3":self.vdelimiter}
        self.selectedItems = []
        self.selectionBox = None
        self.clipboard.clipboardEmpty()
        self.dx = 0
        self.dy = 0
#        self.mode = self.RW
        self.img = None

#     def insertChar(self, idTextBox, c):
#         insert(item,index,text)
#         """
#         Inserta un caracter al final del TextBox con id idTextBox
#         """
#         c = unicode(c, "utf-8")
#         old = self.itemcget(idTextBox, "text")
#         print old.encode("utf-8")
#         self.itemconfig(idTextBox, text=old + c)
