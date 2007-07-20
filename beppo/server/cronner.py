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

from time import localtime, mktime, time
from twisted.internet import reactor
from twisted.python import log


# Un CronJob es una clase que tiene los siguientes métodos / atributos:
#     getTime() - devuelve la hora a la que corresponde ejecutarlo,
#               en segundos desde el epoch (float)
#     cachedTime - atributo definido sólo después de ejecutar getTime,
#                     devuelve el último valor computado por getTime
#     run() - Ejecuta la tarea correspondiente

#   Probablemente se prefiera subclassear HourlyCronJob o
#   MultiHourlyCronJob, y simplemente redefinir run.

class HourlyCronJob:
    """ Un CronJob que corre una vez por hora a cierto minuto"""
    def getTime(self):
        t = localtime()
        next = self.minute + 60 * (t[4] >= self.minute)
        t2 = t[:4] + (next,0) + t[6:]
        self.cachedTime = mktime(t2)
        return self.cachedTime

    def run(self):
        pass

    def __init__(self, minute=0):
        self.minute = minute


class MultiHourlyCronJob:
    """ Un CronJob que corre varias veces por hora, a ciertos minutos"""

    def getTime(self):
        t = localtime()
        missing = filter(lambda x: x > t[4], self.minutes)
        next = len(missing) > 0 and missing[0] or (60 + self.minutes[0])
        t2 = t[:4] + (next,0) + t[6:]
        self.cachedTime = mktime(t2)
        return self.cachedTime

    def run(self):
        pass

    def __init__(self, minutes=[0]):
        self.minutes = minutes
        self.minutes.sort()
    

class Cronner:
    """ Administra una lista de CronJobs y los va ejecutando."""

    RESOLUTION = 60 # La mínima resolución del sistema, en segundos

    def __init__(self):
        self.jobs = {} # Diccionario de jobs indexado por jobId
        self.call = None # El IDelayedCall actual
        self.comingUp = [] # Lista de CronJobs que serán ejecutados proximamente
        self.currJobId = 0

    def missingTime(self, t):
        return t - time()

    def addJob(self, job):
        self.currJobId += 1
        self.jobs[str(self.currJobId)] = job
        if self.call is None:
            self.nextCall()
        elif job.getTime() < self.call.getTime() + self.RESOLUTION:
            self.call.cancel()
            self.nextCall()
        return self.currJobId

    def removeJob(self, jobId):
        job = self.jobs.pop(str(jobId), None)
        if job is None:
            return
        if job in self.comingUp:
            self.comingUp.remove(job)
        
    def nextCall(self):
        if len(self.jobs) == 0:
            self.call = None
            self.comingUp = []
            return
        next_time = min([job.getTime() for job in self.jobs.values()])
        self.comingUp = [job for job in self.jobs.values()
                         if job.cachedTime < next_time + self.RESOLUTION]
        self.call = reactor.callLater(self.missingTime(next_time), self.runJobs)

    def runJobs(self):
        for job in self.comingUp:
            job.run()
        self.nextCall()

    def stop(self):
        if self.call is not None:
            self.call.cancel()
            self.call = None
            self.comingUp = []
