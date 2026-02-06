# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ReportAccountAgedReceivable(models.Model):
    _inherit = "account.aged.receivable"

    @api.model
    def _get_templates(self):
        templates = super(ReportAccountAgedReceivable, self)._get_templates()
        templates['main_template'] = 'account_report_filter.main_template_inherit_filtro_por_cuenta'
        return templates


class ReportAccountAgedPayable(models.Model):
    _inherit = "account.aged.payable"

    @api.model
    def _get_templates(self):
        templates = super(ReportAccountAgedPayable, self)._get_templates()
        templates['main_template'] = 'account_report_filter.main_template_inherit_filtro_por_cuenta'
        return templates
