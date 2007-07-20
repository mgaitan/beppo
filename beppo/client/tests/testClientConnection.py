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

from twisted.internet import reactor, error
from twisted.spread import pb
from twisted.trial import unittest
from twisted.trial.util import deferredResult
from Client import Client
from wbserver import WbServer, WBRealm
from WBChecker import WBChecker
from WBBroker import WBBroker
from twisted.cred import credentials, portal

from twisted.internet.base import DelayedCall
DelayedCall.debug = True

class testClientConnection(unittest.TestCase):

    def setUp(self):
        self.done = False
        self.cFactory = pb.PBClientFactory()
        self.realm = WBRealm()
        self.realm.server = WbServer()
        self.wbServer = self.realm.server
        self.p = portal.Portal(self.realm)
        self.c = WBChecker()
        self.p.registerChecker(self.c)
        self.sFactory = pb.PBServerFactory(self.p)
        self.sFactory.protocol = WBBroker
        self.server = reactor.listenTCP(28789, self.sFactory)

        self.myClient = Client()
        self.myClient2 = Client()
        self.client = reactor.connectTCP("localhost", 28789, self.cFactory)
        self.client2 = reactor.connectTCP("localhost", 28789, self.cFactory)
        def1 = self.cFactory.login(credentials.UsernamePassword("Waldo","waldo"), client=self.myClient.cc)
        def1.addCallback(self.getRoot, 1)
        def1.addErrback(self.failure, "Error al conectarse el cliente1")
        deferredResult(def1)

        def2 = self.cFactory.login(credentials.UsernamePassword("Matias","matias"), client=self.myClient2.cc)
        def2.addCallback(self.getRoot, 2)
        def2.addErrback(self.failure, "Error al conectarse el cliente2")
        deferredResult(def2)

    def tearDown(self):
        reactor.removeAll()
        deferredResult(self.server.stopListening())

    def testAddTextBox(self):
        deferredResult(self.myClient.wb.addTextBox(20, 20))
        self.assertEqual(self.myClient.wb.foreignObjectsCount(), 0)
        self.assertEqual(self.myClient2.wb.foreignObjectsCount(), 1)

    def testInsertChars(self):
        deferredResult(self.myClient.wb.addTextBox(20, 20))
        deferredResult(self.myClient.wb.insertChars(self.myClient.wb.wbCurrent, 0, "fooBarBaz"))
        self.assertEqual(self.myClient.wb.foreignObjectsCount(), 0)
        wb2 = self.myClient2.wb
        self.assertEqual(wb2.foreignObjectsCount(), 1)
        self.assertEqual(wb2.itemcget(wb2.foreignObjects.values()[0], "text"), "fooBarBaz")

    def testDeleteChars(self):
        deferredResult(self.myClient.wb.addTextBox(20, 20))
        deferredResult(self.myClient.wb.insertChars(self.myClient.wb.wbCurrent, 0, "fooBarBaz"))
        deferredResult(self.myClient.wb.deleteChars(self.myClient.wb.wbCurrent, 3, 4))
        self.assertEqual(self.myClient.wb.foreignObjectsCount(), 0)
        wb2 = self.myClient2.wb
        self.assertEqual(wb2.foreignObjectsCount(), 1)
        self.assertEqual(wb2.itemcget(wb2.foreignObjects.values()[0], "text"), "foorBaz")

    def failure(self, msg, who=0):
        print "error: ", msg
        self.done = True

    def getRoot(self, perspective, who):
        d = perspective.callRemote("getWbServer")
        d.addCallback(self.success, who)

    def success(self, root, who):
        if who == 1:
            self.myClient.setRoot(root)
        else:
            self.myClient2.setRoot(root)

    def localDeleteChars(self, data):
        self.myClient.wb.deleteChars(self.myClient.wb.wbCurrent, 3, 4)

    def finished(self):
        self.done = True
        try:
            self.timeout.cancel()
        except (error.AlreadyCancelled, error.AlreadyCalled):
            pass

    def testServerStatusNewText(self):
        deferredResult(self.myClient.wb.addTextBox(20, 20))
        current = self.myClient.wb.wbCurrent
        self.assert_(self.wbServer.wbStatus.has_key(self.wbServer.itemId(3, current)))

    def testServerStatusEditText(self):
        deferredResult(self.myClient.wb.addTextBox(20, 20))
        deferredResult(self.myClient.wb.insertChars(self.myClient.wb.wbCurrent, 0, "fooBarBaz"))
        current = self.myClient.wb.wbCurrent
        dict = self.wbServer.wbStatus[self.wbServer.itemId(3, current)]
        self.assertEqual(dict["text"], "fooBarBaz")
        self.assertEqual(dict["x"], 20)
        self.assertEqual(dict["y"], 20)
        self.assertEqual(dict["owner"].avId, 3)

    def testServerStatusClientConnect(self):
        dict = self.wbServer.wbStatus
        for a in dict.keys():
            self.assert_(self.myClient.wb.foreignObjects.has_key(a))

    def testServerStatusClientDisconnect(self):
        deferredResult(self.myClient.disconnect())
        self.assert_(3 not in self.wbServer.wbClients)

    def testServerStatusClientAdd(self):
        deferredResult(self.myClient.wb.addTextBox(20, 20))
        deferredResult(self.myClient.wb.insertChars(self.myClient.wb.wbCurrent, 0, "fooBarBaz"))
        ddict = self.wbServer.wbStatus
        for a in ddict.keys():
            self.assert_(self.myClient2.wb.foreignObjects.has_key(a))
            tbox = self.myClient2.wb.foreignObjects[a]
            self.assertEqual(self.myClient2.wb.itemcget(tbox, "text"),ddict[a]["text"])

    def testServerStatusClientModify(self):
        deferredResult(self.myClient.wb.addTextBox(20, 20))
        deferredResult(self.myClient.wb.insertChars(self.myClient.wb.wbCurrent, 0, "fooBarBaz"))
        deferredResult(self.myClient.wb.deleteChars(self.myClient.wb.wbCurrent, 3, 5))
        current = self.myClient.wb.wbCurrent
        ddict = self.wbServer.wbStatus[self.wbServer.itemId(3, current)]
        self.assertEqual(self.myClient.wb.itemcget(current, "text"), "fooBaz")
        self.assertEqual(ddict["text"], "fooBaz")
        self.assertEqual(ddict["x"], 20)
        self.assertEqual(ddict["y"], 20)

