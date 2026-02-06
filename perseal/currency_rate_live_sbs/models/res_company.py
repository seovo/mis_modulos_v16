# -*- coding: utf-8 -*-

from pytz import timezone
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import requests
from odoo.exceptions import UserError
from odoo.tools.translate import _
import pytz
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
}
from bs4 import BeautifulSoup

from odoo import fields, models, api


SBS_DATE_FORMAT = '%d/%m/%Y'

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Fields declaration
    currency_provider = fields.Selection(selection_add=[('sbs', u"SBS Perú")], default='sbs')



    @api.model
    def set_special_defaults_on_install(self):
        ''' At module installation, set the default provider depending on the company country.'''
        all_companies = self.env['res.company'].search([])
        currency_providers = {
            'CH': 'fta',  # Sets FTA as the default provider for every swiss company that was already installed
            'MX': 'banxico',  # Sets Banxico as the default provider for every mexican company already installed
            'CA': 'boc',  # Bank of Canada
            'RO': 'bnr',
            'CL': 'mindicador',
            'PE': 'sbs',
            'AE': 'cbuae',
        }
        for company in all_companies:
            company.currency_provider = currency_providers.get(company.country_id.code, 'ecb')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('country_id') and 'currency_provider' not in vals:
                code_providers = {
                    'CH': 'fta',
                    'MX': 'banxico',
                    'CA': 'boc',
                    'RO': 'bnr',
                    'CL': 'mindicador',
                    'PE': 'sbs',
                    'AE': 'cbuae',
                }
                cc = self.env['res.country'].browse(vals['country_id']).code.upper()
                if cc in code_providers:
                    vals['currency_provider'] = code_providers[cc]
        return super(ResCompany, self).create(vals_list)

    def _parse_sbs_data(self, available_currencies):
        ''' This method is used to update the currencies by using SBS service provider.
            Rates are given against SOLES
        '''
        available_currency_names = available_currencies.mapped('name')
        if 'PEN' not in available_currency_names:
            return {}
        currency_rate = CurrencyRate(source='SUNAT')
        # aaa = datetime.now(timezone('America/Lima')).strftime(SBS_DATE_FORMAT)
        today = None
        if self.mapped('currency_next_execution_date')[0]:
            today = (self.mapped('currency_next_execution_date')[0] - timedelta(days=1)).strftime(SBS_DATE_FORMAT)
        else:
            today = (datetime.now(timezone('America/Lima')) - timedelta(days=1)).strftime(SBS_DATE_FORMAT)
        data_frame = currency_rate.get_exchange_rate('USD', today)
        rslt = {
            'PEN': (1.0, fields.Date.context_today(self.with_context(tz='America/Lima')))
        }
        if data_frame:
            rate_value = float(data_frame['sell'])
            date_rate = (datetime.strptime(today, SBS_DATE_FORMAT) + timedelta(days=1)).date()
            rate = 1.0 / rate_value if rate_value else 0
            rslt['USD'] = (rate, date_rate)
        return rslt

    def update_currency_rates_range(self, date_star, date_end):
        active_currencies = self.env['res.currency'].search([])
        currency_rate = CurrencyRate(source='SUNAT')
        while date_star < date_end:
            # available_currency_names = active_currencies.mapped('name')
            currency_rate = CurrencyRate(source='SUNAT')
            today = (date_star - timedelta(days=1)).strftime(SBS_DATE_FORMAT)
            data_frame = currency_rate.get_exchange_rate('USD', today)
            rslt = {'PEN': (1.0, date_star - timedelta(days=1))}
            if data_frame:
                rate_value = float(data_frame['sell'])
                date_rate = date_star
                rate = 1.0 / rate_value if rate_value else 0
                rslt['USD'] = (rate, date_rate)
            self._generate_currency_rates(rslt)
            date_star += timedelta(days=1)

    @api.model
    def run_update_currency(self):
        """ This method is called from a cron job to update currency rates.
        """
        records = self.search([('currency_next_execution_date', '<=', fields.Date.today())])
        if records:
            to_update = self.env['res.company']
            for record in records:
                if record.currency_interval_unit == 'daily':
                    next_update = relativedelta(days=+1)
                elif record.currency_interval_unit == 'weekly':
                    next_update = relativedelta(weeks=+1)
                elif record.currency_interval_unit == 'monthly':
                    next_update = relativedelta(months=+1)
                else:
                    record.currency_next_execution_date = False
                    continue
                if record.currency_next_execution_date < datetime.now(timezone('America/Lima')).date():
                    record.update_currency_rates_range(record.currency_next_execution_date, datetime.now(timezone('America/Lima')).date())
                    record.currency_next_execution_date = datetime.now(timezone('America/Lima'))
                record.update_currency_rates()
                record.currency_next_execution_date = datetime.now(timezone('America/Lima')) + next_update
            #     to_update += record
            # to_update.update_currency_rates()




