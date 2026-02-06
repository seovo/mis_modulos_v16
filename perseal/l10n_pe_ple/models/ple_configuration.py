# coding: utf-8

from odoo import fields, models, api


class PleConfiguration(models.Model):
    _name = "ple.configuration"
    _description = "Ple Configuration Base"

    _sql_constraints = [('report_type_uniq', 'unique(company_id, report_type)', 'Solo se permite un tipo de reporte por compañia.'),]

    @api.onchange('report_type')
    def _onchange_accounts_ids(self):
        if self.report_type in ('8.1', '8.2'):
            return {'domain': {
                'accounts_ids': [('company_id', '=', self.company_id.id), ('internal_type', '=', 'payable'),
                                 ('code', 'not like', '40%')],
                'journals_ids': [('company_id', '=', self.company_id.id), ('type', '=', 'purchase')]
            }
            }
        if self.report_type == '14.1':
            return {'domain': {
                'accounts_ids': [('company_id', '=', self.company_id.id), ('internal_type', '=', 'receivable')],
                'journals_ids': [('company_id', '=', self.company_id.id), ('type', '=', 'sale')]
            }
            }
        else:
            return {'domain': {'accounts_ids': [('company_id', '=', self.company_id.id)]}}

    @api.model
    def _get_account_domain(self):
        if self.report_type == '8.1':
            return "[('company_id','=',company_id),('internal_type', '=', 'payable')]"
        elif self.report_type == '8.2':
            return "[('company_id','=',company_id),('internal_type', '=', 'payable')]"
        elif self.report_type == '14.1':
            return "[('company_id','=',company_id),('internal_type', '=', 'receivable')]"
        else:
            return "[('company_id','=',company_id)]"

    @api.model
    def _get_journal_domain(self):
        for record in self:
            if record.report_type in ('8.1', '8.2'):
                return "[('company_id','=',company_id),('type', '=', 'purchase')]"
            elif record.report_type == '14.1':
                return "[('company_id','=',company_id),('type', '=', 'sale')]"
            else:
                return "[('company_id','=',company_id)]"

    company_id = fields.Many2one('res.company', 'Company', required=True, ondelete='cascade',
                                 default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    report_type = fields.Selection('_get_sunat_ple_type', 'Report type', required=True)
    accounts_ids = fields.Many2many('account.account', 'l10n_pe_conf_account', 'conf_id',
                                    'account_id', 'Target accounts',
                                    domain=_get_account_domain)
    journals_ids = fields.Many2many('account.journal', 'l10n_pe_conf_journal', 'conf_id',
                                    'journal_id', 'Target journals',
                                    domain=_get_journal_domain)
    ##### CAMPOS LIBRO 5.3
    account_chart_code = fields.Selection('_get_account_chart_type', string="Account Chart", default='01')
    ##### CAMPOS 8.1, 8.2
    purchase_domain = "[('company_id','=',company_id),('type_tax_use', '=', 'purchase')]"

    l10n_pe_txbl_txbl_vat = fields.Many2many('account.tax', 'ple_config_tax_txbl_txbl', 'ple_config_txbl_txbl', 'tax_txbl_txbl', string='Taxable for Taxable and Export', domain=purchase_domain)
    l10n_pe_txbl_txbl_notxbl_vat = fields.Many2many('account.tax', 'ple_config_tax_txbl_txbl_notxbl', 'ple_config_txbl_txbl_notxbl', 'tax_txbl_txbl_notxbl', string='Taxable for Taxable, Non Taxable and Export',
                                                   domain=purchase_domain)
    l10n_pe_txbl_notxbl_vat = fields.Many2many('account.tax', 'ple_config_tax_txbl_notxbl', 'ple_config_txbl_notxbl', 'tax_txbl_notxbl', string='Taxable for Non Taxable and Export',
                                              domain=purchase_domain)
    l10n_pe_notxbl_vat = fields.Many2many('account.tax', 'ple_config_tax_notxbl', 'ple_config_notxbl', 'tax_notxbl', string='Non Taxable', domain=purchase_domain)
    l10n_pe_purchase_excise_tax = fields.Many2many('account.tax', 'ple_config_tax_purchase_excise', 'ple_config_purchase_excise', 'tax_purchase_excise', string='Purchase Excise Tax', domain=purchase_domain)
    l10n_pe_purchase_other_tax = fields.Many2many('account.tax', 'ple_config_tax_purchase_other', 'ple_config_purchase_other', 'tax_purchase_other', string='Purchase Other Tax', domain=purchase_domain)
    pastic_bag_purchase_tax = fields.Many2many('account.tax', 'ple_config_tax_bag_purchase', 'ple_config_bag_purchase', 'tax_bag_purchase', string='Plastic Bag Tax Purchase',
                                              domain=[('type_tax_use', '=', 'purchase')])
    ##### campos 14.1
    sales_domain = "[('company_id','=',company_id),('type_tax_use', '=', 'sale')]"

    l10n_pe_exportation_vat = fields.Many2many('account.tax', 'ple_config_tax_exportation', 'ple_config_exportation', 'tax_exportation', string='Exportation', domain=sales_domain)
    l10n_pe_taxable_vat = fields.Many2many('account.tax', 'ple_config_tax_taxable', 'ple_config_taxable', 'tax_taxable', string='Taxable', domain=sales_domain)
    l10n_pe_exonerated_vat = fields.Many2many('account.tax', 'ple_config_tax_exonerated', 'ple_config_exonerated', 'tax_exonerated', string='Exonerated', domain=sales_domain)
    l10n_pe_not_affected_vat = fields.Many2many('account.tax', 'ple_config_tax_not_affected', 'ple_config_not_affected', 'tax_not_affected', string='Not Affected', domain=sales_domain)
    l10n_pe_piled_rise_tax = fields.Many2many('account.tax', 'ple_config_tax_piled_rise', 'ple_config_piled_rise', 'tax_piled_rise', string='Piled Rise Tax', domain=sales_domain)
    l10n_pe_sales_excise_tax = fields.Many2many('account.tax', 'ple_config_tax_excise', 'ple_config_excise', 'tax_excise', string='Sales Excise Tax', domain=sales_domain)
    l10n_pe_sales_other_tax = fields.Many2many('account.tax', 'ple_config_tax_other', 'ple_config_other', 'tax_other', string='Sales Other Tax', domain=sales_domain)
    pastic_bag_sale_tax = fields.Many2many('account.tax', 'ple_config_tax_bag_sale', 'ple_config_bag_sale', 'tax_bag_sale', string='Plastic Bag Tax Sale',
                                          domain=[('type_tax_use', '=', 'sale')])

    #### campo 13.1
    l10n_pe_standard_valuation_method = fields.Selection('_get_valuation_method', string="Standard Type Valuation Method")
    l10n_pe_fifo_valuation_method = fields.Selection('_get_valuation_method', string="FIFO Type Valuation Method")
    l10n_pe_average_valuation_method = fields.Selection('_get_valuation_method',
                                                        string="Average Price Type Valuation Method")

    def get_ple_table(self, code):
        catele_model = self.env['catalog.element']
        table_list = [
            (e.name, "%s - %s" % (e.name, e.description)) for e in catele_model._get_datasource(code) if e.active
        ]
        return table_list

    def _get_account_chart_type(self):
        return self.get_ple_table("PE.SUNAT.PLE_TABLE17")

    @api.model
    def _get_sunat_ple_type(self):
        return self.get_ple_table("PE.SUNAT.PLE_BOOKS")

    def get_report_type(self, context=None):
        rep_types = super(PleConfiguration, self).get_report_type(context=context)
        rep_types = self._get_sunat_ple_type(self)

        return sorted(rep_types, key=lambda e: e[0])

    def get_ple_table(self, code):
        catele_model = self.env['catalog.element']
        table_list = [(e.name, "%s - %s" % (e.name, e.description)) for e in catele_model._get_datasource(code) if
                      e.active]
        return table_list

    def _get_valuation_method(self):
        return self.get_ple_table("PE.SUNAT.PLE_TABLE14")

    def action_create_ple_config(self, value):
        for line in self.env['res.company'].search([]):
            self.create({'company_id': line.id, 'report_type': value})
