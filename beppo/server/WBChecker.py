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

from twisted.cred.checkers import ICredentialsChecker
from zope import interface
from twisted.internet import defer, reactor
from twisted.python import failure, components
from twisted.cred import error, credentials
#from twisted.enterprise import adbapi
from mx.DateTime import now
from DBConnect import DBConnect
from beppo.Constants import TUTOR, PUPIL

class WBChecker:
        interface.implements(ICredentialsChecker)
        credentialInterfaces = (credentials.IUsernamePassword,
        credentials.IUsernameHashedPassword)

        def __init__(self, logged):
            """Inicializa la conexion con la base de datos
            """
            self.logged = logged
            self.db = DBConnect()

        def stop(self):
            """Termina la conexion con la base de datos
            """
            self.db.close()

        def _checkUser(self, credentials):
            """Consulta en la base de datos por el usuario  de credentials
            """
            query = "select id, username, password, kind from person where username = '%s'" % credentials.username
            d = self.db.db.runQuery(query)
            d.addCallback(self.checkValidUser, credentials)
            return d

        def _passMatches(self, matches, avatarId):
            """Chequea matches (que lo devuelve checkPassword),
            para devolver el avatarId (que corresponde con el id del usuario)
            o levantar un error
            """
            if matches:
                if str(avatarId) in self.logged.keys():
                    return failure.Failure(error.UnauthorizedLogin())
                else:
                    return avatarId
            else:
                return failure.Failure(error.UnauthorizedLogin())

        def checkValidUser(self, result, credentials):
            """Toma el resultado de una consulta y una credencial y
            chequea si el password de la credencial coincide con el
            de la consulta (a traves de checkPassword)
            """
            if len(result) > 0:
                d = self._checkKind(result[0][0], result[0][3])
                d.addCallback(self._checkPassword, credentials, result)
                return d
            else: #no autorizado (failure se come un comentario del error)
                return failure.Failure(error.UnauthorizedLogin())


        def requestAvatarId(self, credentials):
            """Chequea con una credential por un usuario
            """
            print "intentando chequear:", credentials.username
            d = self._checkUser(credentials)
            return d

        def _checkKind(self, avatarId, kind):
            if kind == TUTOR:
                d = defer.maybeDeferred(lambda: True)
            elif kind == PUPIL:
                query = "select expires from pupil where id = %d" % avatarId
                d = self.db.db.runQuery(query)
                d.addCallback(lambda res: res[0][0] >= now())
            else:
                d = defer.maybeDeferred(lambda: False)
            return d

        def _checkPassword(self, kindPass, credentials, result):
            if kindPass:
                d = defer.maybeDeferred(credentials.checkPassword, result[0][2])
                d.addCallback(self._passMatches, result[0][0])
                return d
            else:
                return failure.Failure(error.UnauthorizedLogin())

#aparentemente, para que pueda usarse con la adaptacion a zope de python
components.backwardsCompatImplements(WBChecker)
