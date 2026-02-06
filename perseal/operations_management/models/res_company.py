# -*- coding: utf-8 -*-

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    company_partner_category_cedente_id = fields.Many2one(
        comodel_name='res.partner.category',
        string='Cedente',
    )
    company_partner_category_deudor_id = fields.Many2one(
        comodel_name='res.partner.category',
        string='Deudor',
    )
    company_partner_category_proveedor_id = fields.Many2one(
        comodel_name='res.partner.category',
        string='Proveedor',
    )
    company_partner_category_beneficiario_id = fields.Many2one(
        comodel_name='res.partner.category',
        string='Beneficiario',
    )
    company_partner_category_titular_id = fields.Many2one(
        comodel_name='res.partner.category',
        string='Titular',
    )
