from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    acquisition_cost = fields.Float(string="Costo de adquisición")
    acq_exchange_rate = fields.Float(string="Tipo de cambio de adquisición")


class ProductCategory(models.Model):
    _inherit = 'product.category'
    supplier_disc = fields.Float(string="	Descuento %")

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    is_escale_sonsotec = fields.Boolean(string="Es una Escala")
    amount_escale_sonsote = fields.Float(string='Monto Escala')
    use_discount_category_sonsotec =  fields.Boolean(string="Usar Descuento de Categoria")
    use_acquisition_cost  = fields.Boolean(string="Usar Precio : Costo de Adquisición")
    use_rate_acquisition_cost  = fields.Boolean(string="Usar Tipo de cambio Especial")

    @api.onchange('is_escale_sonsotec')
    def change_is_escale_sonsotec(self):
        for record in self:
            if record.is_escale_sonsotec:
                record.use_discount_category_sonsotec = True
            if record.currency_id ==  self.env.ref('base.USD'):
                record.use_acquisition_cost = True
            if record.currency_id == self.env.ref('base.MXN'):
                record.use_rate_acquisition_cost = True


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_price_value_tarifas(self,product):
        res = None
        price_unitx0 = None
        price_unitx = None

        tarifa = self.order_id.pricelist_id
        if tarifa.is_escale_sonsotec and product:
            price_unit = product.acquisition_cost if tarifa.use_acquisition_cost else product.list_price

            price_unitx0 = price_unit - (price_unit * product.categ_id.supplier_disc / 100)

            price_unitx = price_unitx0 / tarifa.amount_escale_sonsote if tarifa.amount_escale_sonsote != 0 else 0



            # ES USD
            if tarifa.use_acquisition_cost:
                res = price_unitx
            else:
                ##########

                product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id,
                                       date=self.order_id.date_order, uom=self.product_uom.id)
                final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(
                    product or self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)

                base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id,
                                                                                                   self.product_uom_qty,
                                                                                                   self.product_uom,
                                                                                                   self.order_id.pricelist_id.id)

                ######
                res = price_unitx
                to_currency = self.order_id.pricelist_id.currency_id
                if currency != to_currency:
                    if tarifa.use_rate_acquisition_cost:
                        rate = self.env['res.currency.special'].search([('from_currency', '=', currency.id),
                                                                        ('to_currency', '=', to_currency.id)], limit=1)
                        if not rate:
                            raise ValueError('CONFIGURE MONEDA ESPECIAL')

                        rate = rate.factor

                        # raise ValueError(price_unitx)
                        res = price_unitx / rate if rate != 0 else 0
                    else:
                        res = currency._convert(
                            price_unitx, self.order_id.pricelist_id.currency_id,
                            self.order_id.company_id or self.env.company,
                            self.order_id.date_order or fields.Date.today())

            # record.price_unit = price_unitx

        #if not res:
        #    raise ValueError([res, tarifa, tarifa.use_acquisition_cost, price_unitx0, price_unitx])


        return res

    def _get_display_price(self, product):
        res = super()._get_display_price(product)
        return res

        if product:
            resx = self.get_price_value_tarifas(product)
            if resx:
                res = resx

        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def force_update_price_tarifas_jz(self):
        return
        for line in self.order_line:
            if line.product_id:
                res = line.get_price_value_tarifas(line.product_id)
                if res:
                    line.price_unit = res
                else:
                    tarifa = line.order_id.pricelist_id
                    #raise ValueError([tarifa,tarifa.is_escale_sonsotec])
