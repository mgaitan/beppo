# -*- coding: UTF-8 -*-
from twisted.internet import reactor
from cronner import HourlyCronJob, MultiHourlyCronJob
from twisted.python import log

class ClassRoomClosingTimeNotifier(MultiHourlyCronJob):
    def __init__(self, server):
        MultiHourlyCronJob.__init__(self, minutes=[0,5,10,15,20,25,30, 32, 33,37,40,45,50,55])
        self.server = server
    def run(self):
        # Muy Chancho, pero es la idea
        for room in self.server.wbRooms.values():
            self.server.signalEndingClass(room.wbTutor)



class PointlessLogger(MultiHourlyCronJob):
    def __init__(self):
        MultiHourlyCronJob.__init__(self, range(60))
    def run(self):
        log.msg("""

#######################################################################
#######################################################################
###                                                                 ###
### Aviso importante:                                               ###
###    Intente reducir el tamanio de los logs.  Estudios recientes  ###
###    muestran que llevar logs de tamanio excesivo en una          ###
###    aplicacion pueden llevar a una degradacion significativa en  ###
###    la performance del sistema.                                  ###
###                                                                 ###
###    Y recuerde... cada byte cuenta!                              ###
###                                                                 ###
#######################################################################
#######################################################################

""")
