from beppo.Constants import TUTOR, PUPIL
from beppo.Constants import EXPIRE_TIME
from beppo.Constants import DEMO_AI, DEMO_PC
from twisted.python import failure
from mx import DateTime
from twisted.trial.util import deferredResult, deferredError
import sha

class DemoMaker(object):
    def __init__(self, username, tipo, connection):
        self.db = connection
        self.username = username
        self.tipo = tipo
    def createDemo(self):
        self.pas = sha.new('demo').hexdigest()
        query = "insert into person (kind, username, password, first_name, last_name, email, language, fk_timezone, demo) \
         values (%i, %s, %s, %s, 'demo', 'demo@demo.org', 1, 2, True)" 
       
        d = self.db.db.runOperation(query, (self.tipo, self.username,self.pas,self.username))
        d.addErrback(self.printError)
        
        query = "select id from person where username = %s"
        d.addCallback(lambda a: self.db.db.runQuery(query, (self.username,)))
        
       
        if self.tipo == TUTOR:
            d.addCallback(self.insertTutor)
        elif self.tipo == PUPIL:
            d.addCallback(self.insertPupil)
            
        return d

    def insertPupil(self, row):
        assert(len(row) == 1)
        id_user = row[0][0]
        #genero un cliente ficticio con el mismo id del alumno
        #VER!
        d = self.db.db.runOperation("insert into client (id, organization, ai_available ,pc_available) values (%d, %s, %f, %f)", (id_user, self.username, DEMO_AI, DEMO_PC)) 
        d.addErrback(self.printError)
        
        #genero el insert del alumno
        expire_time = DateTime.now() + DateTime.RelativeDate(**EXPIRE_TIME)
        d.addCallback(lambda a:self.db.db.runOperation("insert into pupil (id, fk_client, expires, ai_total, ai_available, pc_available, pc_total) values (%d, %d, '%s', %f, %f, %f, %f)", (id_user, id_user, expire_time, DEMO_AI, DEMO_AI, DEMO_PC, DEMO_PC)))
        d.addCallback (lambda a: id_user)
        return d

    def insertTutor(self, row):
        assert(len(row) == 1)
        self.id_user = row[0][0]
        
        #inserto el tutor. 
        d = self.db.db.runOperation("insert into tutor (id) VALUES (%d)", (self.id_user,)) 
        
        #asigno semana completa para el tutor
        d.addCallback(lambda a: self.db.db.runOperation("insert into tutor_schedule (fk_tutor, time_start, time_end, schedule_type) values (%d, %s, %s, 1)", (self.id_user, '2007-10-01 00:00:00', '2007-10-08 00:00:00',)))
        
        #asigno todas las materias existentes para el tutor. 
        d.addCallback(lambda a: self.db.db.runOperation("INSERT INTO tutor_subject (fk_subject,fk_tutor) (SELECT id, %d FROM subject)", (self.id_user,)))
        d.addCallback (lambda a: self.id_user)
        return d

    def printError(self, failure):
        """Imprime el error de failure"""
        print failure.getErrorMessage()
