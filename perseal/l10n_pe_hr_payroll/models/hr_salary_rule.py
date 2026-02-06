#-*- coding:utf-8 -*-

from odoo import api, fields, models, _


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    regular = fields.Boolean(string='Regular')
    sctr = fields.Boolean(string='SCTR')
    onp = fields.Boolean(string='ONP')
    afp = fields.Boolean(string='AFP')
    fifth = fields.Boolean(string='5ta')