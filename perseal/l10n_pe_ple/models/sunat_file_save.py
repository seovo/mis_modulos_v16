# coding: utf-8

from odoo import fields, models, _


class SunatFileSave(models.TransientModel):
    _name = 'sunat.file.save'
    _description = "Sunat File Save"

    def get_name_txt(self):
        return _('Output filename')

    output_name = fields.Char('Output filename', size=128, default=get_name_txt)
    output_file = fields.Binary('Output file', readonly=True, filename="output_name")

    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}
