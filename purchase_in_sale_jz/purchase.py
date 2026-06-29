from odoo import models, exceptions, fields , api , _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    sale_id  = fields.Many2one('sale.order')
    partner_ref = fields.Char()
    order_related_id = fields.Many2one('purchase.order',related='order_id',string="Compra")
    #partner_id = fields.Many2one('res.partner')

    @api.model
    def create(self,vals):
        if 'sale_id' in vals:
            sale = self.env['sale.order'].search([('id','=',vals['sale_id'])])
            partner_id = sale.partner_id.id

            if not  sale:
                raise UserError('Guarde la Venta primero')

            if 'partner_id' in vals:
                if vals['partner_id']:
                    partner_id = vals['partner_id']

            dm = [('id', 'in', sale.purchase_ids.ids), ('partner_id', '=', partner_id), ('state', '=', 'draft')]
            create_purchase = {'partner_id': partner_id}

            if 'partner_ref' in vals:
                dm.append(('partner_ref','=',vals['partner_ref']))
                create_purchase.update({'partner_ref': vals['partner_ref']})
            else:
                dm.append(('partner_ref', '=', False))
                create_purchase.update({'partner_ref': False})


            if not sale.purchase_ids:
                purchase = self.env['purchase.order'].create(create_purchase)
                vals['order_id'] = purchase.id
            else:

                purchase = self.env['purchase.order'].search(dm)

                if not purchase:
                    #raise ValueError([dm,sale.partner_id])
                    purchase = self.env['purchase.order'].create(create_purchase)
                    vals['order_id'] = purchase.id


                vals['order_id'] = purchase.id


            #raise ValueError(vals)

        res = super().create(vals)
        return res
