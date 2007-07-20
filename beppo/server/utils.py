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

import gettext
from DBConnect import DBConnect

def setSessionLocale(session, locale_id, locale):
    session.locale = locale
    session.locale_id = locale_id
    trans = gettext.translation('beppo', 'locales', languages=[locale])
    session._ = trans.gettext


def getTranslatorFromSession(request, refresh=False):
    """ Devuelve un internacionalizador para usar como _.
        Además guarda el _ en la session, para usarlo después si hace
        falta.
        Si el usuario está autenticado busca su preferencia
        en la base de datos, y si el usuario no está autenticado, detecta
        la preferencia del browser
    """
    session = request.getSession()
    def saveLocaleInfo(data, session):
        # Callback para cuando buscamos el idioma en la DB
        locale_id = data[0][0]
        locale = data[0][1]
        session.locale_id = locale_id
        session.locale = locale
        trans = gettext.translation('beppo', 'locales', languages=[locale])
        session._ = trans.gettext
        return trans.gettext

    if hasattr(session, '_') and not refresh:
        # Ya se eligió idioma
        return session._
    else:
        if hasattr(session, 'userId'):
            # Usuario autenticado, buscamos su preferencia de la base de datos
            db = DBConnect()
            userId = session.userId
            d = db.db.runQuery('select l.id, l.locale from language l, person where person.language = l.id and person.id = %d', (userId, ))
            d.addCallback(saveLocaleInfo, session)
            return d
        else:
            # Detectamos la preferencia del browser
            locales = []
            header = request.getHeader('Accept-Language')
            if header is not None:
                locales = [x.strip() for x in header.split(';')[0].split(',')]
            locales.append('es_AR')
            trans = gettext.translation('beppo', 'locales', languages = locales)
            session._ = trans.gettext
            return trans.gettext
    # No deberíamos llegar acá
    return None

def dummyTranslator(msg):
    return msg

def timezoneToString(tz):
    _ = dummyTranslator
    return _('GMT') + ' +' + str(tz)
