#!/usr/bin/env python3
##############################################################################
#
#    MyGNUHealth : Mobile and Desktop PHR node for GNU Health
#
#           MyGNUHealth is part of the GNU Health project
#
##############################################################################
#
#    GNU Health: The Libre Digital Health Ecosystem
#    Copyright (C) 2008-2024 Luis Falcon <falcon@gnuhealth.org>
#    Copyright (C) 2011-2024 GNU Solidario <health@gnusolidario.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import os
import gettext
from kivy.lang import Observable


class Lang(Observable):
    observers = []
    lang = None

    def __init__(self, defaultlang):
        super(Lang, self).__init__()
        self.ugettext = lambda text: text
        self.lang = defaultlang
        self.switch_language(self.lang)

    def _(self, text):
        if isinstance(text, str) and text != '':
            return self.ugettext(text)
        else:
            return text

    # Used to deferred translations.
    def N_(self, text):
        return text

    def fbind(self, name, func, args, **kwargs):
        if name == "_":
            self.observers.append((func, args, kwargs))
        else:
            return super(Lang, self).fbind(name, func, *args, **kwargs)

    def funbind(self, name, func, args, **kwargs):
        if name == "_":
            key = (func, args, kwargs)
            if key in self.observers:
                self.observers.remove(key)
        else:
            return super(Lang, self).funbind(name, func, *args, **kwargs)

    def switch_language(self, lang):
        try:
            locale_dir = os.path.join(
                os.path.dirname(__file__), 'data', 'locale')
            locales = gettext.translation(
                'mygnuhealth', locale_dir, languages=[lang])
            self.ugettext = locales.gettext
            self.lang = lang

            # update all the kv rules attached to this text
            for func, largs, kwargs in self.observers:
                func(largs, None, None)
        except BaseException:
            print('Warn: switch_language can not ' +
                  f'find locale file of "{lang}"!!!')


tr = Lang("en")
