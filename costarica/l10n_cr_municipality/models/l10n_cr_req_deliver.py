from odoo import api, fields, models


class RequirementDeliver(models.Model):
    _name = "l10n_cr.req_deliver"
    _description = "Requirements Delivered"

    name = fields.Char(string='Name')
    patent_ids = fields.Many2many('l10n_cr.patent', column1='req_deliver_id', column2='patent_id', string='Patents')
    
