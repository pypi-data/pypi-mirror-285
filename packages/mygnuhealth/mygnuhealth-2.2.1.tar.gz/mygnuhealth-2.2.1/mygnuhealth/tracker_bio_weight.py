from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from mygnuhealth.core import (maindb, PageOfLife, line_plot,
                              filter_by_date, default_date_range,
                              bol_measurement_formatter)
from mygnuhealth.lang import tr

import datetime
from uuid import uuid4

# In a future, try to work directly with SVG format generated from pygal
# from kivy.graphics.svg import Svg
# from kivy.uix.scatter import Scatter

"""
# For future use when pygal svg chart better integrates with Kivy
class SvgWidget(Scatter):

    def __init__(self, **kwargs):
        super(SvgWidget, self).__init__(**kwargs)
        with self.canvas:
            src = TrackerBioWeightStatsScreen.Weightplot()
            svg = Svg(source=src)
"""


class TrackerBioWeightScreen(Screen):
    """Class that manages the person weight readings

        Attributes:
        -----------

        Methods:
        --------
            set_values: Places the new reading values on the 'weight'
            and creates the associated page of life
            default_weight: Gets the latest weight (TODO replace by getWeight)
            read_weight: Retrieve the weight levels history
            getWeight: Extracts the latest readings from Weight
    """

    def default_weight(self):
        weighttable = maindb.table('weight')
        if (len(weighttable) > 0):
            last_weight = weighttable.all()[-1]
            return (last_weight['weight'])
        else:
            return 0

    def read_weight():
        # Retrieve the weight levels history
        weighttable = maindb.table('weight')
        weighthist = weighttable.all()
        return (weighthist)

    def getWeight():
        # Extracts the latest readings from Weight
        weighthist = TrackerBioWeightScreen.read_weight()
        weightobj = ['', '']
        if (weighthist):
            weight = weighthist[-1]  # Get the latest (newest) record
            dateobj = datetime.datetime.fromisoformat(weight['timestamp'])
            date_repr = dateobj.strftime(tr._("%a, %b %d '%y - %H:%M"))

            weightobj = [str(date_repr), str(weight['weight'])]
        return weightobj

    def validate_values(self, body_weight):
        # Check for sanity on values before saving them
        rc = 0
        errors = []

        if body_weight:
            if (2 <= float(body_weight) < 500):
                body_weight = float(body_weight)
            else:
                print("Wrong value for weight")
                rc = -1
                errors.append("Body weight")
        else:
            body_weight = 0
            print("No weight")

        if (rc == 0):
            self.set_values(body_weight)

        else:
            popup = Popup(
                title=tr._('Wrong values'),
                content=Label(
                    text=tr._("Please check {0}").format(errors)),
                size_hint=(0.5, 0.5), auto_dismiss=True)

            popup.open()

    def set_values(self, body_weight):
        weighttable = maindb.table('weight')
        profiletable = maindb.table('profile')
        current_date = datetime.datetime.now().isoformat()
        domain = 'medical'
        context = 'self_monitoring'

        if body_weight > 0:
            event_id = str(uuid4())
            synced = False
            height = None
            bmi = None
            if (len(profiletable) > 0):
                height = profiletable.all()[0]['height']
            vals = {'timestamp': current_date,
                    'event_id': event_id,
                    'synced': synced,
                    'weight': body_weight}
            measurements = {'wt': body_weight}

            # If height is in the person profile, calculate the BMI
            if height:
                bmi = body_weight / ((height / 100)**2)
                bmi = round(bmi, 1)  # Use one decimal
                vals['bmi'] = bmi
                measurements['bmi'] = bmi

            weighttable.insert(vals)

            print("Saved weight", event_id, synced, body_weight, bmi,
                  current_date)

            # Create a new PoL with the values
            # within the medical domain and the self monitoring context
            pol_vals = {
                'page': event_id,
                'page_date': current_date,
                'domain': domain,
                'context': context,
                'measurements': [measurements]
            }

            # Create the Page of Life associated to this reading
            PageOfLife.create_pol(PageOfLife, pol_vals)

    @classmethod
    def bol_measurement_formatter_weight(cls, args):
        weight = str(args) or ''
        return tr._("Weight: ") + weight + ' ' + tr._("kg")

    @classmethod
    def bol_measurement_formatter_bmi(cls, args):
        bmi = str(args) or ''
        return tr._("BMI: ") + bmi + ' ' + tr._("kg/m2")


bol_measurement_formatter.add(
    'wt',
    TrackerBioWeightScreen.bol_measurement_formatter_weight)


bol_measurement_formatter.add(
    'bmi',
    TrackerBioWeightScreen.bol_measurement_formatter_bmi)


class TrackerBioWeightStatsScreen(Screen):
    date_start = ObjectProperty()
    date_end = ObjectProperty()
    weight_plot = ObjectProperty(None)

    def on_pre_enter(self):
        date_range = default_date_range(
            data=TrackerBioWeightScreen.read_weight()
        )
        self.date_start = date_range[0]
        self.date_end = date_range[1]
        # Update / Refresh the chart anytime we access the stats screen
        self.weight_plot = self.Weightplot()

    def update_pots(self, date_start, date_end):
        self.date_start = date_start
        self.date_end = date_end
        self.weight_plot = self.Weightplot()

    # Plotting - Weight
    def Weightplot(self):
        # Retrieves the history and packages into an array.
        weighthist = filter_by_date(
            TrackerBioWeightScreen.read_weight(),
            self.date_start,
            self.date_end)

        weight = []
        weight_date = []
        sorted_list = sorted(weighthist, key=lambda sk: sk['timestamp'])

        for element in sorted_list:
            dateobj = datetime.datetime.fromisoformat(element.get('timestamp'))
            # Transform datetime obj to str for the x labels
            weight_date.append(dateobj.strftime('%Y-%m-%d'))
            weight.append(element.get('weight'))

        series_weight = {tr._('Weight'): weight}

        # In the future we could use renderfmt='svg' instead of png
        chart_io = line_plot(
            title=tr._('Weight') + ' (' + tr._('Kg') + ')',
            series=series_weight,
            y_legend=tr._('Kg'),
            x_values=weight_date,
            renderfmt='png')

        return CoreImage(chart_io, ext='png').texture

        # return chart  # Use for future SVG plots
