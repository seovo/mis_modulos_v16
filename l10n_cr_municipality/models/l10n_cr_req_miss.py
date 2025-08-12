from odoo import api, fields, models


class RequirementMIss(models.Model):
    _name = "l10n_cr.req_miss"
    _description = "Requirements Missed"

    name = fields.Char(string='Name')
    patent_ids = fields.Many2many('l10n_cr.patent', column1='req_miss_id', column2='patent_id', string='Patents')