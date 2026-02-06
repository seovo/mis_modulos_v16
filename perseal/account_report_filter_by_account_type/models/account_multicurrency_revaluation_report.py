# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError

from itertools import chain


class MulticurrencyRevaluationReportCustomHandler(models.AbstractModel):

    _inherit = 'account.multicurrency.revaluation.report.handler'

    # def _custom_options_initializer(self, report, options, previous_options=None):
    #     super()._custom_options_initializer(report, options, previous_options=previous_options)
    #     if options.get('currency_rates', False):
    #         options['currency_rates']['1']['rate'] = 1/options['currency_rates']['1']['rate']