from odoo import api, fields, models , _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty

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
    ],string="Modalidad")

    obs_modality_land = fields.Text(string="Observaciones")
    price_total_land = fields.Float(string="Valor del Terreno")
    price_initial_land = fields.Float(string="Inicial del Terreno")
    price_credit_land = fields.Float(string="Credito del Terreno")

    note = fields.Text()
    recalcule_and_save_total_land = fields.Boolean(default=True,string="Recalcular Montos")

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
            if record.recalcule_and_save_total_land:
                record._update_text_mz_lote()

        return res
    '''
    def create(self,vals):
        res = super().create(vals)
        for record in res:
            if record.recalcule_and_save_total_land:
                record._update_text_mz_lote()


        return res
    '''
    def _get_invoiceable_lines(self, final=False):
        """Return the invoiceable lines for order `self`."""
        down_payment_line_ids = []
        invoiceable_line_ids = []
        pending_section = None
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        quantity_lines_invoice = 0
        for line in self.order_line:
            if line.display_type == 'line_section':
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue

            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if line.is_downpayment:
                    continue

            quantity_lines_invoice += 1



        for line in self.order_line:



            if line.display_type == 'line_section':
                # Only invoice the section if one of its lines is invoiceable
                pending_section = line
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue

            if quantity_lines_invoice > 1 and line.product_id.payment_land_dues:
                continue

            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if line.is_downpayment:
                    # Keep down payment lines separately, to put them together
                    # at the end of the invoice, in a specific dedicated section.
                    down_payment_line_ids.append(line.id)
                    continue
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = None
                invoiceable_line_ids.append(line.id)



        return self.env['sale.order.line'].browse(invoiceable_line_ids + down_payment_line_ids)







