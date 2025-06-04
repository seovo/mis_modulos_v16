from odoo import api, fields, models



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    supplier_disc = fields.Float(string="Descuento Proveedor",related='product_id.categ_id.supplier_disc')
    standard_price = fields.Float(string="Costo",related='product_id.standard_price')
    acquisition_cost = fields.Float(string="Costo de adquisición", related='product_id.acquisition_cost')
    categ_id = fields.Many2one('product.category', string="Categoria", related='product_id.categ_id')

    margin_cost_usd_jz = fields.Float(string="Precio costo USD",compute='get_margin_jz')
    margin_suggested_usd_jz = fields.Float(string="Precio sugerido de Venta", compute='get_margin_jz')
    margin_priceunit_usd_jz = fields.Float(string="Precio unitario venta USD", compute='get_margin_jz')
    margin_margin_usd_jz = fields.Float(string="Margen unitario", compute='get_margin_jz')
    pricelist_id_jz = fields.Many2one('product.pricelist',string="Tarifa", compute='get_margin_jz')



    def get_margin_jz(self):
        for record in self:

            pricelist_id = None
            sale = record.sale_line_ids
            currency = record.always_set_currency_id
            if sale:
                pricelist_id = sale[0].order_id.pricelist_id

            if not pricelist_id:
                pricelist_id = record.partner_id.property_product_pricelist


            record.pricelist_id_jz = pricelist_id.id if pricelist_id else None


            desc =  1 - ( record.supplier_disc / 100  )

            cost = record.standard_price

            if cost and cost > 0 :
                margin_cost_usd_jz = ( cost / 19 ) *  desc
            else:
                margin_cost_usd_jz = record.acquisition_cost * desc

            margin_suggested_usd_jz = 0

            if pricelist_id:
                margin_suggested_usd_jz = margin_cost_usd_jz / pricelist_id.amount_escale_sonsote if pricelist_id.amount_escale_sonsote else 0

            record.margin_cost_usd_jz = margin_cost_usd_jz
            record.margin_suggested_usd_jz = margin_suggested_usd_jz
            record.margin_priceunit_usd_jz = record.price_unit if currency ==  self.env.ref('base.USD') else record.price_unit / 19
            record.margin_margin_usd_jz = ( record.margin_suggested_usd_jz - record.margin_cost_usd_jz  ) / record.margin_cost_usd_jz  if record.margin_cost_usd_jz != 0 else 0
            

