from unittest.util import unorderable_list_difference

from odoo import api, fields, models , _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning
from odoo.tools.float_utils import float_round

class SaleOrder(models.Model):
    _inherit = 'sale.order'



    suitable_journal_ids = fields.Many2many(
        'account.journal',
        compute='_compute_suitable_journal_ids',
    )

    @api.depends('company_id')
    def _compute_suitable_journal_ids(self):
        for m in self:
            journal_type = 'sale'
            company_id = m.company_id.id or self.env.company.id
            domain = [('company_id', '=', company_id), ('type', '=', journal_type)]
            m.suitable_journal_ids = self.env['account.journal'].search(domain)

    journal_id = fields.Many2one(
        'account.journal',
        string='Diario',
        compute='_compute_journal_id', inverse='_inverse_journal_id', store=True, readonly=False, precompute=True,

        states={'draft': [('readonly', False)]},
        check_company=True,
        domain="[('id', 'in', suitable_journal_ids)]",
    )
    #required=True,

    @api.onchange('journal_id')
    def _inverse_journal_id(self):
        self._conditional_add_to_compute('company_id', lambda m: (
                not m.company_id
                or m.company_id != m.journal_id.company_id
        ))
        self._conditional_add_to_compute('currency_id', lambda m: (
                not m.currency_id
                or m.journal_id.currency_id and m.currency_id != m.journal_id.currency_id
        ))

    def _conditional_add_to_compute(self, fname, condition):
        field = self._fields[fname]
        to_reset = self.filtered(lambda move:
                                 condition(move)
                                 and not self.env.is_protected(field, move._origin)
                                 and (move._origin or not move[fname])
                                 )
        to_reset.invalidate_recordset([fname])
        #self.env.add_to_compute(field, to_reset)

    @api.depends('partner_id')
    def _compute_journal_id(self):
        for record in self.filtered(lambda r: r.journal_id.type not in r._get_valid_journal_types()):
            record.journal_id = record._search_default_journal()

    def _get_valid_journal_types(self):
        return ['sale']

    def _search_default_journal(self):


        journal_types = self._get_valid_journal_types()
        company_id = (self.company_id or self.env.company).id
        domain = [('company_id', '=', company_id), ('type', 'in', journal_types)]

        journal = None
        # the currency is not a hard dependence, it triggers via manual add_to_compute
        # avoid computing the currency before all it's dependences are set (like the journal...)
        if self.env.cache.contains(self, self._fields['currency_id']):
            currency_id = self.currency_id.id or self._context.get('default_currency_id')
            if currency_id and currency_id != self.company_id.currency_id.id:
                currency_domain = domain + [('currency_id', '=', currency_id)]
                journal = self.env['account.journal'].search(currency_domain, limit=1)

        if not journal:
            journal = self.env['account.journal'].search(domain, limit=1)

        if not journal:
            company = self.env['res.company'].browse(company_id)

            error_msg = _(
                "No journal could be found in company %(company_name)s for any of those types: %(journal_types)s",
                company_name=company.display_name,
                journal_types=', '.join(journal_types),
            )
            raise UserError(error_msg)

        return journal


    l10n_latam_available_document_type_ids = fields.Many2many('l10n_latam.document.type',
                                                              compute='_compute_l10n_latam_available_document_types')
    l10n_latam_document_type_id = fields.Many2one(
        'l10n_latam.document.type', string='Tipo de Documento', readonly=False, auto_join=True, index='btree_not_null',
        states={'posted': [('readonly', True)]}, compute='_compute_l10n_latam_document_type', store=True)

    @api.depends('journal_id', 'partner_id', 'company_id')
    def _compute_l10n_latam_available_document_types(self):
        self.l10n_latam_available_document_type_ids = False
        #for rec in self.filtered(lambda x: x.journal_id and x.l10n_latam_use_documents and x.partner_id):
        for rec in self.filtered(lambda x: x.journal_id  and x.partner_id ):
            dmx = rec._get_l10n_latam_documents_domain()
            dd = self.env['l10n_latam.document.type'].search(dmx)
            #raise ValueError(dd)
            rec.l10n_latam_available_document_type_ids = dd

    def _get_l10n_latam_documents_domain(self):
        self.ensure_one()


        dx = [
                ('country_id', '=', self.company_id.account_fiscal_country_id.id),
                ('internal_type','=','invoice'),('code','in',['01','03'])]
        if self.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code == '1':
            dx.append(('code','in',['03']))
        return dx

    @api.depends('l10n_latam_available_document_type_ids')
    def _compute_l10n_latam_document_type(self):
        for rec in self.filtered(lambda x: x.state == 'draft'):
            document_types = rec.l10n_latam_available_document_type_ids._origin

            document_types = document_types.filtered(lambda x: x.internal_type not in ['credit_note'])
            rec.l10n_latam_document_type_id = document_types and document_types[0].id


    def action_confirm(self):
        res =  super().action_confirm()

        if self.journal_id:
            wizard = self.env['sale.advance.payment.inv'].create({
                'advance_payment_method': 'delivered',
                'sale_order_ids': [(6, 0, [self.id])]
            })

            wizard.create_invoices()

            for invoice in  self.invoice_ids:
                invoice.action_post()



        return res

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        if self.l10n_latam_document_type_id:
            res.update({'l10n_latam_document_type_id':  self.l10n_latam_document_type_id.id})
        return res

class CustomStockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    company_id = fields.Many2one("res.company", string="Compañía",
                                 default=lambda self: self.env.company.id,
                                 states={'validado': [('readonly', True)]})

    name = fields.Char(
        string='Batch Transfer', default='/',
        copy=False, required=True, readonly=True)



    @api.onchange('company_id','allowed_picking_ids')
    def change_company(self):
        for record in self:
            if record.allowed_picking_ids:
                record.picking_ids = [(6,0,record.allowed_picking_ids.ids)]


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    quantity_return_jz = fields.Float(compute="get_quantity_return_jz")
    def get_quantity_return_jz(self):
        for record in self:
            quantity_total = 0
            for stock_move in record.move_ids:
                if stock_move.state == 'cancel':
                    continue
                if stock_move.scrapped:
                    continue

                quantity = stock_move.product_qty

                for move in stock_move.move_dest_ids:



                    if not move.origin_returned_move_id or move.origin_returned_move_id != stock_move:
                        continue
                    if move.state in ('partially_available', 'assigned'):
                        quantity -= sum(move.move_line_ids.mapped('reserved_qty'))

                    elif move.state in ('done'):
                        quantity -= move.product_qty

                quantity_total += quantity
            record.quantity_return_jz = quantity_total

    def return_picking_jz(self):
        return {
            "name": f"Retornar",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            # "view_id": self.env.ref('land.view_order_form_due').id,
            "res_model": "stock.return.picking",
            #"res_id": product.id,
            "target": "new",
            #"domain": [('product_tmp_id', '=', product.id)],
            "context": {
                'default_picking_id': self.id
            }

        }


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    cajas_kw = fields.Integer(compute="get_stock_kw")
    unidades_kw = fields.Integer(compute="get_stock_kw")

    @api.depends('quantity')
    def get_stock_kw(self):
        for record in self:
            cajas = 0
            unidades = 0

            if record.product_id.uom_po_id.uom_type == 'bigger':
                ratio = record.product_id.uom_po_id.factor_inv
                cajas = int(record.quantity/ratio if ratio > 0 else 0)
                unidades = record.quantity -  (cajas * ratio)

            else :
                unidades = record.quantity

            record.cajas_kw = cajas
            record.unidades_kw = unidades



            

