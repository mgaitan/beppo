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

from twisted.trial import unittest
from WBRoom import WBRoom

class testWBRoom(unittest.TestCase):
    def setUp(self):
        self.room = WBRoom()

    #def tearDown(self):

    def testCreate(self):
        self.assertEqual(self.room.statusGetKeys(), [])
        self.assertEqual(self.room.clientsGetIds(), [])

    def testClientsAdd(self):
        self.room.clientsAdd(3)
        self.room.clientsAdd(4)
        self.assert_(3 in self.room.clientsGetIds())
        self.assert_(4 in self.room.clientsGetIds())
        self.assert_(2 not in self.room.clientsGetIds())

    def testClientsRemove(self):
        self.room.clientsAdd(3)
        self.room.clientsAdd(4)
        self.room.clientsRemove(3)
        self.assert_(3 not in self.room.clientsGetIds())
        self.assert_(4 in self.room.clientsGetIds())

    def testAddTextBox(self):
        self.room.statusAddTextBox(boxId=1, x=3, y=4, owner=4)
        self.room.statusSetField(1, "text", "waldo")
        self.assertEqual(self.room.statusGetField(boxId=1, field="text"), "waldo")
        self.assertEqual(self.room.statusGetField(boxId=1, field="x"), 3)
        self.assertEqual(self.room.statusGetField(boxId=1, field="y"), 4)
        self.assertEqual(self.room.statusGetField(boxId=1, field="owner"), 4)

    def testStatusGetKeys(self):
        self.room.statusAddTextBox(boxId=1, x=3, y=4, owner=4)
        self.assert_(1 in self.room.statusGetKeys())
        self.assert_(2 not in self.room.statusGetKeys())
