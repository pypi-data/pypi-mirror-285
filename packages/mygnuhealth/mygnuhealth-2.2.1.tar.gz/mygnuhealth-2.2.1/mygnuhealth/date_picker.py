#!/usr/bin/python

###########################################################
# date_picker.py is a fork of KivyCalendar:
#
# * KivyCalendar *
# URL: https://bitbucket.org/xxblx/kivycalendar
#      https://pypi.org/project/KivyCalendar/
# License: MIT License (MIT License)
# Author: Oleg Kozlov (xxblx)
###########################################################
import re

from calendar import Calendar, monthrange
from datetime import datetime
from dateutil.relativedelta import relativedelta

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import (NumericProperty, BooleanProperty,
                             ObjectProperty, ReferenceListProperty)

from mygnuhealth.lang import tr


class DateRange(BoxLayout):
    touch_switch = BooleanProperty()
    popup_hint_x = NumericProperty(0.7)
    popup_hint_y = NumericProperty(0.7)
    popup_hint = ReferenceListProperty(popup_hint_x, popup_hint_y)
    date_start = ObjectProperty()
    date_end = ObjectProperty()
    update_range_function = ObjectProperty()

    def update_range(self, date_start, date_end, update_range_function):
        if self.check_date_range(date_start, date_end):
            update_range_function(date_start, date_end)
        else:
            popup = Popup(
                title=tr._('Wrong Date Range.'),
                content=Label(
                    text=tr._("Please check start and end of date.")),
                size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

    def check_date_range(self, date_start, date_end):
        try:
            date_start = datetime.fromisoformat(date_start)
            date_end = datetime.fromisoformat(date_end)
            return date_start <= date_end
        except BaseException:
            return False


class DatePicker(TextInput):
    """Date picker is a textinput, if it focused shows popup with
    calendar which allows you to define the popup dimensions using
    popup_hint_x, popup_hint_y, and the popup_hint lists, for example
    in kv:

    DatePicker:
        popup_hint: 0.7,0.4

    would result in a size_hint of 0.7,0.4 being used to create the
    popup

    """
    popup_hint_x = NumericProperty(0.7)
    popup_hint_y = NumericProperty(0.7)
    popup_hint = ReferenceListProperty(popup_hint_x, popup_hint_y)
    init_date = ObjectProperty()
    touch_switch = BooleanProperty()

    def on_init_date(self, instance, value):
        self.init_ui()

    def on_touch_switch(self, instance, value):
        self.init_ui()

    def init_ui(self):

        self.text = get_init_date(self.init_date)

        # Popup Content.
        self.popup_content = DatePickerPopupContent(
            init_date=self.init_date,
            touch_switch=self.touch_switch,
            quit_function=self.quit_popup)

        # Popup
        self.popup = Popup(
            title="",
            content=self.popup_content,
            on_dismiss=self.update_value)

        self.bind(focus=self.show_popup)

    def quit_popup(self):
        self.popup.dismiss()

    def show_popup(self, isnt, val):
        """
        Open popup if textinput focused,
        and regardless update the popup size_hint
        """
        self.popup.size_hint = self.popup_hint
        if val:
            # Automatically dismiss the keyboard
            # that results from the textInput
            Window.release_all_keyboards()
            self.popup.open()

    def update_value(self, inst):
        """ Update textinput value on popup close """

        self.text = format_date(
            date=self.popup_content.get_active_date())
        self.popup_content.clear_text_input()

        self.focus = False


class DatePickerPopupContent(BoxLayout):
    init_date = ObjectProperty()
    touch_switch = ObjectProperty()
    calendar = ObjectProperty()
    date_input = ObjectProperty()
    quit_function = ObjectProperty()

    def get_active_date(self):
        return self.calendar.active_date

    def quit_calendar(self):
        self.quit_function()
        self.clear_text_input()

    def clear_text_input(self):
        self.date_input.text = ''

    def select_date(self, text):
        try:
            if re.search(r'[+ymdw]', text):
                self._select_date_by_delta(text)
            else:
                self._select_date(text)
        except BaseException:
            pass

    def _select_date(self, text):

        def format_year(year, cur_year):
            year = str(year)
            cur_year = str(cur_year)
            if len(year) < 4:
                return int(cur_year[0:(4 - len(year))] + year)
            else:
                return int(year)

        def format_month(month, cur_month):
            if month > 12:
                return cur_month
            else:
                return month

        def format_day(day, cur_day):
            if day > 31:
                return cur_day
            else:
                return day

        date_now = datetime.now()
        cur_year = date_now.year
        cur_month = date_now.month
        cur_day = date_now.day
        year, month, day = cur_year, cur_month, cur_day

        # Support 'y-m-d' 'y/m/d' and 'y m d'.
        text = re.sub(r'[^0-9-/ ]', '', text)
        text = re.sub(r'[/ ]', '-', text)
        info = [int(x) for x in text.split('-') if x != '']

        if len(info) == 3:
            year = format_year(info[0], cur_year)
            month = format_month(info[1], cur_month)
            day = format_day(info[2], cur_day)
        elif len(info) == 2:
            month = format_month(info[0], cur_month)
            day = format_day(info[1], cur_day)
        elif len(info) == 1:
            day = format_day(info[0], cur_day)
        else:
            pass

        date_str = f'{year:04}-{month:02}-{day:02}'
        date = datetime.fromisoformat(date_str).isoformat()
        self.calendar.select_date(date)

    def _select_date_by_delta(self, text):

        date_now = datetime.now()
        years = months = weeks = days = 0

        rule_list = re.sub(r'[^0-9-+wmdy ]', '', text).split(' ')

        for rule in rule_list:
            if rule != '':
                categery = rule[-1]
                if rule[0] == '-':
                    sign = -1
                else:
                    sign = 1
            else:
                categery = ''
                sign = 1

            n = re.sub(r'[^0-9]', '', rule)

            if n != '':
                num = int(n) * sign
                if categery == 'y':
                    years = num
                elif categery == 'm':
                    months = num
                elif categery == 'w':
                    weeks = num
                else:
                    days = num

        date = date_now + relativedelta(
            years=years, months=months,
            weeks=weeks, days=days)

        self.calendar.select_date(date.strftime("%Y-%m-%d"))

    def select_today(self):
        date = datetime.now().strftime("%Y-%m-%d")
        self.calendar.select_date(date, quit=True)


class CalendarWidget(RelativeLayout):
    """ Basic calendar widget """
    init_date = ObjectProperty()
    touch_switch = ObjectProperty()
    quit_function = ObjectProperty()

    def __init__(self, *args, **kwargs):
        super(CalendarWidget, self).__init__(*args, **kwargs)
        self.prepare_data()
        self.init_ui()

    def select_date(self, date, quit=False):
        self.init_date = date
        self.refresh_ui()
        if quit:
            self.quit_calendar()

    def refresh_ui(self):
        self.clear_widgets()
        self.prepare_data()
        self.init_ui()

    def quit_calendar(self):
        if self.quit_function:
            self.quit_function()

    def init_ui(self):
        self.left_arrow = ArrowButton(
            text="<", on_press=self.go_prev,
            pos_hint={"top": 1, "left": 0})

        self.right_arrow = ArrowButton(
            text=">", on_press=self.go_next,
            pos_hint={"top": 1, "right": 1})

        self.add_widget(self.left_arrow)
        self.add_widget(self.right_arrow)

        # Title
        self.title_label = MonthYearLabel(text=self.title)
        self.add_widget(self.title_label)

        # ScreenManager
        self.sm = MonthsManager()
        self.add_widget(self.sm)

        self.create_month_scr(self.quarter[1], toogle_today=True)

    def create_month_scr(self, month, toogle_today=False):
        """ Screen with calendar for one month """

        scr = Screen()
        scr.name = format_date(
            year=self.active_date['year'],
            month=self.active_date['month'])

        # Grid for days
        grid_layout = ButtonsGrid()
        scr.add_widget(grid_layout)

        # Days abbrs
        for i in range(7):
            if i >= 5:  # weekends
                line = DayAbbrWeekendLabel(text=self.days_abrs[i])
            else:  # work days
                line = DayAbbrLabel(text=self.days_abrs[i])

            grid_layout.add_widget(line)

        # Buttons with days numbers
        for week in month:
            for day in week:
                if day[1] >= 5:  # weekends
                    tbtn = DayNumWeekendButton(text=str(day[0]))
                else:  # work days
                    tbtn = DayNumButton(text=str(day[0]))

                tbtn.bind(on_press=self.get_btn_value)

                if toogle_today:
                    # Down today button
                    if day[0] == self.active_date['day'] and day[2] == 1:
                        tbtn.state = "down"
                # Disable buttons with days from other months
                if day[2] == 0:
                    tbtn.disabled = True

                grid_layout.add_widget(tbtn)

        self.sm.add_widget(scr)

    def prepare_data(self):
        """ Prepare data for showing on widget loading """

        # Get days abbrs and month names lists
        self.days_abrs = get_days_abbrs()

        # Today date
        self.active_date = get_init_date_list(self.init_date)

        # Set title
        self.title = format_date(date=self.active_date)

        # Quarter where current month in the self.quarter[1]
        self.get_quarter()

    def get_quarter(self):
        """ Get caledar and months/years nums for quarter """

        self.quarter_nums = calc_quarter(
            self.active_date['year'],
            self.active_date['month'])

        self.quarter = get_quarter(
            self.active_date['year'],
            self.active_date['month'])

    def get_btn_value(self, inst):
        """ Get day value from pressed button """

        self.active_date['day'] = int(inst.text)
        self.quit_calendar()

    def go_prev(self, inst):
        """ Go to screen with previous month """

        # Change active date
        self.active_date = {
            'day': self.active_date['day'],
            'month': self.quarter_nums['previous']['month'],
            'year': self.quarter_nums['previous']['year']}

        # Name of prev screen
        prev_scr_name = format_date(
            year=self.quarter_nums['previous']['year'],
            month=self.quarter_nums['previous']['month'])

        # If it's doen't exitst, create it
        if not self.sm.has_screen(prev_scr_name):
            self.create_month_scr(self.quarter[0])

        self.sm.current = prev_scr_name
        self.sm.transition.direction = "left"

        self.get_quarter()
        self.title = format_date(
            year=self.active_date['year'],
            month=self.active_date['month'])

        self.title_label.text = self.title

    def go_next(self, inst):
        """ Go to screen with next month """

        # Change active date
        self.active_date = {
            'day': self.active_date['day'],
            'month': self.quarter_nums['next']['month'],
            'year': self.quarter_nums['next']['year']}

        # Name of prev screen
        next_scr_name = format_date(
            year=self.quarter_nums['next']['year'],
            month=self.quarter_nums['next']['month'])

        # If it's doen't exitst, create it
        if not self.sm.has_screen(next_scr_name):
            self.create_month_scr(self.quarter[2])

        self.sm.current = next_scr_name
        self.sm.transition.direction = "right"

        self.get_quarter()

        self.title = format_date(
            year=self.active_date['year'],
            month=self.active_date['month'])

        self.title_label.text = self.title

    def on_touch_move(self, touch):
        """ Switch months pages by touch move """

        if self.touch_switch:
            # Left - prev
            if touch.dpos[0] < -30:
                self.go_prev(None)
            # Right - next
            elif touch.dpos[0] > 30:
                self.go_next(None)


class ArrowButton(Button):
    pass


class MonthYearLabel(Label):
    pass


class MonthsManager(ScreenManager):
    pass


class ButtonsGrid(GridLayout):
    pass


class DayAbbrLabel(Label):
    pass


class DayAbbrWeekendLabel(DayAbbrLabel):
    pass


class DayButton(ToggleButton):
    pass


class DayNumButton(DayButton):
    pass


class DayNumWeekendButton(DayButton):
    pass


def format_date(date=None, year=None, month=None, day=None):
    if date:
        year = date['year']
        month = date['month']
        day = date['day']

    year = year and f'{year:04}' or ''
    month = month and f'-{month:02}' or ''
    day = day and f'-{day:02}' or ''

    return year + month + day


def get_days_abbrs():
    """ Return list with days abbreviations """

    return [tr._('Mon'), tr._('Tue'), tr._('Wed'),
            tr._('Thu'), tr._('Fri'), tr._('Sat'),
            tr._('Sun')]


def get_month(y, m):
    """
    Return list of month's weeks, which day
    is a turple (<month day number>, <weekday number>)
    """

    cal = Calendar(firstweekday=0)
    month = cal.monthdays2calendar(y, m)

    # Add additional num to every day which mark from
    # this or from other day that day numer
    for week in range(len(month)):
        for day in range(len(month[week])):
            _day = month[week][day]
            if _day[0] == 0:
                this = 0
            else:
                this = 1
            _day = (_day[0], _day[1], this)
            month[week][day] = _day

    # Days numbers of days from preious and next monthes
    # marked as 0 (zero), replace it with correct numbers
    # If month include 4 weeks it hasn't any zero
    if len(month) == 4:
        return month

    quater = calc_quarter(y, m)

    # Zeros in first week
    fcount = 0
    for i in month[0]:
        if i[0] == 0:
            fcount += 1

    # Zeros in last week
    lcount = 0
    for i in month[-1]:
        if i[0] == 0:
            lcount += 1

    if fcount:

        n = monthrange(
            quater['previous']['year'],
            quater['previous']['month'])[1]

        for i in range(fcount):
            month[0][i] = (n - (fcount - 1 - i), i, 0)

    if lcount:
        # First day of next month
        n = 1

        for i in range(lcount):
            month[-1][-lcount + i] = (n + i, 7 - lcount + i, 0)

    return month


def get_quarter(y, m):
    """ Get quarter where m is a middle month """

    result = []
    quarter = calc_quarter(y, m)
    for key in ['previous', 'current', 'next']:
        result.append(get_month(
            quarter[key]['year'], quarter[key]['month']))

    return result


def calc_quarter(y, m):
    """ Calculate previous and next month """

    # Previous / Next month's year number and month number
    prev_y = y
    prev_m = m - 1
    next_y = y
    next_m = m + 1

    if m == 1:
        prev_m = 12
        prev_y = y - 1
    elif m == 12:
        next_m = 1
        next_y = y + 1

    return {'previous': {'year': prev_y, 'month': prev_m},
            'current': {'year': y, 'month': m},
            'next': {'year': next_y, 'month': next_m}}


def get_init_date_list(init_date):
    """ Return dict with today date """

    try:
        date = datetime.fromisoformat(init_date)
        return {
            'day': date.day,
            'month': date.month,
            'year': date.year}
    except BaseException:
        return {
            'day': datetime.now().day,
            'month': datetime.now().month,
            'year': datetime.now().year}


def get_init_date(init_date):
    """ Return today date """
    try:
        datetime.fromisoformat(init_date)
        return init_date
    except BaseException:
        return datetime.now().strftime("%Y-%m-%d")
