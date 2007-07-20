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

from twisted.web.resource import Resource
from twisted.web import static, server
from twisted.enterprise import adbapi
from twisted.internet import defer
from beppo.server.DBConnect import DBConnect
from WebTemplates import WebTemplates
from beppo.server.utils import getTranslatorFromSession, dummyTranslator
from beppo.server.utils import timezoneToString
from beppo.Constants import CLIENT, PUPIL, ADMIN, TUTOR

class DBDelete:
    # Clase para el borrado de la base de datos de los usuarios y materias
    # Lo que se debe hacer es:
    # pupil -> archive(a 0 los fk_session tq en session tengan fk_pupil),
    #          pre_archive(a 0 los fk_session tq en session tengan fk_pupil),
    #          borrar session(fk_pupil), borrar offline_questions(fk_pupil),
    #          borrar pupil(id), borrar person(id)
    # tutor -> archive(a 0 los fk_session tq en session tengan fk_tutor),
    #          pre_archive(a 0 los fk_session tq en session tengan fk_tutor),
    #          borrar session(fk_tutor), borrar tutor_schedule(fk_tutor),
    #          borrar tutor_subjects(fk_tutor), borrar tutor(id),
    #          borrar person(id)
    # client -> pupil(llamar para todos los alumnos del clietne),
    #           borrar client(id), borrar person(id)
    # subject -> borrar solo si no hay referencias
    #            en offline_questions y prearranged_classes

    def __init__(self, db):
        self.db = db

    def _tableFromId(self, table):
        return "delete from " + table + " where id = %s"

    def _sessionTutor(self):
        return "delete from session where fk_tutor = %s"

    def _sessionPupil(self):
        return "update session set fk_pupil = null where fk_pupil = %s"

    def _offlineQuestions(self):
        return "delete from offline_questions where fk_pupil = %s"

    def _tableFromFkTutor(self, table):
        return "delete from " + table + " where fk_tutor = %s"

    def _archiveFromUser(self, user):
        return "update archive set fk_session = null where fk_session in \
                (select id from session where fk_" + user + " = %s)"

    def _pre_archiveFromUser(self, user):
        return "update pre_archive set fk_session = null where fk_session in \
                (select id from session where fk_" + user + " = %s)"

    def _getPupils(self):
        return "select id from pupil where fk_client = %s"

    def _subjectInTable(self, table):
        return "select fk_subject from " + table + " where fk_subject = %s"

    def _subjectFromId(self):
        return "delete from subject where id = %s"

    def deletePupil(self, id):
        """Borra el alumno id, actualizando y borrando las tablas que hacen falta"""
        d = self.db.db.runOperation(self._archiveFromUser("pupil"), (id,))
        d.addCallback(lambda a: self.db.db.runOperation(self._pre_archiveFromUser("pupil"), (id,)))
        d.addCallback(lambda a: self.db.db.runOperation(self._sessionPupil(), (id,)))
        d.addCallback(lambda a: self.db.db.runOperation(self._offlineQuestions(), (id,)))
        d.addCallback(lambda a: self.db.db.runOperation(self._tableFromId("pupil"), (id,)))
        d.addCallback(lambda a: self.db.db.runOperation(self._tableFromId("person"), (id,)))
        return d

    def deleteTutor(self, id):
        """Borra el tutor id, actualizando y borrando las tablas que hacen falta"""
        d = self.db.db.runOperation(self._tableFromFkTutor("tutor_schedule"), (id,))
        d.addCallback(lambda a: self.db.db.runOperation(self._tableFromFkTutor("tutor_subject"), (id,)))
        d.addCallback(lambda a: self.db.db.runOperation(self._archiveFromUser("tutor"), (id,)))
        d.addCallback(lambda a: self.db.db.runOperation(self._pre_archiveFromUser("tutor"), (id,)))
        d.addCallback(lambda a: self.db.db.runOperation(self._sessionTutor(), (id,)))
        d.addCallback(lambda a: self.db.db.runOperation(self._tableFromId("tutor"), (id,)))
        d.addCallback(lambda a: self.db.db.runOperation(self._tableFromId("person"), (id,)))
        return d

    def _deletePupils(self, rows):
        """Toma el resultado de una consulta y manda a borrar a todos los alumnos
           de la consulta
        """
        d = defer.maybeDeferred(lambda: None)
        for pupil in rows:
            d.addCallback(lambda a: self.deletePupil(str(pupil[0])))
        return d

    def deleteClient(self, id):
        """Borra el cliente id, y todos sus alumnos"""
        d = self.db.db.runQuery(self._getPupils(), (id,))
        d.addCallback(self._deletePupils)
        d.addCallback(lambda a: self.db.db.runOperation(self._tableFromId("client"), (id,)))
        d.addCallback(lambda a: self.db.db.runOperation(self._tableFromId("person"), (id,)))
        return d

    def deletePerson(self, id, kind):
        """Borra el usuario id de clase kind"""
        if kind == CLIENT:
            return self.deleteClient(id)
        elif kind == PUPIL:
            return self.deletePupil(id)
        elif kind == TUTOR:
            return self.deleteTutor(id)

    def deleteSubject(self, id):
        """Borra la materia id, en caso de que no tenga referencias a offline_questions
           ni a prearranged_classes
        """
        d = self.db.db.runQuery(self._subjectInTable("offline_questions"), (id,))
        d.addCallback(self._checkOfflineQuestions, id)
        return d

    def _checkOfflineQuestions(self, rows, id):
        """Recibe el resultado de una consulta (que pregunta por las referencias en
           offline_questions de la materia id) y chequea en prearranged_classes en
           caso de que la cantidad de filas sea 0 (es decir, por ahora la materia
           puede borrarse)
        """
        if len(rows) == 0:
            d = self.db.db.runQuery(self._subjectInTable("prearranged_classes"), (id,))
            d.addCallback(self._checkPrearrangedClasses, id)
        else:
            d = defer.maybeDeferred(lambda: False)
        return d

    def _checkPrearrangedClasses(self, rows, id):
        """Recibe el resultado de una consulta (que chequea la existencia de una
           materia en offline_questions) y la borra en caso de poder. Caso contrario
           devuelve False
        """
        if len(rows) == 0:
            d = self.db.db.runOperation(self._subjectFromId(), (id,))
        else:
            d = defer.maybeDeferred(lambda: False)
        return d
