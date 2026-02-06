# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    input_afp = fields.Selection(string='AFP', selection=[('HS', 'HABITAT SALDO'),
                                                          ('HF', 'HABITAT FLUJO'),
                                                          ('IS', 'INTEGRA SALDO'),
                                                          ('IF', 'INTEGRA FLUJO'),
                                                          ('PMS', 'PRIMA SALDO'),
                                                          ('PMF', 'PRIMA FLUJO'),
                                                          ('PFS', 'PROFUTURO SALDO'),
                                                          ('PFF', 'PROFUTURO FLUJO'),
                                                          ('SNP', 'SNP')])

    input_eps = fields.Selection(string='EPS', selection=[('no', 'NO'),
                                                          ('yes', 'SI')], default='no')
    cuspp = fields.Char(string="CUSPP")

    bank_account_id_cts = fields.Many2one('res.partner.bank', string='Número de Cuenta Bancaria CTS')