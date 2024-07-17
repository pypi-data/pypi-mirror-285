import json
import requests
import threading
import datetime
from tinydb import Query

from mygnuhealth.core import (maindb, boldb,
                              bol_domain_formatter,
                              bol_measurement_formatter,
                              bol_genetic_info_formatter)

from mygnuhealth.lang import tr


class BookofLife():
    """Class that manages the person Book of Life

        Attributes:
        -----------
            boldb: TinyDB instance.
                Holds the book of life with all the events (pages of life)
        Methods:
        --------
            read_book: retrieves all pages
            format_bol: compacts and shows the relevant fields in a
            human readable format
    """

    def format_bol(bookoflife):
        """Takes the necessary fields and formats the book in a way that can
        be shown in the device, mixing fields and compacting entries in a more
        human readable format"""
        book = []
        for pageoflife in bookoflife:
            pol = {}
            summ = []
            msr = []

            # Page ID
            pol['page_id'] = pageoflife['page']

            # Federation sync state.
            pol['fsynced'] = pageoflife['fsynced']

            # Privacy page
            pol['privacy'] = pageoflife['privacy']

            # Date
            dateobj = datetime.datetime.fromisoformat(pageoflife['page_date'])
            # Use a localized and easy to read date format
            date_repr = dateobj.strftime(tr._("%a, %b %d '%y\n%H:%M"))
            pol['date'] = date_repr

            # Domain and context
            pol['domain'] = bol_domain_formatter.handle(
                'domain', [pageoflife['domain'], pageoflife['context']])

            # Title
            title = pageoflife['summary']
            if title:
                summ.append(f'{title}')

            # Measurement
            mvals = pageoflife['measurements']
            if ('measurements' in pageoflife.keys() and
                    mvals):

                for measure in mvals:
                    for name, values in measure.items():
                        msr.append(
                            bol_measurement_formatter.handle(
                                name, values))

                summ = summ + msr

            # Genetics
            genetics = pageoflife['genetic_info']
            if ('genetic_info' in pageoflife.keys() and
                    genetics):

                summ.append(
                    bol_genetic_info_formatter.handle(
                        'genetic_info', genetics))

            # Detail info
            details = pageoflife['info']
            if details:
                summ.append(f'{details}')

            pol['summary'] = "\n".join(summ)
            book.append(pol)
        return book

    def read_book():
        """retrieves all pages of the individual Book of Life
        """
        booktable = boldb.table('pol')
        book = booktable.all()
        formatted_bol = BookofLife.format_bol(book)
        return formatted_bol

    def check_sync_status(self):
        fedinfo = maindb.table('federation')
        if len(fedinfo):
            sync = fedinfo.all()[0]['enable_sync']
            return sync

    def sync_book(fedkey, callback=None):
        # Emit the signal to display a busy indicator while
        # pushing the pages of life to the GH federation
        print(tr._("***** Initiating the synchronization "
                   "with the GH federation server"))
        # self.pushingPols.emit()
        # Spawn a new thread so synchronization / pushing is done
        # asynchronously in a non-blocking fashion
        thread = threading.Thread(
            name="pushpols_thread",
            target=BookofLife.push_pols,
            args=(fedkey, callback))
        thread.start()

    def push_pols(fedkey, callback=None):
        state = {}

        try:
            BookofLife._push_pols(fedkey)
        except BaseException as e:
            print(f'Sync error: {e}')
            state['error'] = e

        if callback:
            callback(state)

    def _push_pols(fedkey):
        """This method will go through each page in the book of life
        that has not been sent to the GNU Health Federation server yet
        (fsynced = False).
        It also checks for records that have a book associated to it
        and that the specific page is has not the "private" flag set.

        Parameters
        ----------
        """
        fedinfo = maindb.table('federation')
        if not len(fedinfo):
            raise Exception(
                tr._("Thalamus settings have problems in network setting."))
            return

        res = fedinfo.all()[0]

        # Refresh all pages of life
        booktable = boldb.table('pol')
        book = booktable.all()
        user = res.get('federation_account')
        protocol = res.get('protocol')
        server = res.get('federation_server')
        port = res.get('federation_port')

        if not user or user == '':
            raise Exception(
                tr._("Can't find Federation account from profile setting."))
            return

        if not fedkey or fedkey == '':
            raise Exception(
                tr._("Need to enter the federation password."))
            return

        pages_send_failed = []

        for pol in book:
            timestamp = pol.get('page_date')
            node = pol.get('node')
            page_id = pol.get('page')
            synced = pol.get('fsynced')

            # Only sync those pages that are not private
            privacy = pol.get('privacy')
            if not privacy and not synced:
                creation_info = {
                    'user': user,
                    'timestamp': timestamp,
                    'node': node}

                pol['creation_info'] = creation_info
                pol['id'] = page_id

                url = f"{protocol}://{server}:{port}/pols/{user}/{page_id}"

                pol['fsynced'] = True
                send_data = requests.request(
                    'POST', url,
                    data=json.dumps(pol),
                    auth=(user, fedkey),
                    verify=False)

                if send_data:
                    Page = Query()
                    booktable.update(
                        {'fsynced': True}, Page.page == page_id)
                else:
                    pages_send_failed.append(page_id)

        if len(pages_send_failed) > 0:
            raise Exception(
                tr._("Pages send failed: {}").format(
                    '\n'.join(pages_send_failed[0:1000])))
