from kivy.uix.screenmanager import Screen
import datetime
from uuid import uuid4
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
from mygnuhealth.core import (maindb, PageOfLife, line_plot,
                              filter_by_date, default_date_range,
                              bol_measurement_formatter)
from mygnuhealth.lang import tr


class TrackerLifestyleSocialScreen(Screen):
    """ Class that manages the person meaningful Social Activity related
        readings. We set and retrieve the latest values from the social
        activity subsystem (meaningful social activities in minutes)

        Attributes:
        -----------

        Methods:
        --------
            set_values: Places the new reading values on the social
                        activity and creates the associated page of life

    """

    # MEANINGFUL SOCIAL ACTIVITIES
    def read_sa():
        # Retrieve the social activity history
        social_activity = maindb.table('socialactivity')
        sahist = social_activity.all()
        return sahist

    def getSA():
        # Extracts the latest readings from Social Activity table
        sahist = TrackerLifestyleSocialScreen.read_sa()
        saobj = ['', '']  # Init to empty string to avoid undefined val
        if sahist:
            sa = sahist[-1]  # Get the latest (newest) record

            dateobj = datetime.datetime.fromisoformat(sa['timestamp'])
            date_repr = dateobj.strftime(tr._("%a, %b %d '%y - %H:%M"))

            saobj = [str(date_repr), str(sa['meaningful'])]

        return saobj

    def set_values(self, meaningful, information):
        social_activity = maindb.table('socialactivity')
        current_date = datetime.datetime.now().isoformat()
        domain = 'lifestyle'
        context = 'social_activities'

        sa_event_id = str(uuid4())
        synced = False
        social_activity.insert(
            {'timestamp': current_date,
             'event_id': sa_event_id,
             'synced': synced,
             'meaningful': meaningful})

        print("Saved Social Activity", sa_event_id, synced,
              meaningful, information)

        # Page of Life block related to Social Activity
        event_id = str(uuid4())
        monitor_readings = [{'sa': {'meaningful': meaningful}}]

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
    def bol_measurement_formatter_sa(cls, args):
        meaningful = str(args.get('meaningful')) or ''
        return (tr._("Meaningful: ") + meaningful)


bol_measurement_formatter.add(
    'sa',
    TrackerLifestyleSocialScreen.bol_measurement_formatter_sa)


class TrackerLifestyleSocialStatsScreen(Screen):
    date_start = ObjectProperty()
    date_end = ObjectProperty()
    sa_plot = ObjectProperty()

    def on_pre_enter(self):
        date_range = default_date_range(
            data=TrackerLifestyleSocialScreen.read_sa()
        )
        self.date_start = date_range[0]
        self.date_end = date_range[1]
        # Update / Refresh the chart anytime we access the stats screen
        self.sa_plot = self.SAplot()

    def update_pots(self, date_start, date_end):
        self.date_start = date_start
        self.date_end = date_end
        self.sa_plot = self.SAplot()

    # Plotting - Social Activity
    def SAplot(self):
        # Retrieves all the history and packages into an array.
        sahist = filter_by_date(
            TrackerLifestyleSocialScreen.read_sa(),
            self.date_start,
            self.date_end)

        sa_meaningful = []
        sa_date = []

        # Sort the list of dictionaries using the timestamp as key
        sorted_list = sorted(sahist, key=lambda sk: sk.get('timestamp'))

        for element in sorted_list:
            dateobj = datetime.datetime.fromisoformat(element.get('timestamp'))
            sa_date.append(dateobj.strftime('%Y-%m-%d'))
            sa_meaningful.append(element.get('meaningful'))

        series_social_activity = {
            tr._('Meaningful Social Activities'): sa_meaningful}

        chart_io = line_plot(
            title=tr._('Meaningful Social Activities') +
            ' (' + tr._('Minutes') + ')',
            series=series_social_activity,
            y_legend=tr._('Minutes'),
            x_values=sa_date,
            renderfmt='png')

        return CoreImage(chart_io, ext="png").texture
