from odoo import api, fields, models , _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta , date
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def write(self,values):
        res = super().write(values)


        if  'report_lot_land_line_id' in values and not self.order_line:
            if self.report_lot_land_line_id:

                amount_total = self.report_lot_land_line_id.price

                if self.inicial_lot_set > 0:
                    amount_total -= self.inicial_lot_set

                self.order_line += self.env['sale.order.line'].new({
                    'product_id': self.report_lot_land_line_id.product_tmp_id.product_variant_ids.id,
                    'price_unit': amount_total / self.report_lot_land_line_id.product_tmp_id.dues_qty,
                    'product_uom_qty': self.report_lot_land_line_id.product_tmp_id.dues_qty

                })

            if self.inicial_lot_set and self.report_lot_land_line_id:
                if self.inicial_lot_set > 0:
                    self.order_line += self.env['sale.order.line'].new({
                        'product_id': self.report_lot_land_line_id.product_tmp_id.optional_product_ids[
                            0].product_variant_ids.id,
                        'price_unit': self.inicial_lot_set,
                        'product_uom_qty': 1
                    })




        return res

    # esto verifica si existe una factura de separacion
    def check_adelanto(self):
        for record in self:

            line_set = None
            amount_set = None

            if record.move_separation_land_id:
                if len(record.order_line) == 2:
                    for line in record.order_line:
                        if line.product_id.is_advanced_land:
                            product_id = record.move_separation_land_id.invoice_line_ids[0].product_id

                            clone_line = line.copy(default={
                                'order_id': record.id,
                                'product_id': product_id.id,
                                'tax_id': [(6, 0, product_id.taxes_id.ids)]
                            })
                            clone_line.price_unit = record.move_separation_land_id.amount_total

                            price_unit_new = line.price_unit - record.move_separation_land_id.amount_total
                            line.price_unit = price_unit_new * 1

                            line_set = line
                            amount_set = price_unit_new * 1

                            record.move_separation_land_id.stage_separation_land = 'initial'

                            # raise ValueError(line.price_unit)

            if line_set:
                line_set.price_unit = amount_set

                # raise ValueError(line_set.price_unit)
            # raise ValueError(line_set)

    def _get_invoiceable_lines(self, final=False):

        if self.sale_line_payment_id:
            return self.sale_line_payment_id



        """Return the invoiceable lines for order `self`."""
        down_payment_line_ids = []
        invoiceable_line_ids = []
        pending_section = None
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        quantity_lines_invoice = 0

        have_separation = False

        for line in self.order_line:
            if line.display_type == 'line_section':
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue

            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                if line.is_downpayment:
                    continue

            if line.product_id.is_separation_land:
                have_separation = True

            quantity_lines_invoice += 1


        for line in self.order_line:



            if line.display_type == 'line_section':
                # Only invoice the section if one of its lines is invoiceable
                pending_section = line
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue

            #if quantity_lines_invoice > 1 and line.product_id.payment_land_dues:
            #    continue

            if have_separation and not line.product_id.is_separation_land:
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

        res = self.env['sale.order.line'].browse(invoiceable_line_ids + down_payment_line_ids)



        return res

    def _prepare_invoice(self):
        self.get_last_payment_date_land()
        res = super()._prepare_invoice()
        if self.journal_id:
            res['journal_id'] = self.journal_id.id

        if self.days_expired_land:
            res['days_expired_land'] = self.days_expired_land
            res['value_mora_land'] = self.value_mora_land



        return res

    def print_report_schedule_excell(self):
        return self.env['report.schedule.land'].print_report_schedule_excell(self)

    def action_confirm(self):
        self.verifi_mz_lot()
        self.check_adelanto()
        res = super().action_confirm()
        if self.move_separation_land_id:
            for line in self.order_line:
                for linex in self.move_separation_land_id.invoice_line_ids:
                    if linex.product_id == line.product_id and line.price_unit == linex.price_unit :
                        line.invoice_lines = [(4, linex.id)]
                        #self.move_separation_land_id.is_separation_land = False


        return res