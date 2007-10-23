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

from beppo.Strings import _

APP_NAME = "Beppo"

OFFLINEQ_COST = 20
ARCHIVE_DIR = "archive/"
ARCHIVE_EXT = ".pdf"
PS_TO_EXT = "epstopdf"
PS_OPTIONS = ""
PS_INFILE = " "
PS_OUTFILE = " -o="

#Person kinds
TUTOR = 1
PUPIL = 2
ADMIN = 3
CLIENT = 4

#Session types
IACLASS = 1 #Alumno conectado, acceso instantaneo
PACLASS = 2 #Alumno conectado, clase precoordinada
EXTRA_IACLASS = 3 #Alumno conectado, clase fuera de turno
OFFLINE_QUESTION = 4 #Respondiendo pregunta offline
WAITING = 5 #Tutor en espera
EXTRA_WAITING = 6 #Tutor en espera, fuera de turno
DECIDING = 7 #Tutor decidiendo si acepta o no pregunta
ABSENT = 8  #Tutor ausente
POST_PROCESS = 9

#Formato de fecha
DATE_FORMAT = "%d/%m/%Y" #dd/mm/aaaa
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S" # dd/mm/aaaa hh:mm:ss
HOUR_FORMAT = "%H:%M" # hh:mm

#Schedule types
SCH_AI = 1
SCH_PC = 2

#Expiracion por defecto de las horas de los alumnos
EXPIRE_TIME = {'months':2}

#Session error codes
NORMAL = 1      #Cierre por alcance de time_end
TUTOR_ENTER = 2 #Tutor crea room
PUPIL_ENTER = 3 #Se acepta alumno
TUTOR_END = 4   #Tutor finaliza clase
PUPIL_END = 5   #Alumno finaliza clase
TUTOR_QUIT = 6  #Tutor se desconecta
SERVER_RESTART = 7 #Reconexion del servidor
QUESTION_ANSWERED = 8 #Pregunta offline contestada
QUESTION_NOT_ANSWERED = 9 #Pregunta offline no contestada
ACCEPTED = 10
REJECTED = 11
CORRECTED = 12
NOT_CORRECTED = 13

#Configuracion de mail
MAIL_FROM = "info@beppo.com.ar" # de quien le decimos al smtp que viene
                                    # el mail (no es el 'From')
MAIL_TO = "info@beppo.com.ar" #quien recibira las consultas
MAIL_HOST = "damned.except.com.ar"
MAIL_PORT = 25

#Configuración web
APP_URL = 'http://localhost:8000/'

#Servidor remoto
REMOTE_SERVER = 'localhost'

#Cola general
GENERAL = "GEN"

#Colores de usuario
TUTOR_COLOR = 1
PUPIL_COLOR = 2

#Colores de pizarra
RED = 3
YELLOW = 4
BLACK = 5
BLUE = 6
GREEN = 7
WHITE = 8
BROWN = 9
TRANSPARENT = 10
SELECTION = 11
STIPPLE = 12

colorPalette = {RED:"red", YELLOW:"yellow", BLACK:"black", BLUE:"blue", GREEN:"green", \
                WHITE:"white", BROWN:"brown", TRANSPARENT:"", SELECTION:"gray", \
                STIPPLE:"gray25", TUTOR_COLOR:"#4B0082", PUPIL_COLOR:"#B8860B"}

#Herramientas de pizarra
TEXT = 1
LINE = 2
RECTANGLE = 3
CIRCLE = 4
SQRT = 5
INTEGRAL = 6
FREEHAND = 7
FILL = 8
HIGHLIGHT = 9
ERASE_ITEM = 10
ERASE_SELECTION = 11
SELECT = 12
MOVE = 13
PASTE = 14
ARROW = 15
DARROW = 16
DASH = 17
AXES = 18
EMOTIC = 19
SYMBOL = 20
MATH = 21
POST = 22

#Anchos de linea
FINE = 3
MEDIUM = 5
BIG = 9
XBIG = 13

#Mensajes de estado de cliente
IN_QUEUE = 1
IN_CLASS = 2
IN_VIEW = 3
OUT = 4
IN_WAITING = 5
IN_ASKING = 6
IN_DECIDING = 7
IN_ANSWERING = 8
IN_POST_PROCESS = 9
statusMsg = {IN_QUEUE:_("En cola"), IN_CLASS:_("En clase"), IN_VIEW:_("Observador"), OUT:_("Fuera"), \
             IN_WAITING:_("En espera"), IN_ASKING:_("Preguntando"), IN_DECIDING:_("Decidiendo"), \
             IN_ANSWERING:_("Respondiendo"), IN_POST_PROCESS:_("Postprocesando")}

#Horas de Modo Demo
DEMO_AI = 20.0
DEMO_PC = 20.0
