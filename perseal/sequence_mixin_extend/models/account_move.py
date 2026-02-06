# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class AccountMove(models.Model):

    _inherit = "account.move"

    l10n_latam_document_number_aux = fields.Char(string='Document Number aux')

    @api.onchange('l10n_latam_document_type_id', 'l10n_latam_document_number')
    def _inverse_l10n_latam_document_number(self):
        for rec in self.filtered(lambda x: x.l10n_latam_document_type_id):
            if not rec.l10n_latam_document_number:
                rec.name = '/'
            elif rec.move_type in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']:
                l10n_latam_document_number = rec.l10n_latam_document_type_id._format_document_number(rec.l10n_latam_document_number)
                if rec.l10n_latam_document_number != l10n_latam_document_number:
                    rec.l10n_latam_document_number = l10n_latam_document_number
                rec.name = l10n_latam_document_number
            else:
                l10n_latam_document_number = rec.l10n_latam_document_type_id._format_document_number(rec.l10n_latam_document_number)
                if rec.l10n_latam_document_number != l10n_latam_document_number:
                    rec.l10n_latam_document_number = l10n_latam_document_number
                rec.name = "%s %s" % (rec.l10n_latam_document_type_id.doc_code_prefix, l10n_latam_document_number)

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get('l10n_latam_document_number', False):
                val['l10n_latam_document_number_aux'] = val.get('l10n_latam_document_number')
        res = super(AccountMove, self).create(vals)
        for line in res:
            if line.move_type in ('in_invoice', 'in_refund', 'in_receipt') and line.l10n_latam_document_number_aux != '':
                line.l10n_latam_document_number = line.l10n_latam_document_number_aux
                line.name = line.l10n_latam_document_number_aux
        return res


    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.state == 'draft' and self._origin:
            sql = """UPDATE account_move
                     SET name = '/'
                     WHERE id = %s """ % (self._origin.id)
            self.env.cr.execute(sql)
        if self.journal_id and self.journal_id.currency_id:
            new_currency = self.journal_id.currency_id
            if new_currency != self.currency_id:
                self.currency_id = new_currency
                self._onchange_currency()
        self._inverse_l10n_latam_document_number()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _assign_analytic_account(self):
        analytic_line_ids = self.env['account.analytic.line'].search([('account_id', '=', False)])
        for line in analytic_line_ids:
            if line.move_line_id.analytic_distribution != False:
                if len(line.move_line_id.analytic_distribution) == 1:
                    json_data = line.move_line_id.analytic_distribution
                    llaves = json_data.keys()
                    lista_llaves = list(llaves)
                    line.update({'account_id': int(lista_llaves[0])})

