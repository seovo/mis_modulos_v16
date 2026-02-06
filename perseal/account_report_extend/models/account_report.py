# -*- coding: utf-8 -*-

from odoo import models, api


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    def get_report_informations(self, options):
        info = super(AccountReport, self).get_report_informations(options)
        if options:
            info['options'].update({
                'cuenta_x_cobrar': options.get('cuenta_x_cobrar', False),
                'cuenta_x_pagar': options.get('cuenta_x_pagar', False),
                'bank_x_cash': options.get('bank_x_cash', False),
            })
            info.update({
                'main_html': self.get_html(info['options']),
            })
        return info

    @api.model
    def _get_options_domain(self, options):
        domain = super(AccountReport, self)._get_options_domain(options)
        cuentas = []
        if options.get('cuenta_x_cobrar', False):
            for cc in self.env['account.account'].search([('user_type_id.name', '=', 'Por cobrar')]):
                cuentas.append(cc.code)
        if options.get('cuenta_x_pagar', False):
            for cc in self.env['account.account'].search([('user_type_id.name', '=', 'Por pagar')]):
                cuentas.append(cc.code)
        if options.get('bank_x_cash', False):
            for cc in self.env['account.account'].search([('user_type_id.name', '=', 'Banco y efectivo')]):
                cuentas.append(cc.code)
        if cuentas:
            domain.append(('account_id.code', '=', cuentas))
        return domain
