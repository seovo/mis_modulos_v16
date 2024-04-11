from odoo import api, fields, models , _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    nro_internal_land =  fields.Char(string="Expediente")
    mz_lot            =  fields.Char(string="MZ - LOTE")
    sector  =  fields.Char()
    stage_land = fields.Selection([
        ('signed',_('Firmado'))
    ])

    m2_land = fields.Char(string="AREA (m2)")
    dues_land = fields.Float(string="Cuotas")
    value_due_land = fields.Float(string="Precio Cuotas")
    crono_land = fields.Char(string="Crono")
    days_tolerance_land  = fields.Integer(string="Gracia")
    value_mora_land = fields.Float(string="Precio Mora")
    percentage_refund_land = fields.Float(string="Porcentaje Devolucion")

    date_sign_land = fields.Date(string="Fecha Firma del Contrato")
    date_first_due_land = fields.Date(string="Fecha Primera Cuota")

    modality_land = fields.Selection([
        ('single',_('Soltero')) ,
        ('low_customer',_('Baja cliente')) ,
        ('married',_('Casado')) ,
        ('divorcee',_('Divorciado')) ,
        ('confirmer',_('Confirmador')) ,
        ('widow',_('Viudo')) ,
        ('transfer',_('Transferencia')) ,
    ])

    obs_modality_land = fields.Text(string="Observaciones")
    price_total_land = fields.Float(string="Valor del Terreno")
    price_initial_land = fields.Float(string="Inicial del Terreno")
    price_credit_land = fields.Float(string="Credito del Terreno")

    def _update_text_mz_lote(self):
        for record in self:
            mz =   None
            lote = None
            total = record.amount_total


            credit = 0

            for line in record.order_line:
                if line.product_id.manzana:
                    mz = line.product_id.manzana
                if line.product_id.lote:
                    lote = line.product_id.lote

                if line.product_id.payment_land_dues:
                    credit = line.price_total

            inicial = total - credit


            if mz or lote:
                mz_lot = (mz or '') + '-' + (lote or '')

                sql = f'''  UPDATE sale_order 
                            SET mz_lot = '{mz_lot}'  , 
                            price_total_land = {total}  ,
                            price_initial_land  = {inicial} ,
                            price_credit_land = {credit}
                            WHERE id = {record.id}  
                       '''
                self.env.cr.execute(sql)





    def _recalcule_price_land(self):
        for record in self:

            for line in record.order_line:
                if line.product_id and line.product_id.payment_land_dues:

                    line.change_product_uom_qty_land()


    def write(self,values):
        res = super().write(values)
        for record in self:
            record._update_text_mz_lote()
        return res

    def create(self,values):
        res = super().create(values)
        for record in res:
            record._update_text_mz_lote()

        return res








