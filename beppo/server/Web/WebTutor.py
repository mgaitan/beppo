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
from WebTemplates import WebTemplates
from twisted.web import static, server
from twisted.internet import defer
from twisted.python import log, failure
from beppo.Constants import TUTOR
from WebPerson import WebPerson
from beppo.server.utils import getTranslatorFromSession, dummyTranslator
from beppo.server.DBConnect import DBConnect

class WebTutor(WebPerson):
    _ = dummyTranslator
    fields = [{'name': 'address1', 'pos': 6, 'desc': _('Direccion 1'), 'required': True, 'isPass': False, 'maxlength': 255, 'query': "tutor"},
    {'name': 'address2', 'pos': 7, 'desc': _('Direccion 2'), 'required': False, \
     'isPass': False, 'maxlength': 255, 'query': "tutor"},
    {'name': 'zip', 'pos': 8, 'desc': _('Codigo postal'), 'required': False, \
     'isPass': False, 'maxlength': 80, 'query': "tutor"},
    {'name': 'phone1', 'pos': 9, 'desc': _('Telefono 1'), 'required': True, \
     'isPass': False, 'maxlength': 255, 'query': "tutor"},
     {'name': 'phone2', 'pos': 10, 'desc': _('Telefono 2'), 'required': False, \
      'isPass': False, 'maxlength': 255, 'query': "tutor"},
     {'name': 'phone3', 'pos': 11, 'desc': _('Telefono 3'), 'required': False, \
      'isPass': False, 'maxlength': 255, 'query': "tutor"},
     {'name': 'icq', 'pos': 12, 'desc': _('ICQ'), 'required': False, \
      'isPass': False, 'maxlength': 255, 'query': "tutor"},
     {'name': 'msn', 'pos': 13, 'desc': _('MSN'), 'required': False, \
      'isPass': False, 'maxlength': 255, 'query': "tutor"},
     {'name': 'aol', 'pos': 14, 'desc': _('Aol'), 'required': False, \
     'isPass': False, 'maxlength': 255, 'query': "tutor"}]
    query = "select person.id, username, password, first_name, \
            last_name, email, address1, address2, zip, phone1, \
            phone2, phone3, icq, msn, aol from person, tutor \
            where person.id = tutor.id and person.id = %s"

    def __init__(self):
        _ = dummyTranslator
        WebPerson.__init__(self, "tutor", _('Pagina del tutor'), TUTOR, WebTutor.query, 15, WebTutor.fields)
