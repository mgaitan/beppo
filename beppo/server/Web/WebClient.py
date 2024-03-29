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
from beppo.Constants import TUTOR, ADMIN, CLIENT
from WebPerson import WebPerson
from beppo.server.utils import getTranslatorFromSession, dummyTranslator
from beppo.server.DBConnect import DBConnect

class WebClient(WebPerson):
    _ = dummyTranslator
    fields = [{'name': 'organization', 'pos': 6, 'desc': _('Organizacion'), \
         'required': True, 'isPass': False, 'maxlength': 255, 'query': "client"}]
    query = "select person.id, username, password, first_name, \
                last_name, email, organization from person, client \
                where person.id = client.id and person.id = %s"

    def __init__(self):
        _ = dummyTranslator
        WebPerson.__init__(self, "client", _('Pagina del cliente'), CLIENT, WebClient.query, 7, WebClient.fields)
