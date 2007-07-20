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

from twisted.internet import reactor, defer
from twisted.spread import pb
from twisted.cred import portal
from PupilAvatar import Pupil
from TutorAvatar import Tutor
from DBConnect import DBConnect
from beppo.Constants import TUTOR, PUPIL

class WBRealm:
    __implements__ = portal.IRealm
    def __init__(self):
        self.db = DBConnect()

    def requestAvatar(self, avatarId, mind, *interfaces):
        assert pb.IPerspective in interfaces
        d = self._getUserKind(avatarId)
        d.addCallback(self._generateAvatar, avatarId, mind)
        return d

    def _generateAvatar(self, result, avatarId, mind):
        if len(result) > 0:
            kind = result[0][0]
            if kind == TUTOR:
                avatar = Tutor(avatarId, self.server)
            elif kind == PUPIL:
                avatar = Pupil(avatarId, self.server)
            avatar.attached(mind)
            self.server.addClient(avatar, str(avatarId))
        return pb.IPerspective, avatar, lambda a=avatar:self.server.removeClient(a)

    def _getUserKind(self, avatarId):
        query = "select kind from person where id = %d" % avatarId
        d = self.db.db.runQuery(query)
        return d
