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

import sys
import os
import logging
import kivy
import mygnuhealth.about as about
from mygnuhealth.user_account import UserAccount

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.properties import (ObjectProperty, ListProperty,
                             DictProperty, StringProperty)

from mygnuhealth.core import CodeNameMap
from mygnuhealth.lang import tr
# Import some of the screens from their own module files
from mygnuhealth.tracker_bio_cardio import TrackerBioCardioScreen as cardio
from mygnuhealth.tracker_bio_glucose import TrackerBioGlucoseScreen as glucose
from mygnuhealth.tracker_bio_weight import TrackerBioWeightScreen as weight
from mygnuhealth.tracker_bio_osat import TrackerBioOsatScreen as osat

from mygnuhealth.tracker_lifestyle_pactivity import \
    TrackerLifestylePactivityScreen as pactivity
from mygnuhealth.tracker_lifestyle_nutrition import \
    TrackerLifestyleNutritionScreen as nutrition

from mygnuhealth.tracker_lifestyle_sleep import TrackerLifestyleSleepScreen \
    as sleep

from mygnuhealth.tracker_lifestyle_social import TrackerLifestyleSocialScreen \
    as social_activity

from mygnuhealth.tracker_psycho_mood import TrackerPsychoMoodScreen \
    as mood

from mygnuhealth.profile_settings import ProfileSettings as profile

from mygnuhealth.network_settings import NetworkSettings as network

from mygnuhealth.bluetooth_settings import BluetoothSettings as bluetooth

from mygnuhealth.book_of_life import BookofLife as bol

from mygnuhealth.page_of_life import PoL as pol

kivy.require('2.3.0')


""" By default Kivy looks for the file name that
    of the same as the main class (MyGNUHealthApp) in
    lower case and without the App suffix, "so mygnuhealth.kv"

    We want to place the user interface in the ui directory, so
    we'll use the Builder load_file method for that.
"""
moddir = os.path.dirname(os.path.abspath(__file__))

# Change directory to this module cwd so we can invoke the images
# and other files relative to it.
os.chdir(moddir)


class Menu(BoxLayout):
    manager = ObjectProperty(None)


# Declare the screens
class InitialScreen(Screen):
    """ In this initial class, MyGNUHealth checks if the
        user account has been created. If that is the case
        the next screen will be the login screen.
        If the user does not exist, it will take them to the
        user account initial setup wizard.
    """

    def account_status(self):
        acct = UserAccount()
        account = acct.account_exist()
        if account:
            self.manager.current = "login"
        else:
            self.manager.current = "newuser"


