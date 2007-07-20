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
from twisted.internet import defer
from WebTemplates import WebTemplates
from beppo.server.DBConnect import DBConnect
from twisted.python import log, failure
from mx.DateTime import DateTime
from psycopg import QuotedString
from beppo.server.utils import getTranslatorFromSession
from beppo.server.DBConnect import DBConnect
from beppo.Constants import MAIL_HOST, MAIL_PORT, MAIL_TO, MAIL_FROM
#para el mail
import re
import smtplib
from email.MIMEText import MIMEText
from email.Header import Header

class WebSendMail(Resource):
    fields = [{'name': 'subject', 'maxlength': 255},
        {'name': 'body', 'maxlength': 64000},
        {'name': 'username', 'maxlength': 255},
        {'name': 'user_id', 'maxlength': 255}]

    def __init__(self):
        self.db = DBConnect()
        self.template = WebTemplates()
        self.render_POST = self.render_GET
        Resource.__init__(self)

    def getChild(self, path, request):
        if path == "":
            return self
        else:
            return static.File.childNotFound

    #Formulario para mandar mail con sugerencias, bugs, etc
    def render_GET(self, request):
        d = defer.maybeDeferred(getTranslatorFromSession, request)
        d.addCallback(self.doAuthentication, request)
        return server.NOT_DONE_YET

    def doAuthentication(self, trans, request):
        session = request.getSession()
        _ = trans
        # 0) Se empieza la página
        request.write(self.template.startPage(session, _('Criticas y sugerencias')))
        d = defer.maybeDeferred(lambda:None)
        # 1) Verificar que esté autenticado ante el sistema
        msg = """<h2>""" + _('Criticas y sugerencias') + """</h2>""" \
            + _('Desde aqui puede mandar sus criticas, sugerencias y comentarios.') + " " \
            + _('La comunicacion se realizara mediante la casilla de mail con la cual se ha registrado.')
        if not hasattr(session, 'username'):
            request.write(self.template.notAuthenticated(session))
        else:
        # La función que procesa e imprime el contenido de la pagina
            self.printContent(request, d, msg)
        # 2) Se termina la página
        d.addCallback(lambda a: request.write(self.template.finishPage(session)))
        d.addCallback(lambda a: request.finish())
        return d

    def checkRequest(self, d, request):
        session = request.getSession()
        _ = session._
        args = dict([(i, request.args[i][0]) for i in request.args.keys()])
        if "submit" in request.args.keys():
            for value in self.fields:
                if value['name'] not in args.keys():
                    args[value['name']] = ''
                    d.addCallback(lambda a: \
                        request.write(self.template.unexpectedArguments(session, \
                        _('Falta el argumento \'%s\'') % value['name'])))
                elif len(args[value['name']]) > value['maxlength']:
                    args[value['name']] = args[value['name']][:value['maxlength']]
                    d.addCallback(lambda a: \
                        request.write(self.template.unexpectedArguments(session, \
                        _('Longitud excesiva del argumento \'%s\'') % value['name'])))
        return args

    def printContent(self, request, d, page):
        session = request.getSession()
        args = self.checkRequest(d, request)
        user_id = session.userId
        query = "select username, id, email from person where id = %d"
        d.addCallback(lambda a: self.db.db.runQuery(query, (user_id,)))
        d.addCallback(self.mail, args, request, page)
        return d

    def mail(self, rows, args, request, page):
        session = request.getSession()
        _ = session._
        if len(rows) == 1:
            if "submit" in args.keys():
                if args['body'] != "":
                    subject = "[%s][%s] %s" % (rows[0][1], rows[0][0], args['subject'])
                    msg = MIMEText(args['body'], _charset='utf-8')
                    msg['Subject'] = Header(subject, 'utf-8')
                    msg['From'] = rows[0][2]
                    msg['To'] = MAIL_TO
                    try:
                        s = smtplib.SMTP(host = MAIL_HOST, port = MAIL_PORT)
                    	s.sendmail(MAIL_FROM, [msg['To']], msg.as_string())
                    except:
                        request.write(self.template.serverError(session, \
                            _('Error al intentar establecer la comunicacion')))
                    else:
                        s.close()
                        request.write("""<div class="message"><h2>""" + \
                        _('Mail enviado correctamente') + """</h2>""" + \
                        _('Agradecemos su colaboracion') + """</div>""")
                else:
                    request.write(self.template.unexpectedArguments(session, \
                        _('El texto del mail no debe ser vacio')))
        else:
            request.write(self.template.unexpectedArguments(session, \
                        _('El usuario no existe en el sistema')))
        request.write(page)
        self.printForm(rows[0], request)

    def printForm(self, row, request):
        _ = request.getSession()._
        self.printCheckArgs(request)
        username = row[0]
        user_id = str(row[1])
        email = row[2]
        string = """
<form action='' method='post' onsubmit='return check_args(this)'><p> """ + \
_('eMail') + """: %s""" % (email,) + """
</p><div><label for='subject'> """ + _('Asunto') + """:
<input type='text' id='subject' name='subject' size='20' maxlength='255'/></label><br/>
<label for='body'>""" + _('Texto') + """: <br/>
<textarea name='body' rows='15' cols='40' id='body'></textarea></label><br/>
<input type='hidden' name='user_id' value='%s'/>""" % (user_id,) + """
<input type='hidden' name='username' value='%s'/>""" % (username,) + """
<input type='submit' id='submit' name='submit' value=\'""" + _('Enviar') + """ \'/>
</div></form>"""
        request.write(string)
        return

    def printCheckArgs(self, request):
        _ = request.getSession()._
        page = """
<script type=\"text/javascript\">\n function check_args(form){
    message='';
    cont = true;
    if(form.body.value == ""){
        message += \"- """ + _('El texto es obligatorio') + """\\n\";\n
    }
    if(message){
        alert(\"""" + _('Error en el ingreso de datos:') + """\\n\" + message);
        return false;
    }else{
        if(form.subject.value == ""){
           cont = confirm(\"""" + _('Enviar el mensaje sin asunto?') + """\");
        }
        if(!cont){
            return false;
        }else{
            return true;
        }
    }
}
</script>
"""
        request.write(page)
        return
