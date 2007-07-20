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

from twisted.internet import defer, reactor
from twisted.python import failure
from twisted.cred import error, credentials
from twisted.trial import unittest
from twisted.trial.util import deferredResult, deferredError

from WBChecker import WBChecker

class testWBChecker(unittest.TestCase):
    def setUp(self):
        self.checker = WBChecker()
        self.credential = credentials.UsernamePassword("Mati", "mati")
        self.credential2 = credentials.UsernamePassword("Mati", "bordgl")
        self.credential3 = credentials.UsernamePassword("Waldo", "waldo")
        #reactor.run()

    def tearDown(self):
        self.checker.stop()

    def testGetValidUser(self):
        d = self.checker.requestAvatarId(self.credential)
        e = self.checker.requestAvatarId(self.credential2)
        f = self.checker.requestAvatarId(self.credential3)
        deferredResult(d)
        deferredError(e)
        deferredResult(f)

#     def error(self, res):
#         print "Error!!:", res
