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

from twisted.enterprise import adbapi

from beppo.settings import *

class DBConnect:
    """ Conexion a la base de datos.  Clase singleton, para que todo el mundo
        utilice sin preocuparse por la cantidad de conexiones creadas """

    # Es DSN, la Data Source Name
    DBARGS = DSN
    DBLIB = "psycopg"

    def __init__(self):
        self.db = adbapi.ConnectionPool(self.DBLIB, self.DBARGS, cp_reconnect=True)
        self.db.start()

    def close(self):
        self.db.close()

    def __call__(self):
        """ Devolvemos siempre la misma instancia """
        return self


DBConnect = DBConnect()
