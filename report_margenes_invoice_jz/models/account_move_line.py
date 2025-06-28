from odoo import api, fields, models



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    supplier_disc = fields.Float(string="Descuento Proveedor",related='product_id.categ_id.supplier_disc')
    standard_price = fields.Float(string="Costo",related='product_id.standard_price')
    acquisition_cost = fields.Float(string="Costo de adquisición", related='product_id.acquisition_cost')
    categ_id = fields.Many2one('product.category', string="Categoria", related='product_id.categ_id')

    margin_cost_usd_jz = fields.Float(string="Precio costo USD",compute='get_margin_jz',help=" precio unitario de la ultima factura de compra , si es MX  /tipo cambio")
    margin_suggested_usd_jz = fields.Float(string="Precio sugerido de Venta", compute='get_margin_jz',help="precio costo USD / escala")
    margin_priceunit_usd_jz = fields.Float(string="Precio unitario venta USD", compute='get_margin_jz',help="precio unitario / tipo de cambio  , si es US es el mismo precio unitario")
    margin_margin_usd_jz = fields.Float(string="Margen Unitario", compute='get_margin_jz',help="(P.Unitario  USD - precio costo USD) / P.Unitario  USD")
    pricelist_id_jz = fields.Many2one('product.pricelist',string="Tarifa", compute='get_margin_jz')
    last_purchase_move_id_jz = fields.Many2one('account.move',string="Ultima Factura Proveedor", compute='get_margin_jz')
    last_purchase_jz = fields.Char(string="Ultima Compra Proveedor",compute='get_margin_jz')
    last_purchase_partner_jz = fields.Many2one('res.partner',string="Ultimo Proveedor", compute='get_margin_jz')



    def get_margin_jz(self):
        for record in self:
            purchase_name = None
            purchase_move_id = None
            last_purchase_partner_jz = None

            pricelist_id = None

            currency = record.always_set_currency_id

            ratio = record.move_id.inv_exchange_rate_display
            if currency != self.env.ref('base.USD') and  ratio <= 1 :
                ratio = 19


            sale = record.sale_line_ids

            if sale:
                pricelist_id = sale[0].order_id.pricelist_id

            if not pricelist_id:
                pricelist_id = record.partner_id.property_product_pricelist


            record.pricelist_id_jz = pricelist_id.id if pricelist_id else None


            desc =  1 - ( record.supplier_disc / 100  )

            cost = record.standard_price

            if cost and cost > 0 :
                margin_cost_usd_jz = ( cost / ratio ) *  desc
            else:
                margin_cost_usd_jz = record.acquisition_cost * desc

            #precio unitario de la ultima factura de compra , si es MX  /tipo cambio


            if record.product_id:
                ultima_compra = self.env['account.move.line'].search(
                    [
                        ('parent_state', '=', 'posted'),
                        ('product_id', '=', record.product_id.id),
                        ('move_id.type', '=', 'in_invoice'),
                        ('date','<=',record.date)

                    ],
                    order='date DESC',
                    limit=1
                )
                if ultima_compra:

                    if ultima_compra.purchase_line_id.order_id:
                        purchase_name =  ultima_compra.purchase_line_id.order_id.name

                    last_purchase_partner_jz = ultima_compra.move_id.partner_id.id or None
                    purchase_move_id = ultima_compra.move_id.id
                    rate_sell = ultima_compra.move_id.inv_exchange_rate_display
                    if ultima_compra.move_id.currency_id != self.env.ref('base.USD') and rate_sell <= 1:
                        rate_sell = 19

                    margin_cost_usd_jz = ultima_compra.price_unit if ultima_compra.move_id.currency_id == self.env.ref('base.USD') else ultima_compra.price_unit / rate_sell


            #COSTO USD = costo * descuento , descuento= 1 - (descuento / 1000) , costo =  costo_producto /19 o costo adquision
            record.margin_cost_usd_jz = margin_cost_usd_jz

            margin_suggested_usd_jz = 0

            if pricelist_id:
                margin_suggested_usd_jz = margin_cost_usd_jz / pricelist_id.amount_escale_sonsote if pricelist_id.amount_escale_sonsote else 0



            #sugerido = precio costo USD / escala
            record.margin_suggested_usd_jz = margin_suggested_usd_jz

            #precio unitario = precio unitario / tipo de cambio  , si es US es 19
            price_unitario = record.price_unit if currency == self.env.ref('base.USD') else record.price_unit / ratio
            record.margin_priceunit_usd_jz = price_unitario

            #M. Unit = P.Unit - precio costo USD / precio costo USD
            record.margin_margin_usd_jz = ( price_unitario - record.margin_cost_usd_jz  ) / price_unitario  if price_unitario != 0 else 0
            record.last_purchase_move_id_jz = purchase_move_id

            record.last_purchase_jz = purchase_name
            record.last_purchase_partner_jz = last_purchase_partner_jz

