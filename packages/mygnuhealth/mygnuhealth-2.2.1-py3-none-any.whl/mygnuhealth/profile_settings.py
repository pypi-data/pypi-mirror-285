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

import bcrypt
import locale
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from mygnuhealth.lang import tr
from mygnuhealth.core import (get_personal_key, get_user_profile,
                              get_federation_account,
                              maindb, CodeNameMap)


class ProfileSettings():

    def check_current_password(current_password):
        personal_key = get_personal_key(maindb)
        cpw = current_password.encode()
        rc = bcrypt.checkpw(cpw, personal_key)
        if not rc:
            popup = Popup(
                title=tr._('Wrong password'),
                content=Label(
                    text=tr._("Current password does not match")),
                size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

        return rc

    def check_new_password(password, password_repeat):
        rc = None
        print(len(password))
        if ((password == password_repeat) and (len(password) > 2)):
            rc = password
        if not rc:
            popup = Popup(
                title=tr._('Wrong values'),
                content=Label(
                    text=tr._("Passwords don't match or key is too small")),
                size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()
        return rc

    def update_personalkey(password):
        encrypted_key = bcrypt.hashpw(password.encode('utf-8'),
                                      bcrypt.gensalt()).decode('utf-8')

        credentialstable = maindb.table('credentials')
        if (len(credentialstable) > 0):
            credentialstable.update({'personal_key': encrypted_key})
        else:
            print("Initializing credentials table")
            credentialstable.insert({'personal_key': encrypted_key})

        print("Saved personal key", encrypted_key)

    def update_height(profile):
        profiletable = maindb.table('profile')
        if (len(profiletable) > 0):
            print(f"Updating height to {profile['height']}")
            profiletable.update({'height': profile['height']})

        else:
            print(f"Initializing profile. Setting height {profile['height']}")
            profiletable.insert({'height': profile['height']})

        popup = Popup(
            title=tr._('Success!'),
            content=Label(
                text=tr._("Height succesfully updated")),
            size_hint=(0.5, 0.5), auto_dismiss=True)
        popup.open()

        return True

    def set_height(height):
        profile_height = {'height': height}
        if (height):
            ProfileSettings.update_height(profile_height)

    def all_languages_info():
        languages = [
            {'code': 'en', 'name': 'English (en)'},
            {'code': 'fr', 'name': 'Français (fr)'},
            {'code': 'de', 'name': 'Deutsch (de)'},
            {'code': 'es', 'name': 'Español (es)'},
            {'code': 'zh_CN', 'name': '中文简体 (zh_CN)'},
        ]
        return languages

    languages_map = CodeNameMap(
        mapfunc=all_languages_info)

    def all_languages():
        languages_map = ProfileSettings.languages_map
        return languages_map.get_names()

    def set_language(language_name):
        languages_map = ProfileSettings.languages_map
        languages_map.update_history(language_name)
        language_code = languages_map.get_code(language_name)
        profile_language = {'language': language_code}
        if (language_code):
            ProfileSettings.update_language(profile_language)
            tr.switch_language(language_code)

    def update_language(profile):
        profiletable = maindb.table('profile')
        if (len(profiletable) > 0):
            print(f"Updating language to {profile['language']}")
            profiletable.update({'language': profile['language']})

        else:
            print("Initializing profile. " +
                  f"Setting language {profile['language']}")
            profiletable.insert({'language': profile['language']})

        popup = Popup(
            title=tr._('Success!'),
            content=Label(
                text=tr._("Language succesfully updated")),
            size_hint=(0.5, 0.5), auto_dismiss=True)
        popup.open()

        return True

    def update_fedacct(fedacct):
        fedtable = maindb.table('federation')
        if (len(fedtable) > 0):
            fedtable.update({'federation_account': fedacct})
        else:
            print("Initializing federation settings")
            fedtable.insert({'federation_account': fedacct})

        popup = Popup(
            title=tr._('Success!'),
            content=Label(
                text=tr._("Federation account succesfully updated")),
            size_hint=(0.5, 0.5), auto_dismiss=True)
        popup.open()

        return True

    def set_fedacct(userfedacct):
        if (userfedacct):
            ProfileSettings.update_fedacct(userfedacct)

    def validate_pkey_update(current_password, password,
                             password_repeat):
        if (ProfileSettings.check_current_password(current_password) and
                ProfileSettings.check_new_password(password, password_repeat)):
            print("Pkey validation OK... updating personal key")
            ProfileSettings.update_personalkey(password)
            popup = Popup(
                title=tr._('Success!'),
                content=Label(
                    text=tr._("Personal Key sucessfully updated")),
                size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

        else:
            print("Pkey validation error")

    def default_height():
        if get_user_profile(maindb):
            return get_user_profile(maindb)['height']

    def default_language_name():
        languages_map = ProfileSettings.languages_map
        language_code = ProfileSettings.default_language_code()
        return (languages_map.get_name(language_code) or
                languages_map.get_name('en'))

    def default_language_code():
        if get_user_profile(maindb):
            language_code = (get_user_profile(maindb).get('language')
                             or locale.getdefaultlocale()[0]
                             or 'en')
            return language_code
        else:
            return locale.getdefaultlocale()[0] or 'en'

    def default_fedacct():
        return get_federation_account()
