from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)


class CustomStockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_id = fields.Many2one(
        'account.move', string='Comprobante', compute="_compute_other_data")
    invoice_amount = fields.Float(
        string='Monto', compute="_compute_other_data")
    sale_user_id = fields.Many2one(
        'res.users', string='Vendedor', related="sale_id.user_id")

    def _compute_other_data(self):
        for record in self:
            if record.picking_type_id.code == 'outgoing':
                if len(record.sale_id.invoice_ids) > 0:
                    record.invoice_id = record.sale_id.invoice_ids.filtered(
                        lambda p: p.move_type == 'out_invoice')[0]
                    record.invoice_amount = record.sale_id.invoice_ids[0].amount_total

                else:
                    record.invoice_id = False
                    record.invoice_amount = 0
            else:
                record.invoice_id = False
                record.invoice_amount = 0


class CustomStockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    company_id = fields.Many2one("res.company", string="Compañía",
                                 default=lambda self: self.env.company.id,
                                 states={'validado': [('readonly', True)]})
    company_partner_id = fields.Many2one(
        "res.partner", related="company_id.partner_id", readonly=True)

    # modalidad_transporte = fields.Selection(
    #     selection="_list_modalidad_transporte", string="Modalidad de Transporte")

    # def _list_modalidad_transporte(self):
    #     modalidad_transporte_objs = self.env["gestionit.modalidad_transporte"].search([
    #     ])
    #     return [(mt.code, mt.name) for mt in modalidad_transporte_objs]

    # TRANSPORTE PRIVADO
    conductor_privado_partner_id = fields.Many2one(
        "res.partner", string="Conductor", states={'validado': [('readonly', True)]})
    vehiculo_privado_id = fields. Many2one(
        "fleet.vehicle", string="Vehículo", states={'validado': [('readonly', True)]})

    # TRANSPORTE PÚBLICO
    transporte_partner_id = fields.Many2one(
        "res.partner", string="Empresa Transportista", states={'validado': [('readonly', True)]})
    conductor_publico_id = fields.Many2one("res.partner", string="Conductor", states={
                                           'validado': [('readonly', True)]})
    vehiculo_publico_id = fields.Many2one(
        "fleet.vehicle", string="Vehículo", states={'validado': [('readonly', True)]})

    qty_documents = fields.Integer(
        string='Documentos', compute="_compute_totals")
    qty_partners = fields.Integer(string='Clientes', compute="_compute_totals")
    total_weight = fields.Float(
        string='Peso total', digits=(9, 2), compute="_compute_totals")
    total_amount = fields.Float(
        string='Valorizado', digits=(9, 2), compute="_compute_totals")

    def _compute_totals(self):
        for record in self:
            documents = len(record.picking_ids)
            partners = len(record.picking_ids.mapped('partner_id'))
            weight = 0
            total = 0

            for pick in record.picking_ids:
                weight += pick.shipping_weight
                total += pick.invoice_amount

            record.qty_documents = documents
            record.qty_partners = partners
            record.total_weight = weight
            record.total_amount = total

    def group_stock_picking_lines(self):

        # spb = self.env['stock.picking.batch'].browse(id)

        data = []
        product_ids = self.move_line_ids.mapped('product_id')
        for product in product_ids:
            qty = 0
            product_id = product
            for line in self.move_line_ids:
                if product.id == line.product_id.id:
                    qty += line.qty_done

            data.append({"product": product_id, "qty": qty,
                         "uom_id": line.product_uom_id})

        return data
        # # Armar el query
        # rtbi_query = """
        # SELECT amount, date, amount_ars FROM report_trial_balance_initial_amount rtb WHERE rtb.account_id = %s AND rtb.state = 'done' AND date < %s
        # """
        # # Tupla de parametros
        # query_update_account_params = (
        #     acc.account_id.id,
        #     date_init,
        # )

        # # Ejecucion
        # # aca haces el query con los parametros como tupla
        # self.env.cr.execute(rtbi_query, query_update_account_params)

        # # Resultados
        # rtbi = self.env.cr.fetchone()