"""
Class CurrencyRate destinada para realizar la extraccion de datos desde el servicio de SBS
"""


class CurrencyRate(object):
    ENDPOINT = 'http://www.sbs.gob.pe/app/stats/seriesH-tipo_cambio_moneda_excel.asp'
    CURRENCIES = {
        'USD': '02',
        'SEK': '55',
        'CHF': '57',
        'CAD': '11',
        'EUR': '66',
        'JPY': '38',
        'GBP': '34'
    }
    date_format = None
    source = None

    def __init__(self, date_format='%d/%m/%Y', source='SBS'):
        self.date_format = date_format
        if source in ['SBS', 'SUNAT']:
            self.source = source
        else:
            _logger.info('The {0} source is invalid.'.format(source))

    def _get_currency(self, currency):
        try:
            return self.CURRENCIES[currency]
        except KeyError:
            _logger.info('The {0} currency is invalid.'.format(currency))

    def _get_endpoint(self, currency, from_date, to_date):
        return '{0}?fecha1={1}&fecha2={2}&moneda={3}&cierre='.format(
            self.ENDPOINT, from_date, to_date, currency)

    def _data_frame(self, currency_code, from_date):
        # Valid dates
        self._valid_date(from_date)
        # self._valid_date(to_date)
        # Dates
        # date = datetime.strptime(date, '%d/%m/%Y')
        from_date=datetime.now(pytz.timezone('America/Lima')).strftime('%d/%m/%Y')
        date_1 = datetime.strptime(from_date, '%d/%m/%Y') - timedelta(days=3)
        # to_date = datetime.strptime(to_date, '%d/%m/%Y')
        date_2 = datetime.strptime(from_date, '%d/%m/%Y')
        # Get endpoint
        endpoint = self._get_endpoint(currency_code,
                                      date_1.strftime('%d/%m/%Y'),
                                      date_2.strftime('%d/%m/%Y'))
        # Create data frames
        # endpoint = "https://www.sbs.gob.pe/app/stats/seriesH-tipo_cambio_moneda_excel.asp?fecha1=12/01/2025&fecha2=16/01/2025&moneda=02&cierre="
        res = requests.get(endpoint, headers=headers,timeout=30)
        _logger.info('respuesta:'+ str(res.text))
        soup = BeautifulSoup(res.text, "html.parser")
        # soup.find("table", {"class": "skuBestPrice"}).text

        data = []
        table = soup.find('table')
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])  # Get rid of empty values

        if len(data) > 1:
            return data
        return None

    @staticmethod
    def _convert_source(data_frame):
        idx = []
        for i in data_frame.index:
            i = i + timedelta(days=1)
            idx.append(i.strftime('%d/%m/%Y'))
        return idx

    @staticmethod
    def _to_dict(df):
        data = {}
        df.pop(0)
        # for d in df.itertuples():
        for d in df:
            # d = list(d)
            data[d[0]] = {
                'buy': '{:.3f}'.format(float(d[2])),
                'sell': '{:.3f}'.format(float(d[3]))
            }
        return data

    @staticmethod
    def _valid_date(pdate):
        date = datetime.strptime(pdate, '%d/%m/%Y')
        if date.year < 2000:
            _logger.info('Information available from the 2000 year.')
        return True

    def get_exchange_rate(self, currency, from_date):
        # today = from_date or datetime.now(timezone('America/Lima')).strftime(SBS_DATE_FORMAT)
        currency_code = self._get_currency(currency)
        data_frame = self._data_frame(currency_code, from_date)
        if data_frame is not None:
            data = self._to_dict(data_frame)
            # if from_date:
            # date = datetime.strptime(today, '%d/%m/%Y') - timedelta(days=1)
            # aux = date.strftime(self.date_format)
            aux = list(data.keys())
            return data[aux[-1]]
            # return data
        else:
            _logger.info('No data found.')
