# from collections import defaultdict

# from odoo import api, fields, models, _
# from odoo.exceptions import UserError
# from odoo.tools import float_compare, float_round, float_is_zero, pycompat

# import logging
# _logger = logging.getLogger(__name__)    

# class StockMove(models.Model):
#     _inherit = "stock.move"

#     def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
#         self.ensure_one()
#         AccountMove = self.env['account.move']
#         quantity = self.env.context.get('forced_quantity', self.product_qty)
#         quantity = quantity if self._is_in() else -1 * quantity

#         # Make an informative `ref` on the created account move to differentiate between classic
#         # movements, vacuum and edition of past moves.
#         ref = self.picking_id.name
#         if self.env.context.get('force_valuation_amount'):
#             if self.env.context.get('forced_quantity') == 0:
#                 ref = 'Revaluation of %s (negative inventory)' % ref
#             elif self.env.context.get('forced_quantity') is not None:
#                 ref = 'Correction of %s (modification of past move)' % ref

#         move_lines = self.with_context(forced_ref=ref)._prepare_account_move_line(quantity, abs(self.value), credit_account_id, debit_account_id)
#         if move_lines:
#             date = self._context.get('force_period_date', fields.Date.context_today(self))
#             if self.picking_id:
#                 date = self.picking_id.scheduled_date
#             else:
#                 date = self.date
#             period = self.env['date.range'].search([('date_start','<=',date),('date_end','>=',date),('company_id','=',self.company_id.id)])
#             if not period.id:
#                 raise UserError(_("periodo no encontrado para la fecha ")+date)
#             new_account_move = AccountMove.sudo().create({
#                 'journal_id': journal_id,
#                 'line_ids': move_lines,
#                 'date': date,
#                 'ref': ref,
#                 'stock_move_id': self.id,
#                 'period_id':period.id
#             })
#             new_account_move.post()
#         return True