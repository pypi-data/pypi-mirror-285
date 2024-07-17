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

import datetime
import os
import io
import sys
import math
import pygal
from pygal.style import Style
from tinydb import TinyDB, where
from mygnuhealth.myghconf import dbfile, bolfile
from mygnuhealth.lang import tr

# Set custom style for pygal charts

mygh_style = Style(
    background='transparent',
    plot_background='transparent',
    stroke_width='3',)


''' Import main and bol databases '''
maindb = TinyDB(dbfile)
boldb = TinyDB(bolfile)


def scale_xaxis(series_length, x_values):
    """ The method produces an array based on the original x_values
        of 15 elements or less, interspaced by the length of the array
        over MAX_LABELS
    """
    MAX_LABELS = 15

    index = 1
    counter = 0
    step = math.ceil(series_length / MAX_LABELS)

    while (step > 1 and index < series_length):
        if counter < step:
            x_values[index] = None
            counter = counter + 1
        else:
            counter = 0

        index = index + 1

    return x_values


def line_plot(title, y_legend, series, x_values=None, renderfmt=None):
    """ Method to plot basic charts using pygal, encapsulating
        the image object in memory
    """
    line_chart = pygal.Line(
        style=mygh_style,
        x_label_rotation=35,
        allow_interruptions=True)

    line_chart.title = title
    for title, data in series.items():
        line_chart.add(title, data)

    line_chart.x_labels = scale_xaxis(len(x_values), x_values)

    chart_io = io.BytesIO()
    if (renderfmt == 'svg'):
        line_chart.render(chart_io)  # Render to raw
        # Testing the svg format on a file
        # line_chart.render_to_file(filename='/tmp/foo.svg')
    else:
        line_chart.render_to_png(chart_io)  # PNG rendering

    chart_io.seek(0)
    return chart_io


def stacked_plot(title, series, x_values=None, renderfmt=None):

    stacked_chart = pygal.StackedBar()
    stacked_chart.title = title
    for title, data in series.items():
        stacked_chart.add(title, data)

    stacked_chart.x_labels = x_values

    chart_io = io.BytesIO()
    if (renderfmt == 'svg'):
        stacked_chart.render(chart_io)  # Render to raw
    else:
        stacked_chart.render_to_png(chart_io)  # Render to PNG

    chart_io.seek(0)
    return chart_io


def filter_by_date(data, date_start, date_end):
    start = datetime.datetime.fromisoformat(date_start).date()
    end = datetime.datetime.fromisoformat(date_end).date()

    start_is_found = []
    end_is_found = []
    results = []
    date_min = None

    for data_line in data:
        date = datetime.datetime.fromisoformat(
            data_line['timestamp']).date()
        if date_min:
            date_min = min(date, date_min)
        else:
            date_min = date
        if date == start:
            start_is_found.append('yes')
        if date == end:
            end_is_found.append('yes')
        if date >= start and date <= end:
            results.append(data_line)

    if date_min is not None:
        if start > date_min and 'yes' not in start_is_found:
            results.append({'timestamp': start.isoformat()})
    else:
        if 'yes' not in start_is_found:
            results.append({'timestamp': start.isoformat()})

    if 'yes' not in end_is_found:
        results.append({'timestamp': end.isoformat()})

    return results


def default_date_range(data=None):

    sorted_list = sorted(data, key=lambda sk: sk.get('timestamp'))

    if sorted_list:
        date_start = datetime.datetime.fromisoformat(
            sorted_list[0].get('timestamp')).strftime("%Y-%m-%d")
    else:
        date_start = (datetime.datetime.now() -
                      datetime.timedelta(days=7)).strftime("%Y-%m-%d")

    date_end = datetime.datetime.now().strftime("%Y-%m-%d")

    return (date_start, date_end)


def get_arch():
    if 'ANDROID_ARGUMENT' in os.environ:
        return "android"
    arch = sys.platform
    print(f"Running on {arch}")
    return arch


def pkg_path():
    if get_arch() == 'android':
        pass
        # return "/data/data/org.test.mygnuhealth/files/app/"
    else:
        moddir = os.path.dirname(os.path.abspath(__file__))
        return moddir


def get_user_profile(db):
    """Retrieves the user profile (DoB, sex, height ...)"""

    profile_table = db.table('profile')
    profile = None
    # Credentials table holds a singleton, so only one record
    if (len(profile_table) > 0):
        profile = profile_table.all()[0]
    return profile


def get_personal_key(db):
    """Retrieves the user personal key"""

    credentials_table = db.table('credentials')
    # Credentials table holds a singleton, so only one record
    personal_key = credentials_table.all()[0]['personal_key']
    return personal_key.encode()


def get_federation_account():
    """Retrieves the user GH Federation account, if any."""

    federation_table = maindb.table('federation')
    fedacct = None
    if (len(federation_table) > 0):
        # Federation Account table holds a singleton, so only one record
        res = federation_table.all()[0]
        if 'federation_account' in res.keys():
            fedacct = res['federation_account']
    return fedacct


def get_device(model):
    """Retrieves the device features and ID based on the model"""

    device_table = maindb.table('devices')
    # device = None

    res = device_table.search(where('model') == model)

    return res


def check_date(date):
    """ Verifies that the entered date is valid"""
    year, month, day = date
    try:
        datetime.date(int(year), int(month), int(day))
        return True
    except ValueError:
        print("Invalid date")
        return False


