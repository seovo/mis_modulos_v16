# -*- coding: utf-8 -*-
import logging
import requests
import json
from datetime import datetime, timedelta
from pytz import timezone
from bs4 import BeautifulSoup


from odoo import fields, models, api
DATE_FORMAT = '%Y-%m-%d'
_logger = logging.getLogger(__name__)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
}

class ResCompany(models.Model):
    _inherit = 'res.company'


    def check_exchange_rate_today(self):
        today = datetime.now(timezone('America/Lima')).strftime(DATE_FORMAT)
        rate_today = datetime.strptime(today, DATE_FORMAT).date()
        companies = self.search([])
        exchange_rate_today = self.exchange_rate_today()
        for company in companies.filtered(lambda l: l.country_id.code == 'PE'):
            usd = self.env.ref('base.USD')
            if not usd.rate_ids.filtered(lambda l: l.name == rate_today and l.company_id == company):
                parse_results = {'PEN': (1.0, rate_today), 'USD': (exchange_rate_today,today)}
                company._generate_currency_rates(parse_results)
                _logger.info("En la compañia " + company.name + " el tipo de cambio del dolar " + str(exchange_rate_today))
            else:
                _logger.info("En la compañia " + company.name + " el tipo de cambio del dolar ya existe para el " + today)

    def exchange_rate_today(self):
        try:
            endpoint = 'https://elperuano.pe/Portal/_GetDolarActualizado'
            res = requests.get(endpoint, headers=headers, timeout=10)
            json_data = json.loads(res.text)
            return 1 / json_data['intVenta']
        except ValueError as e:
            _logger.error(e)
            try:
                endpoint = 'https://diariooficial.elperuano.pe/home/LoadUltimoStatusDolar'
                res = requests.get(endpoint, headers=headers, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")
                rows = soup.find_all('p')
                cols = [ele.text.strip() for ele in rows]
                value = cols[2][-5:]
                return 1/float(value)
            except ValueError as e:
                _logger.error(e)
