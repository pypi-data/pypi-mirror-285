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


class TrackerBioOsatScreen(Screen):
    """Class that manages the person Hb oxygen saturation readings

        Attributes:
        -----------

        Methods:
        --------
            set_values: Places the new reading values on the 'osat'
                        and creates the associated page of life
            read_osat: Retrieve the blood osat levels history
            getOsat: Extracts the latest readings from Osat
    """

    # OSAT
    def read_osat():
        # Retrieve the blood osat levels history
        osat = maindb.table('osat')
        osathist = osat.all()
        return osathist

    def getOsat():
        # Extracts the latest readings from Osat
        osathist = TrackerBioOsatScreen.read_osat()
        osatobj = ['', '']
        if (osathist):
            osat = osathist[-1]  # Get the latest (newest) record
            dateobj = datetime.datetime.fromisoformat(osat['timestamp'])
            date_repr = dateobj.strftime(tr._("%a, %b %d '%y - %H:%M"))
            osatobj = [str(date_repr), str(osat['osat'])]
        return osatobj

    def validate_values(self, hb_osat):
        # Check for sanity on values before saving them
        rc = 0
        errors = []

        if hb_osat:
            if (int(hb_osat) in range(30, 100)):
                hb_osat = int(hb_osat)
            else:
                rc = -1
                errors.append("osat")
        else:
            hb_osat = 0

        if (rc == 0):
            self.set_values(hb_osat)

        else:
            popup = Popup(
                title=tr._('Wrong values'),
                content=Label(
                    text=tr._("Please check {0}").format(errors)),
                size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

    def set_values(self, hb_osat):
        osat = maindb.table('osat')
        current_date = datetime.datetime.now().isoformat()
        domain = 'medical'
        context = 'self_monitoring'

        if hb_osat > 0:
            event_id = str(uuid4())
            synced = False
            osat.insert({'timestamp': current_date,
                         'event_id': event_id,
                         'synced': synced,
                         'osat': hb_osat})

            print("Saved osat", event_id, synced, hb_osat, current_date)

            # Create a new PoL with the values
            # within the medical domain and the self monitoring context
            pol_vals = {
                'page': event_id,
                'page_date': current_date,
                'domain': domain,
                'context': context,
                'measurements': [{'osat': hb_osat}]
            }

            # Create the Page of Life associated to this reading
            PageOfLife.create_pol(PageOfLife, pol_vals)

    @classmethod
    def bol_measurement_formatter_osat(cls, args):
        osat = str(args) or ''
        return tr._("Osat: ") + osat + ' ' + "%"


bol_measurement_formatter.add(
    'osat',
    TrackerBioOsatScreen.bol_measurement_formatter_osat)


class TrackerBioOsatStatsScreen(Screen):
    osat_plot = ObjectProperty()
    date_start = ObjectProperty()
    date_end = ObjectProperty()

    def on_pre_enter(self):
        date_range = default_date_range(
            data=TrackerBioOsatScreen.read_osat()
        )
        self.date_start = date_range[0]
        self.date_end = date_range[1]
        # Update / Refresh the chart anytime we access the stats screen
        self.osat_plot = self.Osatplot()

    def update_pots(self, date_start, date_end):
        self.date_start = date_start
        self.date_end = date_end
        self.osat_plot = self.Osatplot()

    # Plotting - Osat
    def Osatplot(self):
        # Retrieves the history and packages into an array.
        osathist = filter_by_date(
            TrackerBioOsatScreen.read_osat(),
            self.date_start,
            self.date_end)

        osat = []
        osat_date = []
        sorted_list = sorted(osathist, key=lambda sk: sk.get('timestamp'))

        for element in sorted_list:
            dateobj = datetime.datetime.fromisoformat(element.get('timestamp'))
            osat_date.append(dateobj.strftime('%Y-%m-%d'))
            osat.append(element.get('osat'))

        series_osat = {tr._('Oxygen Saturation'): osat}

        chart_io = line_plot(
            title=tr._('Oxygen Saturation') + ' (' + '%' + ')',
            series=series_osat,
            y_legend='%',
            x_values=osat_date,
            renderfmt='png')

        return CoreImage(chart_io, ext="png").texture
