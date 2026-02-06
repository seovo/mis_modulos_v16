# -*- coding: utf-8 -*-

from odoo import models,fields, api,_,osv


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_account_type = fields.Selection(selection_add=[('bank', 'Banco y efectivo')])

    def _init_options_account_type(self, options, previous_options=None):
        '''
        Initialize a filter based on the account_type of the line (trade/non trade, payable/receivable).
        Selects a name to display according to the selections.
        The group display name is selected according to the display name of the options selected.
        '''
        if self.filter_account_type == 'disabled':
            return

        account_type_list = [
            {'id': 'trade_receivable', 'name': _("Por cobrar"), 'selected': True},
            {'id': 'non_trade_receivable', 'name': _("Cuentas por cobrar no comerciales"), 'selected': False},
            {'id': 'trade_payable', 'name': _("Por pagar"), 'selected': True},
            {'id': 'non_trade_payable', 'name': _("Cuentas por pagar no comerciales"), 'selected': False},
            {'id': 'bank_and_cash', 'name': "Banco y efectivo", 'selected': False},
        ]

        if self.filter_account_type == 'receivable':
            options['account_type'] = account_type_list[0:2]
        elif self.filter_account_type == 'payable':
            options['account_type'] = account_type_list[2:4]
        elif self.filter_account_type == 'bank':
            options['account_type'] = [account_type_list[4]]
        else:
            options['account_type'] = account_type_list

        if previous_options and previous_options.get('account_type'):
            previously_selected_ids = {x['id'] for x in previous_options['account_type'] if x.get('selected')}
            for opt in options['account_type']:
                opt['selected'] = opt['id'] in previously_selected_ids
                
    @api.model
    def _get_options_account_type_domain(self, options):
        all_domains = []
        selected_domains = []
        if not options.get('account_type') or len(options.get('account_type')) == 0:
            return []
        for opt in options.get('account_type', []):
            if opt['id'] == 'trade_receivable':
                domain = [('account_id.non_trade', '=', False), ('account_id.account_type', '=', 'asset_receivable')]
            elif opt['id'] == 'trade_payable':
                domain = [('account_id.non_trade', '=', False), ('account_id.account_type', '=', 'liability_payable')]
            elif opt['id'] == 'non_trade_receivable':
                domain = [('account_id.non_trade', '=', True), ('account_id.account_type', '=', 'asset_receivable')]
            elif opt['id'] == 'non_trade_payable':
                domain = [('account_id.non_trade', '=', True), ('account_id.account_type', '=', 'liability_payable')]
            elif opt['id'] == 'bank_and_cash':
                domain = [('account_id.account_type', '=', 'asset_cash')]
            if opt['selected']:
                selected_domains.append(domain)
            all_domains.append(domain)
        return osv.expression.OR(selected_domains or all_domains)
                
                
    # def get_report_informations(self, previous_options):
    #     info = super(AccountReport, self).get_report_informations(previous_options)
    #     if previous_options:
    #         info['options'].update({
    #             'cuenta_x_cobrar': previous_options.get('cuenta_x_cobrar', False),
    #             'cuenta_x_pagar': previous_options.get('cuenta_x_pagar', False),
    #         })
    #         all_column_groups_expression_totals = self._compute_expression_totals_for_each_column_group(self.line_ids.expression_ids, info['options'])
    #         lines = self._get_lines(info['options'], all_column_groups_expression_totals)
    #         report_html = self.get_html(info['options'], lines)
    #         json_friendly_column_group_totals = self._get_json_friendly_column_group_totals(all_column_groups_expression_totals)
    #         report_manager = self._get_report_manager(info['options'])
    #         info.update({
    #             'column_groups_totals': json_friendly_column_group_totals,
    #             'report_manager_id': report_manager.id,
    #             'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
    #             'main_html': report_html,
    #         })
    #     return info
    #
    # @api.model
    # def _get_options_domain(self, options, date_scope):
    #     domain = super(AccountReport, self)._get_options_domain(options, date_scope)
    #     cuentas = []
    #     if options.get('cuenta_x_cobrar', False):
    #         for cc in self.env['account.account'].search([('account_type', '=', 'asset_receivable')]):
    #             cuentas.append(cc.code)
    #     if options.get('cuenta_x_pagar', False):
    #         for cc in self.env['account.account'].search([('account_type', '=', 'liability_payable')]):
    #             cuentas.append(cc.code)
    #     if cuentas:
    #         domain.append(('account_id.code', '=', cuentas))
    #     return domain
