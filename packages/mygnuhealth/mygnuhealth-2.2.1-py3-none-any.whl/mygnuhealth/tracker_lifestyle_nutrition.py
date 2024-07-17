from kivy.uix.screenmanager import Screen
import datetime
from uuid import uuid4
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from mygnuhealth.core import (maindb, PageOfLife, stacked_plot,
                              filter_by_date, default_date_range,
                              bol_measurement_formatter)
from mygnuhealth.lang import tr


class TrackerLifestyleNutritionScreen(Screen):
    """ Class that manages the person Nutrition related readings
        We set and retrieve the latest values from the nutrition
        subsystem (calorie intake at different times of the day)

        Attributes:
        -----------

        Methods:
        --------
            set_values: Places the new reading values on the nutrition
                        and creates the associated page of life

    """

    # NUTRITION
    def read_nutrition():
        # Retrieve the nutrition history
        nutrition = maindb.table('nutrition')
        nutrihist = nutrition.all()
        return nutrihist

    def getNutrition():
        # Extracts the latest readings from the nutrition table
        nutrihist = TrackerLifestyleNutritionScreen.read_nutrition()
        # Init to empty string to avoid undefined val
        nutriobj = ['', '', '', '', '']
        if nutrihist:
            nutri = nutrihist[-1]  # Get the latest (newest) record

            dateobj = datetime.datetime.fromisoformat(nutri['timestamp'])
            date_repr = dateobj.strftime(tr._("%a, %b %d '%y - %H:%M"))

            nutriobj = [str(date_repr), str(nutri['calmorning']),
                        str(nutri['calafternoon']),
                        str(nutri['calevening']),
                        str(nutri['caltotal'])
                        ]

        return nutriobj

    def validate_values(self, calmorning, calafternoon,
                        calevening, caltotal, information):
        # Check for sanity on values before saving them
        rc = 0
        errors = []
        if calmorning:
            if (int(calmorning) in range(1, 50000)):
                calmorning = int(calmorning)
            else:
                rc = -1
                errors.append("Morning")
        else:
            calmorning = 0

        if calafternoon:
            if (int(calafternoon) in range(1, 50000)):
                calafternoon = int(calafternoon)
            else:
                errors.append("Afternoon")
                rc = -1
        else:
            calafternoon = 0

        if calevening:
            if (int(calevening) in range(1, 50000)):
                calevening = int(calevening)
            else:
                rc = -1
                errors.append("Evening")
        else:
            calevening = 0

        if caltotal:
            if (int(caltotal) in range(1, 50000)):
                calevening = int(calevening)
            else:
                rc = -1
                errors.append("Total")
        else:
            calevening = 0

        if (rc == 0):
            self.set_values(calmorning, calafternoon, calevening,
                            caltotal, information)

        else:
            popup = Popup(
                title=tr._('Wrong values'),
                content=Label(
                    text=tr._("Please check {0}").format(errors)),
                size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

    def set_values(self, calmorning, calafternoon, calevening, caltotal,
                   information):
        nutrition = maindb.table('nutrition')
        current_date = datetime.datetime.now().isoformat()
        domain = 'lifestyle'
        context = 'nutrition'

        nutrition_event_id = str(uuid4())
        synced = False
        nutrition.insert({'timestamp': current_date,
                          'event_id': nutrition_event_id,
                          'synced': synced,
                          'calmorning': calmorning,
                          'calafternoon': calafternoon,
                          'calevening': calevening,
                          'caltotal': caltotal})

        print("Saved Nutrition information", nutrition_event_id,
              calmorning, calafternoon, calevening, caltotal, current_date)

        # Page of Life block related to Nutrition
        event_id = str(uuid4())

        monitor_readings = [
            {'nutrition': {'calmorning': calmorning,
                           'calafternoon': calafternoon,
                           'calevening': calevening,
                           'caltotal': caltotal}},
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
    def bol_measurement_formatter_nutrition(cls, args):
        calmorning = str(args.get('calmorning')) or ''
        calafternoon = str(args.get('calafternoon')) or ''
        calevening = str(args.get('calevening')) or ''
        caltotal = str(args.get('caltotal')) or ''
        u = tr._('Kcal')

        return (tr._("Morning: ") + calmorning + ' ' + u + ',  ' +
                tr._("Afternoon: ") + calafternoon + ' ' + u + '\n' +
                tr._("Evening: ") + calevening + ' ' + u + ',  ' +
                tr._("Total: ") + caltotal + ' ' + u)


bol_measurement_formatter.add(
    'nutrition',
    TrackerLifestyleNutritionScreen.bol_measurement_formatter_nutrition)


class TrackerLifestyleNutritionStatsScreen(Screen):
    date_start = ObjectProperty()
    date_end = ObjectProperty()
    nutrition_plot = ObjectProperty()

    def on_pre_enter(self):
        date_range = default_date_range(
            data=TrackerLifestyleNutritionScreen.read_nutrition()
        )
        self.date_start = date_range[0]
        self.date_end = date_range[1]
        # Update / Refresh the chart anytime we access the stats screen
        self.nutrition_plot = self.Nutritionplot()

    def update_pots(self, date_start, date_end):
        self.date_start = date_start
        self.date_end = date_end
        self.nutrition_plot = self.Nutritionplot()

    def convert(self, value):
        try:
            value = float(value)
        except BaseException:
            value = 0

        return value

    # Plotting - Nutrition
    def Nutritionplot(self):
        # Retrieves all the history and packages into an array.
        nutrihist = filter_by_date(
            TrackerLifestyleNutritionScreen.read_nutrition(),
            self.date_start,
            self.date_end)
        nutri_morning = []
        nutri_afternoon = []
        nutri_evening = []
        nutri_date = []

        # Sort the list of dictionaries using the timestamp as key
        sorted_list = sorted(nutrihist, key=lambda sk: sk.get('timestamp'))

        for element in sorted_list:
            dateobj = datetime.datetime.fromisoformat(element.get('timestamp'))
            nutri_date.append(dateobj.strftime('%Y-%m-%d'))
            nutri_morning.append(self.convert(element.get('calmorning')))
            nutri_afternoon.append(self.convert(element.get('calafternoon')))
            nutri_evening.append(self.convert(element.get('calevening')))

        series = {tr._('Morning'): nutri_morning,
                  tr._('Afternoon'): nutri_afternoon,
                  tr._('Evening'): nutri_evening}

        chart_io = stacked_plot(
            title=tr._('Nutrition') + ' (' + tr._('Kcal') + ')',
            series=series,
            x_values=nutri_date,
            renderfmt='png')

        return CoreImage(chart_io, ext="png").texture
