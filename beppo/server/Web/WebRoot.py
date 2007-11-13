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
from beppo.server.utils import getTranslatorFromSession
from twisted.internet import defer
from WebTemplates import WebTemplates
from WebRoomInfo import WebRoomInfo
from WebUserInfo import WebUserInfo
from WebLogin import WebLogin, WebLogout
from WebSettings import WebSettings
from WebSubjects import WebSubjects
from WebSchedules import WebSchedules
from WebSubjectAdmin import WebSubjectAdmin
from WebAdmin import WebAdmin
from WebArchive import WebArchive
from WebListUsers import WebListUsers
from WebTutor import WebTutor
from WebTutorSessions import WebTutorSessions
from WebTutorData import WebTutorData
from WebClient import WebClient
from WebClientReport import WebClientReport
from WebTutorInfo import WebTutorInfo
from WebPupilInsert import WebPupilInsert
from WebPupilEdit import WebPupilEdit
from WebPCArrange import WebPCArrangeRoot
from WebMyPupils import WebMyPupils
from WebMyPupilsInfo import WebMyPupilsInfo
from WebSendMail import WebSendMail
from WebEditAdmin import WebEditAdmin
from twisted.web import static, server
from beppo.server.DBConnect import DBConnect
from twisted.python import log

class WebRoot(Resource):
    #def __init__(self, users, openRooms, shouldBeOpenRooms):
    def __init__(self, server):
        Resource.__init__(self)
        self.db = DBConnect()
        self.template = WebTemplates()
        self.putChild("roominfo", WebRoomInfo(server))
        self.putChild("userinfo", WebUserInfo())
        self.putChild("login", WebLogin())
        self.putChild("logout", WebLogout())
        self.putChild("static",  static.File("./htdocs/"))
        self.putChild("board_archive", static.File("./archive/"))
        self.putChild("content", WebContent())
        self.putChild("calendar",  static.File("./calendar/"))
        self.putChild("subjects", WebSubjects())
        self.putChild("settings", WebSettings())
        self.putChild("subject_admin", WebSubjectAdmin())
        self.putChild("schedules", WebSchedules())
        self.putChild("admin", WebAdmin())
        self.putChild("archive", WebArchive())
        self.putChild("list", WebListUsers())
        self.putChild("tutor", WebTutor())
        self.putChild("tutor_info", WebTutorInfo())
        self.putChild("tutor_data", WebTutorData())
        self.putChild("tutor_sessions", WebTutorSessions())
        self.putChild("client", WebClient())
        self.putChild("report", WebClientReport())
        self.putChild("mail", WebSendMail())
        self.putChild("my_pupils", WebMyPupils())
        self.putChild("my_pupils_info", WebMyPupilsInfo())
        self.putChild("pupil_edit", WebPupilEdit())
        self.putChild("new_pupil", WebPupilInsert())
        self.putChild("pc_arrange", WebPCArrangeRoot())
        self.putChild("editadmin", WebEditAdmin())


    def getChild(self, path, request):
        if path in ('', 'index.html', 'index'):
            return self
        else:
            return static.File.childNotFound

    def render_GET(self, request):
        #VEEER
        #verificar borrado?
        #de aqui se puede llamar a deletePA
        keys = request.args.keys()
        print keys
        if "del" in keys:
            print "lalala" + str(request.args['del'][0])
        d = defer.maybeDeferred(getTranslatorFromSession, request)
        d.addCallback(self.writeWelcomeMessage, request)
        return server.NOT_DONE_YET

    def writeWelcomeMessage(self, trans, request):
        _ = trans
        session = request.getSession()
        request.write(self.template.startPage(session, \
            _('Beppo - Sistema de educacion a distancia')))
        d = defer.maybeDeferred(lambda: None)
        if hasattr(session, 'username'):
            d.addCallback(lambda a: self.template.homePageContent(session))
            d.addCallback(request.write)
            d.addCallback(lambda a: self.template.commonInfo(trans))
            d.addCallback(request.write)
        else:
            d.addCallback(lambda a: request.write('<h1>' + _('Bienvenido!') \
               + '</h1> <p>' + \
               _('Aqui podra conocer todas las ventajas de utilizar el sistema Beppo, y lo intentaremos convencer de que lo compre.') + '</p>'))
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return d

class WebContent(Resource):

    def __init__(self):
        Resource.__init__(self)
        self.template = WebTemplates()
        self.pages = static.File('./htdocs/content/')

    def getChild(self, path, request):
        return self


    def render_GET(self, request):
        d = defer.maybeDeferred(getTranslatorFromSession, request)
        d.addCallback(self.writeContent, request)
        return server.NOT_DONE_YET

    def writeContent(self, trans, request):
        session = request.getSession()
        _ = trans
        request.write(self.template.startPage(session, \
            _('Beppo - Sistema de educacion a distancia')))
        page = self.pages.getChild(request.prepath[-1], request)
        if hasattr(page, 'getContent'):
            request.write(page.getContent())
        else:
            request.write(self.template.notFound(session))
        request.write(self.template.finishPage(session))
        request.finish()
        return