# moddir = pkg_path()
''' Import the Natural variants database from the data
directory, relative to the this mygnuhealth module
The datafile is loaded into the TinyDB "vardb" variable
'''

app_path = os.path.dirname(os.path.abspath(__file__))
varfile = os.path.join(app_path, 'data/variants.db')
vardb = TinyDB(varfile, access_mode='r')


class CodeNameMap():
    history = []
    mapinfo = None
    mapfunc = None
    current_mapinfo = []

    def __init__(self, mapinfo=None, mapfunc=None):
        self.mapinfo = mapinfo
        self.mapfunc = mapfunc

    def get_mapinfo(self):
        result = None
        if self.mapfunc:
            result = self.mapfunc()
        else:
            mapinfo = self.mapinfo
            result = [{'code': item['code'], 'name': tr._(item['name'])}
                      for item in mapinfo]

        self.current_mapinfo = result
        return result

    def get_names(self):
        mapinfo = self.get_mapinfo()
        return [item['name'] for item in mapinfo]

    def get_name(self, code):
        mapinfo = self.get_mapinfo()
        name = None

        for item in mapinfo:
            if item.get('code') == code:
                name = item.get('name')
                break

        return name

    def get_code(self, name):
        code = None
        mapinfo = self.get_mapinfo()

        for item in mapinfo:
            if item.get('name') == name:
                code = item.get('code')
                break

        if code is not None:
            history = list(reversed(self.history))
            for his in history:
                for item in his.get('mapinfo'):
                    if item.get('name') == name:
                        code = item.get('code')
                        break

        return code

    def update_history(self, name):
        self.history.append(
            {'name': name,
             'mapinfo': self.current_mapinfo})


class PageOfLife():
    """
    Page of Life
    The basic shema of PoL from GH Federation HIS, used  by Thalamus

    Attributes
    ----------
        boldb: TinyDB instance
            The book of life DB. It contains all the Pages of Life created
            by the user.

        pol_model : dict
            Dictionary holding the schema of the GNU Healtth Federation
            Health Information System database

        medical_context: In a page of life, when the medical domain is chosen,
            the user can choose

        social_context: The different contexts within the Social domain.

        Methods:
        --------
            create_pol: Creates a Page of Life associated the event / reading

    """

    boldb = TinyDB(bolfile)

    pol_model = dict.fromkeys([
        'book', 'page_date', 'age', 'domain', 'relevance', 'privacy',
        'context', 'measurements', 'genetic_info', 'summary', 'info',
        'node', 'author', 'author_acct', 'fsynced'
    ])

    def create_pol(self, pol_vals):
        """Creates a Page of Life associated to the reading

        Parameters
        ----------
        pol_vals: Takes all the values from the page of life, which is a
        dictionary. Some of them:
            domain: the domain (medical, psycho, social)
            context: the context within a domain (possible contexts are listed
                in the core module.
            genetic_info: variant, rsref, protein, gene, aa_change
            measurements: blood pressure, Osat, temp, heart & resp frequency,..
            summary: Short description / title of the page
            info: Extended information related to this page of life.
        """

        node = "mygnuhealth"  # The node name is generic. "mygnuhealth"
        fed_acct = get_federation_account()
        poltable = self.boldb.table('pol')
        page_of_life = self.pol_model.copy()

        domain = pol_vals.get('domain')
        context = pol_vals.get('context')

        if (fed_acct):
            #  If the Federation account does not exist, it will be
            #  a private entry, not linked to a book or author
            #  and it won't be shared in the GNU Health Federation

            print("Retrieved Federation Account: ", fed_acct)
            page_of_life['book'] = fed_acct
            page_of_life['author'] = fed_acct
            page_of_life['author_acct'] = fed_acct

        page_of_life['node'] = node
        page_of_life['page'] = pol_vals.get('page')
        page_of_life['page_date'] = pol_vals.get('page_date')
        page_of_life['domain'] = domain
        page_of_life['context'] = context
        page_of_life['relevance'] = pol_vals.get('relevance')
        page_of_life['privacy'] = pol_vals.get('privacy')
        page_of_life['genetic_info'] = pol_vals.get('genetic_info', '')
        page_of_life['measurements'] = pol_vals.get('measurements')
        page_of_life['summary'] = pol_vals.get('summary', '')
        page_of_life['info'] = pol_vals.get('info', '')

        # The fsync key reflects whether the page has been sent to the
        # GNU Health Federation HIS (Health Information System)
        page_of_life['fsynced'] = False
        # create the new PoL entry

        print("New Page of Life:", page_of_life.get('page'))
        data = page_of_life
        poltable.insert(data)

        # Sample measurements keys accepted by Thalamus / GH Federation HIS
        #  {'bp': {'systolic': 116, 'diastolic': 79}, 't': 36.0, 'hr': 756, '
        #    rr': 16,
        #  'osat': 99, 'wt': 68.0, 'ht': 168.0, 'bmi': 24.09, 'bg': 116}


class BookOfLifeFormatter():
    formatters = {}

    def add(self, name, formatter):
        self.formatters[name] = formatter

    def handle(self, name, args):
        if args:
            formatter = self.formatters.get(name)

            if formatter:
                return formatter(args)
            else:
                return args
        else:
            return ''


bol_domain_formatter = BookOfLifeFormatter()
bol_measurement_formatter = BookOfLifeFormatter()
bol_genetic_info_formatter = BookOfLifeFormatter()
