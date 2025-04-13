# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

from odoo import models , fields

class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking',  'portal.mixin']

    signature = fields.Image(
        string="Firma",
        copy=False, attachment=True, max_width=1024, max_height=1024)


    def action_preview_stock_picking(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    def _compute_access_url(self):
        super()._compute_access_url()
        for order in self:
            order.access_url = f'/transfer_detail/{order.id}'
            #order.access_url = f'/transfer_detail/download_stock_pdf/{order.id}'

    def _get_report_base_filename(self):
        self.ensure_one()
        return self.name

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: