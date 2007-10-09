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

from time import localtime
from beppo.Constants import EXTRA_IACLASS

class WBRoom:
    def __init__(self, roomDesc, roomType, tutorStatus):
        """
        Crea el room con tutor de Id tutorId y status de pizarra tutorStatus
        """
        self.wbTutor = roomDesc[0]
        self.wbClients = [self.wbTutor]
        self.wbViewers = []
        self.wbStatus = tutorStatus
        self.waitingPupil = None
        self.wbRoomType = roomType
        self.endTime = roomDesc[1]
        self.logChat = ""

    def roomPupilCheck(self, clientId):
        """
        El alumno con Id clientId espera dentro del room
        """
        self.waitingPupil = clientId

    def roomPupilReject(self):
        """
        Rechaza al alumno que esperaba dentro del room
        """
        self.roomPupilStopWaiting()

    def roomPupilAccept(self):
        """
        Acepta y hace entrar al alumno que esperaba dentro del room
        """
        if self.waitingPupil != None:
            self.wbClients.append(self.waitingPupil)
            self.roomPupilStopWaiting()

    def roomPupilExit(self, clientId):
        """
        El alumno con Id clientId abandona el room
        """
        self.wbClients.remove(clientId)

    def roomPupilWaiting(self):
        """
        Devuelve el Id del alumno que espera dentro del room
        """
        return self.waitingPupil

    def roomPupilStopWaiting(self):
        """
        El alumno que esperaba dentro del room ya no espera
        """
        self.waitingPupil = None

    def roomPupilCurrent(self):
        """
        Devuelve el Id del alumno actual de este room
        """
        if len(self.wbClients) != 2:
            return None
        else:
            return self.wbClients[1]

    def roomListViewers(self):
        return self.wbViewers
        
    def roomListPupils(self):
        return self.wbClients

    def roomListClients(self):
        """
        Devuelve una lista de Ids de los clientes de este room
        """
        return self.wbClients + self.wbViewers

    def roomIsClosing(self):
        """
        Devuelve True si el room esta en sus ultimos 15 minutos de vida
        """
        if self.roomType() == EXTRA_IACLASS:
            return False
        y, m, d, hs, ms, ss, wd, yd, c = localtime()
        return (self.endTime.day_of_week == wd and ((self.endTime.hour == (hs + 1)%24 and self.endTime.minute == 0 and ms >= 45) or (self.endTime.hour == hs and self.endTime.minute == 30 and ms >= 15)))

    def roomIsClosed(self):
        """
        Devuelve True si el room ya alcanzo/supero su hora de cierre
        """
        if self.roomType() == EXTRA_IACLASS:
            return False
        y, m, d, hs, ms, ss, wd, yd, c = localtime()
        return (self.endTime.day_of_week == wd and (self.endTime.hour < hs or (self.endTime.hour == hs and self.endTime.minute <= ms)))

    def roomIsEmpty(self):
        return (self.waitingPupil == None and len(self.wbClients) == 1)

    def setRoomType(self, kind, endTime):
        self.wbRoomType = kind
        self.endTime = endTime

    def roomType(self):
        return self.wbRoomType
        
    def roomViewerEnter(self, clientId):
        self.wbViewers.append(clientId)

    def roomViewerExit(self, clientId):
        self.wbViewers.remove(clientId)

    def roomViewersExit(self):
        self.wbViewers = []
