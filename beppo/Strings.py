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

def _(key):
    appStrings = {
            "Nombre aplicacion":"Beppo",
            "Lista de aulas":"Lista de Aulas",
            "Lista de materias":"Lista de Materias",
            "Imprimir":"Imprimir",
            "Salir":"Salir",
            "Archivo":"Archivo",
            "Edicion":"Edición",
            "Emoticonos":"Emoticonos",
            "Simbolos":"Símbolos",
            "Matematica":"Matemática",
            "Griego":"Griego",
            "Manual de instrucciones":"Manual de Instrucciones",
            "Acerca de...":"Acerca de...",
            "Ayuda":"Ayuda",
            "Links utiles":"Links Útiles",
            "Links":"Links",
            "Preguntas offline":"Preguntas offline",
            "Postprocesado de pizarras":"Postprocesado de pizarras",
            "Cortar":"Cortar",
            "Copiar":"Copiar",
            "Pegar":"Pegar", 
            "Importar texto":"Importar texto",
            "Cola General":"Cola General",
            "Abrir IA extra?":"Todavia no comenzo su horario de clase, quiere abrir un aula de AI Extra?",
            "IA extra":"Clase AI extra",
            "El alumno abandono":"El alumno abandonó",
            "La clase esta por terminar":"La clase está por terminar",
            "El aula se cerro":"El aula se cerró",
            "Tutor":"Tutor",
            "Tipo de clase":"Tipo de clase",
            "Acceso instantaneo":"Acceso instantáneo",
            "Precoordinada":"Precoordinada",
            "Acceso instantaneo (extra)":"Acceso instantáneo (extra)",
            "Hora de cierre":"Hora de cierre",
            "Materias":"Materias",
            "Elegir una materia":"Debe elegir una materia",
            "Proponer pregunta":"Debe proponer pregunta",
            "Clase precoordinada (acceso no permitido)":"Clase precoordinada (acceso no permitido)",
            "Pregunta offline":"Pregunta offline",
            "Guardar pregunta offline?":"Guardar pregunta offline? (20 min AI)",
            "Pregunta guardada":"Pregunta guardada",
            "Pregunta no guardada":"Pregunta no guardada",
            "No tiene suficientes horas disponibles":"No tiene suficientes horas disponibles",
            "Encolar":"Encolar",
            "Tutor no da materia. Entrar?":"El tutor no está dando la materia seleccionada. Quiere entrar igual?",
            "Elegir al menos una materia":"Debe elegir al menos una materia",
            "Respondiendo pregunta offline":"Está respondiendo una pregunta offline",
            "El tutor te rechazo":"El tutor te rechazó",
            "El tutor cerro":"El tutor cerró",
            "Fin de clase":"Fin de clase",
            "Comentario":"Ingrese un comentario",
            "Error al guardar clase":"Error al guardar clase",
            "Tiene un aula solicitada":"Tiene un aula solicitada",
            "Tiene un aula abierta":"Tiene un aula abierta",
            "Tiene horario de clases asignado ahora":"Tiene horario de clases asignado ahora",
            "Postprocesado":"Postprocesado",
            "Error al guardar respuesta":"Error al guardar respuesta",
            "Respuesta guardada":"Respuesta guardada",
            "Respuesta no guardada":"Respuesta no guardada",
            "Aulas disponibles":"Aulas disponibles",
            "Informacion":"Informacion",
            "en cola":"en cola",
            "Entrar":"Entrar",
            "Preguntar":"Preguntar",
            "Ver":"Ver",
            "Seleccionar un aula":"Debe seleccionar un aula",
            "Abandonar":"Abandonar",
            "Crear":"Crear",
            "Terminar clase":"Terminar clase",
            "Eliminar":"Eliminar",
            "Nuevo alumno":"Nuevo alumno",
            "Aceptar alumno?":"Quiere aceptar la pregunta?",
            "Pizarras":"Pizarras",
            "Aceptar":"Aceptar",
            "Actualizar":"Actualizar",
            "Cancelar":"Cancelar",
            "Postprocesar":"Postprocesar",
            "Responder":"Responder",
            "Rechazar":"Rechazar",
            "En cola":"En cola",
            "En clase":"En clase",
            "Observador":"Observador",
            "Fuera":"Sin actividad",
            "En espera":"En espera",
            "Preguntando":"Preguntando",
            "Decidiendo":"Decidiendo",
            "Respondiendo":"Respondiendo",
            "Postprocesando":"Postprocesando",
            "Usuario":"Usuario",
            "Contraseña":"Contraseña",
            "Conectarse":"Conectarse",
            "Error de login":"Error de login",
            "Error al conectarse":"Error al conectarse",
            "No tiene mas horas disponibles":"No tiene más horas disponibles",
            "Enviar" : "Enviar"
    }
    value = appStrings.get(key)
    if value:
        return value
    else:
        return key

