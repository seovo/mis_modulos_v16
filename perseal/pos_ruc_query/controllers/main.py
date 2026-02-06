# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
# import os
# import re
import time
import select
import datetime

# from collections import namedtuple
# from os import listdir
from threading import Thread, Lock

# from odoo import http
# from odoo.addons.hw_proxy.controllers import main as hw_proxy

_logger = logging.getLogger(__name__)

DRIVER_NAME = 'dbnotify'

try:
    import psycopg2
    import psycopg2.extensions
except ImportError:
    _logger.error('Osse module l10n_pe_pos depends on the psycopg2 python module')
    psycopg2 = None

class DbNotify(Thread):
    def __init__(self, db_hostname, db_port, db_name, db_username, db_password, db_notify):
        Thread.__init__(self)
        self.lock = Lock()
        self.dbnotifylock = Lock()
        self.status = {'status':'connecting', 'messages':[]}
        # self.input_dir = '/dev/serial/by-path/'
        # self.volume = 0
        self.volume_info = 'ok'
        # self.device = None
        # self.path_to_scale = ''
        # self.protocol = None

        self.db_username = db_username
        self.db_password = db_password
        self.db_name = db_name
        self.db_hostname = db_hostname
        self.db_port = db_port
        self.db_notify = db_notify
        self.conn = None
        # self.conn = psycopg2.connect(database=self.database, user=self.user, password=self.password, host=self.host)
        self.payload = {}

    def lockedstart(self):
        with self.lock:
            if not self.isAlive():
                self.daemon = True
                self.start()

    def set_status(self, status, message=None):
        if status == self.status['status']:
            if message is not None and message != self.status['messages'][-1]:
                self.status['messages'].append(message)

                if status == 'error' and message:
                    _logger.error('Scale Error: '+ message)
                elif status == 'disconnected' and message:
                    _logger.warning('Disconnected Scale: '+ message)
        else:
            self.status['status'] = status
            if message:
                self.status['messages'] = [message]
            else:
                self.status['messages'] = []

            if status == 'error' and message:
                _logger.error('Scale Error: '+ message)
            elif status == 'disconnected' and message:
                _logger.info('Disconnected Scale: %s', message)

    def get_volume(self):
        self.lockedstart()
        return self.volume

    def get_payload(self):
        self.lockedstart()
        return self.payload

    def get_volume_info(self):
        self.lockedstart()
        return self.volume_info

    def get_status(self):
        self.lockedstart()
        return self.status

    def read_dbnotify(self):
        with self.dbnotifylock:
            try:
                self.conn.commit()
                if not select.select([self.conn],[],[],5) == ([],[],[]):
                    self.conn.poll()
                    self.conn.commit()
                    while self.conn.notifies:
                        notify = self.conn.notifies.pop()
                        self.payload = notify.payload
                        _logger.info("DB NOTIFY: %s, %s, %s, %s", datetime.datetime.now(), notify.pid, notify.channel, notify.payload)

                # weight, weight_info, status = self._parse_weight_answer(p, answer)
                # if status:
                #     self.set_status('error', status)
                #     self.device = None
                # else:
                #     if weight is not None:
                #         self.weight = weight
                #     if weight_info is not None:
                #         self.weight_info = weight_info
            except Exception as e:
                self.set_status(
                    'error',
                    "Database failed: %s" %e)

    def get_connection(self):
        try:
            conn = psycopg2.connect(dbname=self.db_name, user=self.db_username, password=self.db_password, host=self.db_hostname, port=self.db_port)
            curs = conn.cursor()
            curs.execute("LISTEN %s;"%self.db_notify)
        except Exception as e:
            _logger.error(e)
            conn = None
        return conn

    def run(self):
        self.conn = None

        while True:
            if self.conn:
                # old_volume = self.volume
                self.read_dbnotify()
                if self.payload:
                    break
                # _logger.info('New Notify: %s', self.payload)
                # if self.volume != old_volume:
                #     _logger.info('New Weight: %s, sleeping %ss', self.volume, self.protocol.newWeightDelay)
                #     time.sleep(self.protocol.newWeightDelay)
                #     if self.volume and self.protocol.autoResetWeight:
                #         self.volume = 0
                # else:
                #     _logger.info('Weight: %s, sleeping %ss', self.volume, self.protocol.weightDelay)
                #     time.sleep(self.protocol.weightDelay)
            else:
                with self.dbnotifylock:
                    self.conn = self.get_connection()
                if not self.conn:
                    # retry later to support "plug and play"
                    time.sleep(10)


from odoo import models, fields, api, _

class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def read_dbnotify(self, db_hostname, db_port, db_name, db_username, db_password, db_notify):
        dbnotify_thread = DbNotify(db_hostname, db_port, db_name, db_username, db_password, db_notify)
        dbnotify_thread.lockedstart()
        dbnotify_thread.join()
        return {'payload': dbnotify_thread.payload}
        # 'info': dbnotify_thread.get_volume_info()}

# dbnotify_thread = None
# if psycopg2:
#     dbnotify_thread = DbNotify()
#     # dbnotify_thread.start()
#     hw_proxy.drivers[DRIVER_NAME] = dbnotify_thread

# class DbNotifyDriver(hw_proxy.Proxy):
#     @http.route('/hw_proxy/dbnotify_read/', type='json', auth='none', cors='*')
#     def dbnotify_read(self):
#         if dbnotify_thread:
#             return {'payload': dbnotify_thread.get_payload()}
#                     # 'info': dbnotify_thread.get_volume_info()}
#         return None
