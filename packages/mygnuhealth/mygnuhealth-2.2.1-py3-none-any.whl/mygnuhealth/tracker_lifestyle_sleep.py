from kivy.uix.screenmanager import Screen
import datetime
from uuid import uuid4
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from mygnuhealth.core import (maindb, PageOfLife, line_plot, CodeNameMap,
                              filter_by_date, default_date_range,
                              bol_measurement_formatter)
from mygnuhealth.lang import tr


class TrackerLifestyleSleepScreen(Screen):
    """ Class that manages the person Sleep related readings
        We set and retrieve the latest values from the sleep
        subsystem (time and quality)

        Attributes:
        -----------

        Methods:
        --------
            set_values: Places the new reading values on the sleep
                        and creates the associated page of life

    """
    # SLEEP
    def read_sleep():
        # Retrieve the sleep history
        sleep = maindb.table('sleep')
        sleephist = sleep.all()
        return sleephist

    @classmethod
    def getSleep(cls):
        # Extracts the latest readings from the sleep table
        sleephist = TrackerLifestyleSleepScreen.read_sleep()
        # date, hours, sleep quality
        sleepobj = ['', '', '']
        if sleephist:
            sleep = sleephist[-1]  # Get the latest (newest) record

            dateobj = datetime.datetime.fromisoformat(sleep['timestamp'])
            date_repr = dateobj.strftime(tr._("%a, %b %d '%y - %H:%M"))

            sleepobj = [str(date_repr), str(sleep['sleeptime']),
                        str(cls.get_sleep_quality_name(
                            sleep['sleepquality']))]

        return sleepobj

    sleep_quality = CodeNameMap(
        mapinfo=[
            {'code': 'good', 'name': tr.N_('Good')},
            {'code': 'light', 'name': tr.N_('Light')},
            {'code': 'poor', 'name': tr.N_('Poor')},
        ])

    @classmethod
    def get_sleep_quality_name(cls, sleep_quality_code):
        return cls.sleep_quality.get_name(sleep_quality_code)

    def validate_values(self, sleeptime, sleepquality_name, information):
        # Check for sanity on values before saving them
        rc = 0
        errors = []
        sleepquality_code = self.sleep_quality.get_code(sleepquality_name)

        if sleeptime:
            if (0.1 <= float(sleeptime) <= 23.5):
                sleeptime = float(sleeptime)
            else:
                rc = -1
                errors.append("Sleep time")
        else:
            sleeptime = 0

        if (rc == 0):
            self.set_values(sleeptime, sleepquality_code, information)

        else:
            popup = Popup(
                title=tr._('Wrong values'),
                content=Label(
                    text=tr._("Please check {0}").format(errors)),
                size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

    def set_values(self, sleeptime, sleepquality_code, information):
        sleep = maindb.table('sleep')
        current_date = datetime.datetime.now().isoformat()
        domain = 'lifestyle'
        context = 'sleep'

        sleep_event_id = str(uuid4())
        synced = False
        sleep.insert({'timestamp': current_date,
                      'event_id': sleep_event_id,
                      'synced': synced,
                      'sleeptime': sleeptime,
                      'sleepquality': sleepquality_code})

        print("Saved Sleep information", sleep_event_id,
              sleeptime, sleepquality_code, current_date)

        # Page of Life block related to Sleep
        event_id = str(uuid4())
        monitor_readings = [
            {'sleep': {'sleeptime': sleeptime,
                       'sleepquality': sleepquality_code}},
        ]

        pol_vals = {
            'page': event_id,
            'page_date': current_date,
            'domain': domain,
            'context': context,
            'measurements': monitor_readings,
            'info': information
        }

        # Create the Page of Life associated to this reading
        PageOfLife.create_pol(PageOfLife, pol_vals)

    @classmethod
    def bol_measurement_formatter_sleep(cls, args):
        sleeptime = str(args.get('sleeptime')) or ''
        sleepquality_code = str(args.get('sleepquality')) or ''
        sleepquality_name = cls. get_sleep_quality_name(
            sleepquality_code) or ''

        return (tr._("Sleep Time: ") + sleeptime + '\n' +
                tr._("Sleep Quality: ") + sleepquality_name)


bol_measurement_formatter.add(
    'sleep',
    TrackerLifestyleSleepScreen.bol_measurement_formatter_sleep)


class TrackerLifestyleSleepStatsScreen(Screen):
    date_start = ObjectProperty()
    date_end = ObjectProperty()
    sleep_plot = ObjectProperty()

    def on_pre_enter(self):
        date_range = default_date_range(
            data=TrackerLifestyleSleepScreen.read_sleep()
        )
        self.date_start = date_range[0]
        self.date_end = date_range[1]
        # Update / Refresh the chart anytime we access the stats screen
        self.sleep_plot = self.Sleepplot()

    def update_pots(self, date_start, date_end):
        self.date_start = date_start
        self.date_end = date_end
        self.sleep_plot = self.Sleepplot()

    # Plotting - Sleep
    def Sleepplot(self):
        # Retrieves all the history and packages into an array.
        sleephist = filter_by_date(
            TrackerLifestyleSleepScreen.read_sleep(),
            self.date_start,
            self.date_end)

        sleep_time = []
        sleep_date = []

        # Sort the list of dictionaries using the timestamp as key
        sorted_list = sorted(sleephist, key=lambda sk: sk.get('timestamp'))

        for element in sorted_list:
            dateobj = datetime.datetime.fromisoformat(element.get('timestamp'))
            sleep_date.append(dateobj.strftime('%Y-%m-%d'))
            sleep_time.append(element.get('sleeptime'))

        series_sleep = {tr._('Sleep'): sleep_time}

        chart_io = line_plot(
            title=tr._('Sleep') + ' (' + tr._('Hours') + ')',
            series=series_sleep,
            y_legend=tr._('Hours'),
            x_values=sleep_date,
            renderfmt='png')

        return CoreImage(chart_io, ext="png").texture
