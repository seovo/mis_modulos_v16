# -*- coding: utf-8 -*-

from odoo import fields, models, _


class PosConfig(models.Model):
    _inherit = "pos.config"


    default_country_id = fields.Many2one(comodel_name='res.country', string=_('Default Country'), compute='_get_default_pos_country')
    default_state_id = fields.Many2one(comodel_name='res.country.state', string=_('Default State'), compute='_get_default_pos_country')
    default_city_id = fields.Many2one(comodel_name='res.city', string=_('Default City'), compute='_get_default_pos_country')
    default_district_id = fields.Many2one(comodel_name='l10n_pe.res.city.district', string=_('Default District'), compute='_get_default_pos_country')


    def _get_default_pos_country(self):
        for config in self:
            config.default_country_id = self.env.ref('base.pe').id
            config.default_state_id = self.env.ref('base.state_pe_01').id
            config.default_city_id = self.env.ref('l10n_pe.city_pe_0101').id
            config.default_district_id = self.env.ref('l10n_pe.district_pe_010101').id
