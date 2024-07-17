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

import asyncio
import logging
from bleak import BleakScanner
from mygnuhealth.lang import tr
from mygnuhealth.core import CodeNameMap, maindb
from tinydb import Query
from bleak import BleakClient
from bleak.exc import BleakError

HEART_RATE_UUID = "00002a37-0000-1000-8000-00805f9b34fb"


class BluetoothSettings():

    device_table = maindb.table('devices')

    device_map = CodeNameMap(
        mapinfo=[
            {'code': 'InfiniTime',
             'name': tr.N_('PineTime Smartwatch')},
            {'code': 'btdevice', 'name': tr.N_('Generic')},
        ])

    def get_device_addr(model):
        """Searches and retrieves the device address based on the model"""
        dev = asyncio.run(BluetoothSettings.getdev(model))
        BluetoothSettings.device_address = dev and dev.address or ''
        if dev:
            return dev.address

    async def getdev(model):
        try:
            dev = await BleakScanner.find_device_by_name(model)
        except BleakError:
            logging.info("No bt devices found")
            dev = None
        return dev

    def get_device_info(model):
        """Retrieves the device features from the local database"""
        dev_table = BluetoothSettings.device_table
        res = dev_table.search(Query()['model'] == model)
        if res:
            return res[0]

    def update_device_info(addr, model, features):
        """Updates the ID of the device based on the model"""
        dev_table = BluetoothSettings.device_table

        if (addr and model):
            logging.info(f"Address:{addr}, Model:{model},"
                         f"Features: {features}")

            dev_table.upsert(
                {'model': model,
                 'address': addr,
                 'features': features}, Query().address == addr)

    def get_measures(address, model, feature):
        """Searches and retrieves the device address based on the model"""
        measure = asyncio.run(
            BluetoothSettings.dev_measures(address, model, feature))
        return measure

    async def dev_measures(address, model, feature):
        if feature == 'hr':
            async with BleakClient(address) as client:
                logging.info(f"START: Syncing {feature} for {model}")
                heart_rate = await client.read_gatt_char(HEART_RATE_UUID)
                hr = int.from_bytes(heart_rate)
                logging.info(f"DONE: Value for {feature}: {hr}")
                return hr
        else:
            return None
