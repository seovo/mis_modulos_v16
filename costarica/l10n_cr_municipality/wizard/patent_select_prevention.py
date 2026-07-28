# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import UserError,ValidationError

TYPE = [
    ('10','Prevención 1'),
    ('5','Prevención 2')
]

class PatentSelectPreventionWizard(models.TransientModel):
    _name = "patent.select.prevention.wizard"
    _description = 'Patent | Seleccionar el tipo de prevención'


    patent_id = fields.Many2one('l10n_cr.patent',string='Patente')
    type = fields.Selection(TYPE, string='Escoja el tipo de prevención', required=True, default='10')

    def print(self):
        self.ensure_one()

        self.patent_id.generate_number_prevention(self.type)

        return self.env.ref('l10n_cr_municipality.action_report_patent_prevention').report_action(self.patent_id)

        #return (self.env['ir.actions.report'].sudo().search([('report_name', '=', 'l10n_cr_municipality.patent_prevention')], limit=1).report_action(self.patent_id.id, data=data))



