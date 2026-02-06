# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models, api, _, _lt

import logging

_logger = logging.getLogger( __name__ )


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _logger_info(self, xml):
        _logger.info(xml)