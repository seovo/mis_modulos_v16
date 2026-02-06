# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class L10nPeResCityDistrict(models.Model):
    _inherit = 'l10n_pe.res.city.district'



    country_id = fields.Many2one('res.country', string='Country', related='city_id.country_id', store=True)
