from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_pe_edi_provider = fields.Selection(selection_add=[('nubefact', 'Nubefact')], ondelete={'nubefact': 'set default'})
    
    l10n_pe_edi_provider_url = fields.Char(
        string="Nubefact Url")
    l10n_pe_edi_provider_token = fields.Char(
        string="Nubefact Token")