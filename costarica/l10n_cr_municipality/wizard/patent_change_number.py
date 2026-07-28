# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import UserError,ValidationError

TYPE = [
    ('10','Prevención 1'),
    ('5','Prevención 2')
]

class PatentChangeNumberWizard(models.TransientModel):
    _name = "patent.change.number.wizard"
    _description = 'Patente (Cambiar número)'

    def _get_patent(self):
        patent = self.env['l10n_cr.patent'].browse(self.env.context['active_ids'])
        return patent

    def _get_old_name(self):
        patent = self.env['l10n_cr.patent'].browse(self.env.context['active_ids'])
        return patent.name

    patent_id = fields.Many2one('l10n_cr.patent',string='Número de pantente', default=_get_patent, readonly=True, store=True)
    old_name = fields.Char(string='Nombre anterior', default=_get_old_name, store=True)
    new_name = fields.Char('Nuevo número', required=True)
    motive = fields.Text('Motivo', required=True)


    def process_change(self):
        if self.patent_id:
            message_body = "<p><b>Cambio en número de Patente</b></p>"
            message_body += (
                "<br/><b>Antes: </b> {}"
                "<br/><b>Ahora :</b> {}"
                "<br/><b>Motivo:</b> {}"
                "<br/><b>Realizó el cambio:</b> {}"
                "</p>".format(self.old_name, self.new_name, self.motive, self.create_uid.display_name)
            )
            self.patent_id.message_post(body=message_body, subtype_xmlid="mail.mt_note", message_type='comment')
            self.patent_id.name = self.new_name
            self.env.user.notify_success(message='Cambio realizado de manera exitosa!',title="BIEN! ")

