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
from WBQueuer import WBQueuer
from Constants import GENERAL

class testWBQueuer(unittest.TestCase):
    def setUp(self):
        self.queues = WBQueuer()
        self.queues.addQueue("1")

    def testCreate(self):
        self.failUnless(self.queues.isEmpty(GENERAL))
        self.failUnless(self.queues.isEmpty("1"))
        self.assert_(len(self.queues.roomList()) == 2)

    def testEnqueue(self):
        self.queues.enterQueue("1", "6")
        self.assert_(self.queues.lenQueue("1") == 1)
        self.assert_(self.queues.firstInQueue("1") == "6")

    def testDequeue(self):
        self.queues.enterQueue("1", "6")
        self.queues.enterQueue("1", "9")
        self.assert_(self.queues.lenQueue("1") == 2)
        self.queues.leaveQueue("1", "6")
        self.assert_(self.queues.lenQueue("1") == 1)
        self.assert_(self.queues.firstInQueue("1") == "9")

    def testFirst(self):
        self.queues.enterQueue(GENERAL, "6")
        self.queues.enterQueue(GENERAL, "9")
        self.assert_(self.queues.lenQueue(GENERAL) == 2)
        first = self.queues.popQueue(GENERAL)
        self.assert_(first == "6")
        self.assert_(self.queues.lenQueue(GENERAL) == 1)
        self.assert_(self.queues.firstInQueue(GENERAL) == "9")

    def testInQueue(self):
        self.queues.enterQueue(GENERAL, "6")
        self.queues.enterQueue(GENERAL, "9")
        self.failUnless(self.queues.isClientInQueue(GENERAL, "9"))
        self.failIf(self.queues.isClientInQueue("1", "6"))

    def testNextClient(self):
        self.queues.addQueue("2")
        self.queues.enterQueue("1", "6")
        self.queues.enterQueue(GENERAL, "9")
        self.assert_(self.queues.whoIsNext("1") == "6")
        self.assert_(self.queues.whoIsNext("2") == "9")

