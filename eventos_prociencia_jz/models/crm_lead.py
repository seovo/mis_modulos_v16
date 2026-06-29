# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.osv import expression


class CrmLead(models.Model):
    _inherit = 'crm.lead'
    place_event_id = fields.Many2one('place.event', string="Ubicacion")
    date_event = fields.Datetime(string='Fecha Evento')
    note_event_start = fields.Text(string="Listado Inicial")

    def action_new_quotation(self):
        res = super().action_new_quotation()

        res['context']['default_note_event_start'] = self.note_event_start
        res['context']['default_name_event'] = self.name
        res['context']['default_crm_lead_id'] = self.id
        res['context']['default_state'] = 'draft'


        if self.place_event_id:
            res['context']['default_place_event_id'] = self.place_event_id.id
        if self.date_event:
            res['context']['default_date_event'] = self.date_event


        product = self.env['product.product'].search([('is_product_event','=',True)])
        if product:
            res['context']['default_order_line'] = [(0,0,{
                'product_id': product.id ,
                'name': product.name ,
                #'company_id': self.env.company.id ,
                'product_uom_qty': 1 ,
                'price_unit': self.expected_revenue ,
                'product_uom': product.uom_id.id,
                'customer_lead': 0
            })]






        return res