class LoginScreen(Screen):

    personal_key = ObjectProperty()

    def validate_credentials(self):
        # Check userid
        acct = UserAccount()
        if acct.login(self.personal_key.text):
            logging.info("Welcome to the jungle!")
            App.get_running_app().login_status = True
            self.manager.current = "phr"

        else:
            # switching the current screen to display validation result
            logging.error("Wrong key")

            popup = Popup(
                title=tr._('Invalid Credentials'),
                content=Label(
                    text=tr._('Wrong Personal key')),
                size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

            # reset the personal key
            self.personal_key.text = ""


class NewUserScreen(Screen):

    sex_map = CodeNameMap(
        mapinfo=[
            {'code': 'Female', 'name': tr.N_('Female')},
            {'code': 'Male', 'name': tr.N_('Male')},
            {'code': 'Other', 'name': tr.N_('Other')},
        ])

    def init_user(self, username, sex_name, height, bday,
                  bmonth, byear, pkey, pkey_repeat):
        birthdate = [byear, bmonth, bday]
        acct = UserAccount()

        sex_code = NewUserScreen.sex_map.get_code(sex_name)

        if (acct.createAccount(pkey, pkey_repeat,
                               height, username, birthdate, sex_code)):
            self.manager.current = "login"


class AboutScreen(Screen):
    myghinfo = about


class PHRScreen(Screen):
    pass


class HealthTrackerScreen(Screen):
    pass


class ProfileSettingsScreen(Screen):
    person_height = ObjectProperty()
    person_language = ObjectProperty()
    person_fedacct = ObjectProperty()

    person_profile = profile

    def on_pre_enter(self):
        # Get the default values for height and federation account
        self.person_height = profile.default_height()
        self.person_language = profile.default_language_name()
        self.person_fedacct = profile.default_fedacct()


class NetworkSettingsScreen(Screen):
    # Default information of the thalamus server
    thalamus = DictProperty({
        'federation_account': '',
        'protocol': 'https',
        'federation_server': '',
        'federation_port': 8443,
        'enable_sync': False})

    network_settings = network

    def on_pre_enter(self):
        # Get the values from the current network settings
        if (self.network_settings.fedinfo):
            self.thalamus = self.network_settings.fedinfo


class BluetoothSettingsScreen(Screen):

    bluetooth_settings = bluetooth

    def read_device_info(self, model):
        """Retrieves the device features from the local database"""
        dev_info = self.bluetooth_settings.get_device_info(model)

        if dev_info:
            self.ids['address'].text = dev_info['address']

            for feature in dev_info['features'].keys():
                self.ids[feature].state = dev_info['features'][feature]

    def discover_device(self, model):
        """ Assign to the TextInput with id address the UID address
            of the device referenced by the model
        """
        self.ids.address.text = \
            self.bluetooth_settings.get_device_addr(model) or ''
        logging.info(f"Device address for {model}  {self.ids.address.text}")

    def sync_device(self, addr, model, features):
        """ Retrieves and saves to the local database the values of the
            services associated to the device address
        """
        active_features = []
        for feature, value in features.items():
            # In Kivy, the ToggleButton state is 'down' when pressed (selected)
            if value == 'down':
                active_features.append(feature)

        for feature in active_features:
            measure = self.bluetooth_settings.get_measures(
                addr, model, feature)
            if measure and feature == 'hr':
                logging.info(f"Retrieved measure: {measure}")
                logging.info("Syncing the results...")
                sync_info = f'synced from {model}'
                cardio.set_values(
                    self, systolic=-1, diastolic=-1,
                    heart_rate=measure, extra_info=sync_info)


class TrackerBioScreen(Screen):
    bp = ListProperty(["", "", "", ""])  # Date, sys, dia and hr
    glucose = ListProperty(["", ""])     # Date and glycemia value
    weight = ListProperty(["", ""])     # Date and weight value
    osat = ListProperty(["", ""])     # Date and osat value

    def on_pre_enter(self):
        # Refresh the chart anytime we access the bio summary
        self.bp = cardio.getBP()
        self.glucose = glucose.getGlucose()
        self.weight = weight.getWeight()
        self.osat = osat.getOsat()


class PageofLifeScreen(Screen):
    pdate = ListProperty(["", "", "", "", ""])  # Year, month, day, hour, min
    domain_names = ListProperty()
    domain_context_names = ListProperty()
    relevance_names = ListProperty()

    rsinfo = DictProperty(
        {'dbsnp': '', 'gene': '', 'protein': '', 'variant': '',
         'aa_change': '', 'category': '', 'disease': ''})

    page = pol

    def on_pre_enter(self):
        self.pdate = pol.get_date()
        self.domain_names = pol.get_domain_names()
        self.relevance_names = pol.get_relevance_names()

    def get_domain_context_names(self, domain_name):
        self.domain_context_names = pol.get_context_names(domain_name)

    def domain_context_is_genetic(self, domain_name):
        return pol.domain_context_is_genetic(domain_name)

    def get_rsinfo(self, rs):
        if (rs):
            res = pol.checkSNP(rs)
            if res:
                self.rsinfo = res
            else:
                # Reset to '' all the rsinfo dictionary key values
                self.rsinfo = dict.fromkeys(self.rsinfo, '')


class ScrollableLabel(ScrollView):
    text = StringProperty('')


class BookofLifeSummaryButton(Button):
    text = StringProperty('')
    page_info = DictProperty({})


class BookofLifeScreen(Screen):
    bolgrid = ObjectProperty()
    book = ListProperty([])

    bookcls = bol

    pols_cache = []
    last_group = 1
    group_range = (0, 0)
    group_length = 50

    clock = None
    syncing_image = None

    def summary_button_callback(self, event):
        page_info = event.page_info
        popup = Popup(
            title=page_info['domain'],
            content=ScrollableLabel(
                text=page_info['summary']),
            size_hint=(0.7, 0.7),
            auto_dismiss=True)
        popup.open()

    def create_pols_widgets(self, group=1, use_pols_cache=False):
        if use_pols_cache:
            pols = self.pols_cache
        else:
            pols = list(reversed(bol.read_book()))
            self.pols_cache = pols

        group_range = (1, len(pols) // self.group_length + 1)
        group = min(group_range[1], max(group, 1))

        self.group_range = group_range
        self.last_group = group

        begin = (group - 1) * self.group_length
        to = group * self.group_length

        pols_showed = pols[begin:to]

        widgets = []

        for page in pols_showed:
            if page["fsynced"]:
                tags = ''
            elif page['privacy']:
                tags = tr._('Private')
            else:
                tags = tr._('Not synced')

            if tags != '':
                tags = '\n(' + tags + ')'

            page_date = (f'[color=#32393a]{str(page["date"])}' +
                         f'[b]{tags}[/b][/color]')
            page_domain_summary = (
                f'[color=#32393a][b]{str(page["domain"])}:[/b]\n' +
                f'{str(page["summary"])}[/color]')

            date_widget = Label(text=page_date, markup=True)

            domain_summary_widget = BookofLifeSummaryButton(
                text=page_domain_summary,
                page_info=page)
            domain_summary_widget.bind(
                on_press=self.summary_button_callback)

            widgets.append(
                (date_widget, domain_summary_widget))

        return widgets

    def on_pre_enter(self):
        widgets = self.create_pols_widgets(group=1)
        self.bolgrid_add_widgets(widgets)

    def bolgrid_add_widgets(self, widgets):
        self.bolgrid.clear_widgets()

        for date_widget, domain_summary_widget in widgets:
            self.bolgrid.add_widget(date_widget)
            self.bolgrid.add_widget(domain_summary_widget)

        self.ids.show_pols_groups_info.text = self.show_pols_groups_info()

    def show_pols_groups_info(self):
        group_range = self.group_range
        last_group = self.last_group

        if last_group == group_range[0]:
            fmt = '{0}[{1}] .. {3}{4}'
        elif last_group == group_range[1]:
            fmt = '{0}{1} .. [{3}]{4}'
        else:
            fmt = '{0}{1} .. [{2}] .. {3}{4}'

        info = fmt.format(
            '[color=#32393a]',
            group_range[0],
            last_group,
            group_range[1],
            '[/color]')

        return info

    def show_next_pols_group(self, arg=1):
        group = self.last_group + arg
        self.jump_to_pols_group(group)

    def show_previous_pols_group(self, arg=1):
        self.show_next_pols_group(-1 * arg)

    def jump_to_pols_group(self, group=1):
        try:
            group = int(group)
        except BaseException:
            group = 1
        widgets = self.create_pols_widgets(
            group=group, use_pols_cache=True)
        self.bolgrid_add_widgets(widgets)
        self.ids.bolscroll.scroll_y = 1

    def sync_book(self, fedkey, button_id):
        sync_button = self.ids[button_id]
        syncing_image = Image(
            source='./images/syncing-icon.gif',
            anim_delay=0.1,
            size=sync_button.size,
            pos=sync_button.pos)
        sync_button.add_widget(syncing_image)
        self.syncing_image = syncing_image

        def redraw(self, args):
            syncing_image.size = sync_button.size
            syncing_image.pos = sync_button.pos
        self.bind(size=redraw, pos=redraw)

        callback = self.refresh_current_pols_group
        self.bookcls.sync_book(fedkey, callback=callback)

    def refresh_current_pols_group(self, sync_state):
        pols = list(reversed(bol.read_book()))
        self.pols_cache = pols
        if self.clock:
            self.clock.cancel()
        self.clock = Clock.schedule_once(
            lambda dt: self.refresh_current_pols_group_for_clock(sync_state),
            0.5)

    def refresh_current_pols_group_for_clock(self, sync_state):
        sync_error = sync_state.get('error')
        if sync_error:
            popup = Popup(
                title=tr._('Federation Sync Error'),
                content=ScrollableLabel(
                    text=str(sync_error)),
                size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()
        else:
            self.jump_to_pols_group(self.last_group),

        sync_button = self.syncing_image.parent
        sync_button.remove_widget(self.syncing_image)


class TrackerLifestyleScreen(Screen):
    # Date, aerobic, anaerobic, steps
    pactivity = ListProperty(["", "", "", ""])
    # Date, morning, afternoon, evening, total, info
    nutrition = ListProperty(["", "", "", "", ""])
    # Date, sleep_time, quality, info
    sleep = ListProperty(["", "", "", ""])
    # Date, meaningful social activities time, info
    social_activity = ListProperty(["", "", ""])

    def on_pre_enter(self):
        # Refresh the chart anytime we access the lifestyle summary
        self.pactivity = pactivity.getPA()
        self.nutrition = nutrition.getNutrition()
        self.sleep = sleep.getSleep()
        self.social_activity = social_activity.getSA()


class TrackerPsychoScreen(Screen):
    # Date, mood, energy, info
    mood = ListProperty(["", "", "", ""])

    def on_pre_enter(self):
        # Refresh the chart anytime we access the lifestyle summary
        self.mood = mood.getMood()


class ScreenController(ScreenManager):
    pass


# Load the main kv file from the UI directory
# call load_file from here, after all the classes are declared
kv = Builder.load_file('ui/mygnuhealth.kv')

""" By default Kivy looks for the file name that
    of the same as the main class (MyGNUHealthApp) in
    lower case and without the "App" suffix, "so mygnuhealth.kv"
    We use the Builder load_file method to call it from the ui dir
"""


class MyGnuHealthApp(App):
    # Use a soft background color
    # Window.clearcolor = get_color_from_hex('#f5fafa')
    Window.clearcolor = get_color_from_hex('#ffffff')

    """ The last_known_screen keeps the latest loaded screen.
        We use this variable for return to the previous screen
        as in the the About page (similar to a stack pop operation)
    """
    last_known_screen = None
    login_status = False

    language_code = profile.default_language_code()
    tr.switch_language(language_code)

    def build(self):
        self.title = f"MyGNUHealth {about.__version__}"
        self.icon = 'images/mygnuhealth-icon.png'
        return Menu()

    def bailout(self, rc):
        """ Exit the application with the given return code, rc
        """
        sys.exit(rc)


def mygh():
    MyGnuHealthApp().run()


if __name__ == "__main__":
    mygh()
