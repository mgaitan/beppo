from cronjobs import PointlessLogger
from cronner import Cronner, HourlyCronJob, MultiHourlyCronJob
from twisted.application import service, internet
from twisted.web import resource, server, static
from twisted.python import log
from twisted.internet import reactor
import time

class TestCronner(Cronner):
    def nextCall(self):
        
        if len(self.jobs) == 0:
            self.call = None
            self.comingUp = []
            return
        for job in self.jobs.items():
            log.msg("\n\n>>>>>>Job %s: Next call at %s\n\n" % (job[0], time.ctime(job[1].getTime())))
        next_time = min([job.cachedTime for job in self.jobs.values()])
        self.comingUp = [job for job in self.jobs.values()
                         if job.cachedTime < next_time + self.RESOLUTION]
        self.call = reactor.callLater(self.missingTime(next_time), self.runJobs)


class TestServer:
    def __init__(self):
        self.cronner = TestCronner()
        self.cronner.addJob(HourlyCronJob())
        self.cronner.addJob(MultiHourlyCronJob(range(60)))
    def getRoot(self):
        return static.File.childNotFound

testServer = TestServer()
application = service.Application('wb')
serviceCollection = service.IServiceCollection(application)
internet.TCPServer(8000, server.Site(testServer.getRoot())).setServiceParent(serviceCollection)
