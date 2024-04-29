from odoo import api, fields, models , _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    nro_internal_land =  fields.Char(string="Expediente")
    mz_lot            =  fields.Char(string="MZ - LOTE")
    sector  =  fields.Char()
    stage_land = fields.Selection([
        ('signed',_('Firmado'))  ,
        ('cancel',_('Resuelto o Cancelado'))
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

    seller_land = fields.Selection([('villa','Villa del Sur'),('roque','Roque')],required=True,string="Proveedor Terreno")


    #esto es para importar
    journal_import_id = fields.Integer()
    price_unit_import = fields.Float()
    invoice_payment_import_id = fields.Integer()
    invoice_date_import =  fields.Date()
    journal_id = fields.Many2one('account.journal',string="Diario")
    move_separation_land_id = fields.Many2one('account.move',string='Factura Separación')

    stage_payment_lan = fields.Selection([
        ('initial','Inicial'),
        ('dues','Cuotas'),
        ('completed','Completada')
    ],compute='_get_stage_payment_land',store=True)

    last_payment_date_land = fields.Date(string="Ultima Fecha de Pago",compute="get_last_payment_date_land",store=True)
    next_payment_date_land = fields.Date(string="Proxima Fecha de Pago", compute="get_last_payment_date_land",store=True)
    days_expired_land = fields.Date(string="Proxima Fecha de Pago", compute="get_last_payment_date_land")
    type_periodo_invoiced  = fields.Selection([('half_month','Quincenal'),('end_month','Fin de Mes')],
                                              string="Periodo de Facturación",required=True)


    @api.depends('invoice_ids','invoice_ids.state')
    def get_last_payment_date_land(self):
        for record in self:
            date = None
            for invoice in record.invoice_ids:
                if invoice.state == 'posted':
                    if invoice.invoice_date:
                        if not date:
                            date = invoice.invoice_date
                        else:
                            if invoice.invoice_date > date:
                                date = invoice.invoice_date

            record.last_payment_date_land = date

            date_next = None

            if date:
                date_next = date +  relativedelta(months=1)

            record.next_payment_date_land = date_next

            diff_days  = 0

            date_now = fields.Datetime.now().date

            if date_next and  date_now < date_next:
                diff_days = (date_next - date_now).days

            record.days_expired_land = diff_days



    @api.depends('order_line','order_line.product_id','note')
    def _get_stage_payment_land(self):
        for record in self:
            stage = None

            total_initial = 0
            total_initial_invoiced = 0

            total_dues = 0
            total_dues_invoiced = 0
            for line in record.order_line:
                if line.product_id.is_advanced_land:
                    total_initial += line.product_uom_qty
                    total_initial_invoiced += line.qty_invoiced

                if line.product_id.payment_land_dues:
                    total_dues += line.product_uom_qty
                    total_dues_invoiced +=   line.qty_invoiced
            if total_initial_invoiced < total_initial :
                stage = 'initial'

            if not stage:
                if total_dues_invoiced < total_dues:
                    stage = 'dues'
                if total_dues_invoiced == total_dues:
                    stage = 'completed'

            record.stage_payment_lan = stage




    def show_m2_land(self):

        object = self.env['product.attribute'].search([('type_land','=','m2')])

        return {
            "name": f"METRADO",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "product.attribute",
            "res_id": object.id,
            "target": "new",


        }

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

        self.check_adelanto()

        return res

    @api.model
    def create(self,vals):
        res = super().create(vals)
        res.check_adelanto()
        return res


    def check_adelanto(self):
        for record in self:
            if record.move_separation_land_id:
                if len(record.order_line) == 2:
                    for line in record.order_line:
                        if line.product_id.is_advanced_land:
                            clone_line = line.copy(default={'order_id': record.id , 'product_id': record.move_separation_land_id.invoice_line_ids[0].product_id.id })
                            clone_line.price_unit = record.move_separation_land_id.amount_untaxed
                            line.price_unit = line.price_unit - clone_line.price_unit



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


    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        #if self.journal_import_id:
        #    res['journal_id'] = 10

        if self.journal_id:
            res['journal_id'] = self.journal_id.id

        #if self.invoice_payment_import_id:
        #    res['invoice_payment_term_id'] = self.invoice_payment_import_id

        #if self.invoice_date_import:
        #    res['invoice_date'] = self.invoice_date_import

        return res


    def action_confirm(self):
        res = super().action_confirm()
        if self.move_separation_land_id:
            for line in self.order_line:
                for linex in self.move_separation_land_id.invoice_line_ids:
                    if linex.product_id == line.product_id and line.price_unit == linex.price_unit :
                        line.invoice_lines = [(4, linex.id)]
                        self.move_separation_land_id.is_separation_land = False


        return res






