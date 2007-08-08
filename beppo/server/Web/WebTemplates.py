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

from beppo.Constants import TUTOR, ADMIN, CLIENT, PUPIL
from WebGetUserInfo import WebGetUserInfo
from beppo.server.DBConnect import DBConnect
from mx import DateTime
from twisted.internet import defer

class WebTemplates:
    def __init__(self, title=''):
        self.title = title

    def headers(self, session, title='', header=''):
        if title == '':
            title = self.title
        return """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
 "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <title>%s</title>
    <link href="/static/stylesheet.css" type="text/css" rel="stylesheet" />
    %s
  </head>
  <body>
""" % (title, header)

    def banner(self, session):
        return """
<div id="banner">

<div id="header">
  <a id="logo" href="http://localhost:8000/"><img src="/static/graphics/beppo_banner.png"
      width="400" height="48"
      alt="Beppo" /></a>
  <hr />
</div>
"""

    def navbar(self, session):
        """ devuelve la barra de navegacion, de acuerdo al tipo
            de usuario que sea
        """
        _ = session._
        links = [{'users': [ADMIN, CLIENT, TUTOR, PUPIL], 'class': '', \
                  'desc': _('Cerrar sesion'), 'link':  '/logout', 'id': 'logout'},
                 {'users': [ADMIN, CLIENT, TUTOR, PUPIL], 'class': '', \
                  'desc': _('Inicio'), 'link':  '/', 'id': 'home'},
                 {'users': [ADMIN, CLIENT, TUTOR, PUPIL], 'class': '', \
                  'desc': _('Preferencias'), 'link': '/settings', 'id': 'settings'},
                 {'users': [TUTOR], 'class': '', 'desc': _('Mis horarios'), \
                  'link': '/schedules', 'id': 'schedules'},
                 {'users': [TUTOR], 'class': '', 'desc': _('Mis materias'), \
                  'link': '/subjects', 'id': 'subjects'},
                 {'users': [TUTOR], 'class': '', 'desc': _('Mis sesiones'), \
                  'link': '/tutor_sessions', 'id': 'tutor_sessions'},
                 {'users': [CLIENT], 'class': '', 'desc': _('Agregar alumnos'), \
                  'link': '/new_pupil', 'id': 'new_pupil'},
                 {'users': [CLIENT], 'class': '', 'desc': _('Reportes'), \
                  'link': '/report', 'id': 'report'},
                 {'users': [PUPIL], 'class': '', 'desc': _('Precoordinar una clase'), \
                  'link': '/pc_arrange', 'id': 'pc_arrange'},
                 {'users': [ADMIN], 'class': '', 'desc': _('Administrar'), \
                  'link': '/admin', 'id': 'admin'},
                 {'users': [ADMIN, CLIENT, TUTOR, PUPIL], 'class': '', \
                  'desc': _('Contactenos'), 'link': '/mail', 'id': 'mail'}]
        navbar = '<div id="metanav" class="nav">\n<h2>' + \
           _('Navegacion') + '</h2>\n<ul>'

        if hasattr(session, 'username'):
            navbar += '<li class="first">' + _('Sesion iniciada como %s') % \
                session.username + '</li>\n'
            # agregamos los links que necesiten de username
            links = links + [{'users': [ADMIN, CLIENT, TUTOR, PUPIL], 'class': '', \
                  'desc': _('Datos personales'), 'link':'/userinfo?user_id=%s&amp;kind=%s' \
                   % (session.userId, session.kind), 'id': 'userinfo'}]
            for link in links:
                if session.kind in link['users']:
                    cl = link['class']
                    desc = link['desc']
                    ref = link['link']
                    ident = link['id']
                    navbar += '<li class="%s"><a href="%s" id="%s">%s</a></li>\n' % \
                      (cl, ref, ident, desc)
        else:
            navbar += '<li class="first"><a href="/login" id="login">' + \
                  _('Iniciar sesion') + '</a></li>\n'
        navbar += '<li class="last"><a href="/help" id="help">' + \
                  _('Ayuda/Instrucciones') + '</a></li>\n' + \
                  '</ul>\n</div></div>\n'
        return navbar


    def footer(self, session):
        """Imprime el pie de pagina"""
        return """
<div id="footer">
 <hr />
 <a id="exceptpowered" href="http://www.except.com.ar/">
<img src="/static/graphics/except_logo_mini.png" height="30" width="70"
alt="Except Powered" /></a>
</div>

 </body>
</html>
"""

    def startPage(self, session, title=''):
        """Imprime todo hasta donde empieza el contenido de la pagina"""
        return self.headers(session, title=title) + self.banner(session) + self.navbar(session) + """
<div id="content">
"""

    def startPageWithHeader(self, session, header, title=''):
        """Imprime todo para el comienzo de la página. Agregando además header
        """
        return self.headers(session, title=title, header = header) + \
            self.banner(session) + self.navbar(session) + """
<div id="content">
"""

    def finishPage(self, session):
        """ Cierra el div de contenido, muestra el pie de pagina"""
        return '\n</div>\n' + self.footer(session)

    def notAuthenticated(self, session):
        """ Informar al usuario que se debe autenticar """
        _ = session._
        return '<div class="error">\n<h2>' + _('Usuario no autenticado') \
            + '</h2>' + _('Esta intentando acceder a una pagina restringida.') \
            + '<br />' + _('Debe autenticarse ante el sistema antes de acceder a esta pagina.') \
            + '</div>\n'

    def notAuthorized(self, session):
        """ Este tipo de usuario no puede acceder a esta acción"""
        _ = session._
        return '<div class="error">\n<h2>' + _('No autorizado') + \
           '</h2>\n' + _('Usted no esta autorizado a utilizar esta pagina.') \
           + '</div>'

    def unexpectedArguments(self, session, msg=''):
        """ Se recibieron parámetros en la URL que no se esperaban"""
        _ = session._
        return '<div class="error">\n<h2>' + _('No juegues con la URL') + \
            '</h2>\n' + _('Se recibieron parametros inesperados en la URL: ') \
            + '%s</div>' % msg

    def serverError(self, session, msg=''):
        """ Error en el servidor """
        _ = session._
        return '<div class="error">\n<h2>' + _('Error en el servidor') + \
            '</h2>\n' + _('Ha ocurrido un error en el servidor: ') \
            + '%s</div>' % msg

    def homePageContent(self, session):
        """Devuelve el contenido de la pagina principal del usuario
        """
        _ = session._
        content = '<h1>' + _('La pagina de %s %s') % \
            (session.name, session.lastname) + '</h1>\n'
        if session.kind == ADMIN: #root
            content += '<p>' + _('Usted es el administrador de este sitio') + '</p>'
            d = defer.maybeDeferred(lambda: content)
        elif session.kind == TUTOR:
            # si es tutor, se imprimen las clases precoordinadas que tenga arregladas
            info = WebGetUserInfo(DBConnect(), session)
            now = DateTime.now()
            d = info.getPAFromTutor(session.userId, now)
        elif session.kind in [PUPIL, CLIENT]:
            # si es alumno o cliente, se imprimen las horas disponibles (de ai y pc)
            info = WebGetUserInfo(DBConnect(), session)
            d = info.getHours(session.kind, session.userId)
        else:
            content += '<p>' + _('Aqui se muestra alguna informacion general como horas disponibles u horarios en los que se tienen clases, y algunos links utiles.  Por ejemplo, se puede ver la lista de') + ' <a href="/roominfo/">' + \
            _('salas disponibles.') + '</a>' + ' ' + _('o las') + ' ' + \
            '<a href="/static/Paginas/Tarifas.html">' + \
            _('Tarifas actuales') + '</a></p>'
            d = defer.maybeDeferred(lambda: content)
        return d

    def notFound(self, session):
        _ = session._
        return '<div class="error">\n<h2>404 - PageNotFound</h2>\n' + \
            _('La pagina solicitada no existe') + '</div>'

    def commonInfo(self, trans):
        """ Texto comun a todos los usuarios """
        _ = trans
        page = '<p><a href="/archive" id="archive">' + _('Aqui') + ' ' + '</a>' \
               + _('podra acceder a nuestro archivo, el cual consiste de las pizarras virtuales en formato PDF (Portable Document Format). Puede consultar todas las clases que nuestros tutores han dado en el sistema.') + '</p>'
        page += '<p><a href="/roominfo" id="roominfo">' + _('Aqui') + ' ' + '</a>' \
               + _('se pueden ver la lista de aulas abiertas; es decir, aquellas en las que se estan dando clase en este momento. Tambien se incluyen las materias que se estan ofreciendo, la cantidad de alumnos en clase y los tutores a cargo') + '</p>'
        return page
