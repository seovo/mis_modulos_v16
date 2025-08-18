# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import UserError,ValidationError

CATEG = {
    "A": "A",
    "B1": "B1",
    "B2": "B2",
    "C": "C",
    "D1": "D1",
    "D2": "D2",
    "E1A": "E1A",
    "E1B": "E1B",
    "E2": "E2",
    "E3": "E3",
    "E4": "E4",
    "E5": "E5"
}

class PatentCertificateAutorizationWizard(models.TransientModel):
    _name = "patent.certificate.autorization.wizard"
    _description = 'Autorización para impresión de certificados'


    patent_id = fields.Many2one('l10n_cr.patent',string='Patente')
    aprobado_por = fields.Many2one('hr.employee',string='Aprobador por: ', required=True)
    autorizado_por = fields.Many2one('hr.employee', string='Autorizado por: ', required=True)

    def print_certificate(self):
        data = {
            'aprobado_por': self.aprobado_por.id,
            'autorizado_por': self.autorizado_por.id,
        }
        self.patent_id.write(data)
        self.ensure_one()
        if self.patent_id.state == "approved":
            if self.patent_id.type_id.name == "Licores":
                self.patent_id.code_letter = CATEG[self.patent_id.category_liqueur]
                return self.env.ref("l10n_cr_municipality.patent_certificate_licor").report_action(self.patent_id)
            else:
                return self.env.ref("l10n_cr_municipality.patent_certificate").report_action(self.patent_id)
