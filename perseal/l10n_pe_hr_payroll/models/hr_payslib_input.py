# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    @api.onchange('name')
    def _onchange_name_input(self):
        list_ids = {}
        list_ids[self.env.ref('l10n_pe_hr_payroll.input_attachment_salary_he_feriado')] = 2
        list_ids[self.env.ref('l10n_pe_hr_payroll.input_attachment_salary_he_100')] = 2
        list_ids[self.env.ref('l10n_pe_hr_payroll.input_attachment_salary_he_25')] = 1.25
        list_ids[self.env.ref('l10n_pe_hr_payroll.input_attachment_salary_he_35')] = 1.35
        assignment_family = 0
        if self.payslip_id.employee_id.children > 0:
            assignment_family = self.payslip_id.contract_id.rmv * 0.1
        pay_hours = (self.payslip_id.contract_id.wage + assignment_family) / 240
        if self.input_type_id in list(list_ids.keys()):
            if self.string_is_number(self.name):
                self.amount = pay_hours * float(self.name) * list_ids[self.input_type_id]

    def string_is_number(self, cadena):
        try:
            float(cadena)
            return True
        except ValueError:
            return False