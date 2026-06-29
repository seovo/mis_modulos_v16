from odoo import api, fields, models
from odoo.osv import expression


class AccountMove(models.Model):
    _inherit = 'account.move'
    amount_detraccion = fields.Float(compute='get_amount_detraccion_dx')

    def get_amount_detraccion_dx(self):
        for record in self:
            total = 0
            for line in record.invoice_line_ids:
                if line.product_id:
                    if line.product_id.l10n_pe_withhold_code:
                        total += ( line.price_total * line.product_id.l10n_pe_withhold_percentage )/ 100
            record.amount_detraccion = total

    def default_get(self, fields):
        res = super(AccountMove, self).default_get(fields)
        res.update({
            'l10n_pe_edi_operation_type': '1001',

        })
        return res


