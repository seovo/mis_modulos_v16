# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.http import request, route



class Website(models.Model):
    _inherit = 'website'

    def _get_warehouse_available(self):

        res = super()._get_warehouse_available()
        if 'active_warehouse_id' in request.session:
            active_w = int(request.session['active_warehouse_id'])
            return active_w
        return res

        #return (
        #    self.warehouse_id.id or
        #    self.env['ir.default'].sudo()._get('sale.order', 'warehouse_id', company_id=self.company_id.id) or
        #    self.env['ir.default'].sudo()._get('sale.order', 'warehouse_id') or
        #    self.env['stock.warehouse'].sudo().search([('company_id', '=', self.company_id.id)], limit=1).id
        #3)