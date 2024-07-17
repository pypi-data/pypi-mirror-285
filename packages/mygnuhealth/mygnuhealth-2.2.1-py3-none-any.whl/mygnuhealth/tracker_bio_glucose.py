from kivy.uix.screenmanager import Screen
import datetime
from uuid import uuid4
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from mygnuhealth.core import (maindb, PageOfLife, line_plot,
                              filter_by_date, default_date_range,
                              bol_measurement_formatter)
from mygnuhealth.lang import tr


class TrackerBioGlucoseScreen(Screen):
    """Class that manages the person blood glucose readings

        Attributes:
        -----------

        Methods:
        --------
            set_values: Places the new reading values on the 'glucose'
            table and creates the associated page of life
            read_glucose: Retrieve the blood glucose levels history
            getGlucose: Extracts the latest readings from Glucose
    """

    def read_glucose():
        # Retrieve the blood glucose levels history
        glucose = maindb.table('glucose')
        glucosehist = glucose.all()
        return glucosehist

    def getGlucose():
        # Extracts the latest readings from Glucose
        glucosehist = TrackerBioGlucoseScreen.read_glucose()
        glucoseobj = ['', '']
        if (glucosehist):  # Enter this block if there is a history
            glucose = glucosehist[-1]  # Get the latest (newest) record
            dateobj = datetime.datetime.fromisoformat(glucose['timestamp'])
            date_repr = dateobj.strftime(tr._("%a, %b %d '%y - %H:%M"))

            glucoseobj = [str(date_repr), str(glucose['glucose'])]
        return glucoseobj

    def validate_values(self, glucose):
        # Check for sanity on values before saving them
        rc = 0
        errors = []

        if glucose:
            if (int(glucose) in range(20, 800)):
                glucose = int(glucose)
            else:
                rc = -1
                errors.append("Glucose")
        else:
            glucose = 0

        if (rc == 0):
            self.set_values(glucose)

        else:
            popup = Popup(
                title=tr._('Wrong values'),
                content=Label(
                    text=tr._("Please check {0}").format(errors)),
                size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

    def set_values(self, blood_glucose):
        """Places the new reading values on the 'glucose' table

        Parameters
        ----------
        blood_glucose: value coming from the getvals method
        """

        glucose = maindb.table('glucose')
        current_date = datetime.datetime.now().isoformat()
        domain = 'medical'
        context = 'self_monitoring'

        if blood_glucose > 0:
            event_id = str(uuid4())
            synced = False
            monitor_vals = {'timestamp': current_date,
                            'event_id': event_id,
                            'synced': synced,
                            'glucose': blood_glucose
                            }
            glucose.insert(monitor_vals)

            print("Saved glucose", event_id, synced, blood_glucose,
                  current_date)

            # Create a new PoL with the values
            # within the medical domain and the self monitoring context
            pol_vals = {
                'page': event_id,
                'page_date': current_date,
                'domain': domain,
                'context': context,
                'measurements': [{'bg': blood_glucose}]
            }

            # Create the Page of Life associated to this blood glucose reading
            PageOfLife.create_pol(PageOfLife, pol_vals)

    @classmethod
    def bol_measurement_formatter_bg(cls, args):
        bg = str(args) or ''
        return tr._("Blood Glucose: ") + bg + ' ' + tr._("mg/dl")


bol_measurement_formatter.add(
    'bg',
    TrackerBioGlucoseScreen.bol_measurement_formatter_bg)


class TrackerBioGlucoseStatsScreen(Screen):
    glucose_plot = ObjectProperty()
    date_start = ObjectProperty()
    date_end = ObjectProperty()

    def on_pre_enter(self):
        date_range = default_date_range(
            data=TrackerBioGlucoseScreen.read_glucose()
        )
        self.date_start = date_range[0]
        self.date_end = date_range[1]
        # Update / Refresh the chart anytime we access the stats screen
        self.glucose_plot = self.Glucoseplot()

    def update_pots(self, date_start, date_end):
        self.date_start = date_start
        self.date_end = date_end
        self.glucose_plot = self.Glucoseplot()

    # Plotting - Glycemia
    def Glucoseplot(self):
        # Retrieves the history and packages into an array.
        glucosehist = filter_by_date(
            TrackerBioGlucoseScreen.read_glucose(),
            self.date_start,
            self.date_end)

        glucose = []
        glucose_date = []
        sorted_list = sorted(glucosehist, key=lambda sk: sk.get('timestamp'))

        for element in sorted_list:
            dateobj = datetime.datetime.fromisoformat(element.get('timestamp'))
            glucose_date.append(dateobj.strftime('%Y-%m-%d'))
            glucose.append(element.get('glucose'))

        series_glucose = {tr._('Blood Glucose Level'): glucose}

        chart_io = line_plot(
            title=tr._('Blood Glucose Level') + ' (' + tr._('mg/dl') + ')',
            series=series_glucose,
            y_legend=tr._('mg/dl'),
            x_values=glucose_date,
            renderfmt='png')

        return CoreImage(chart_io, ext="png").texture
