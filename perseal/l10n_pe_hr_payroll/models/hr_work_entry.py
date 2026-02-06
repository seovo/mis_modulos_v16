# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrWorkEntryType(models.Model):
    _inherit = 'hr.work.entry.type'

    extra_hours = fields.Boolean(string="Horas extra")