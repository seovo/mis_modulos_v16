# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    retention_show = fields.Boolean(string='Mostrar de retencion', compute='_compute_retention_amount')
    retention_percentage = fields.Float(string='Porcentaje de retencion', related='partner_id.percent_retention')
    retention_amount = fields.Float(string='Monto de retencion')
    retention_amount_spot = fields.Float(string='Monto de retencion $')

    def _prepare_retention(self):
        agent_retention = self.partner_id.agent_retention
        if self.l10n_pe_edi_operation_type != '0101':
            return {}
        if not agent_retention:
            return {}
        gravado = False
        for line in self.invoice_line_ids:
            if line.tax_ids.l10n_pe_edi_affectation_reason in ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19']:
                gravado = True
        if not gravado:
            return {}
        if self.amount_total_signed < 700:
            return {}

        MultiplierFactorNumeric = self.partner_id.percent_retention / 100
        return {
            'AllowanceChargeReasonCode': '62',
            'MultiplierFactorNumeric': MultiplierFactorNumeric,
            'Amount': round(self.amount_total * MultiplierFactorNumeric, 2),
            'BaseAmount': self.amount_total,
        }


    def _compute_retention_amount(self):
        agent_retention = self.partner_id.agent_retention
        self.retention_show = True
        if self.l10n_pe_edi_operation_type != '0101':
            self.retention_show = False
        if not agent_retention:
            self.retention_show = False
        gravado = False
        for line in self.invoice_line_ids:
            if line.tax_ids.l10n_pe_edi_affectation_reason in ['10', '11', '12', '13', '14', '15', '16', '17', '18','19']:
                gravado = True
        if not gravado:
            self.retention_show = False
        if self.amount_total_signed < 700:
            self.retention_show = False
        self.retention_amount = abs(self.amount_total * (self.retention_percentage / 100)) if self.retention_show else 0

