# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, Command, fields, models, _
from dateutil.relativedelta import relativedelta
import pytz
import calendar
import math
from datetime import date, datetime, time


zona_horaria = pytz.timezone('America/Lima')


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_schedule_period_start(self):
        schedule = self.contract_id.schedule_pay or self.contract_id.structure_type_id.default_schedule_pay
        today = date.today()
        week_start = self.env["res.lang"]._lang_get(self.env.user.lang).week_start
        date_from = today

        if schedule == 'quarterly':
            current_year_quarter = math.ceil(today.month / 3)
            date_from = today.replace(day=1, month=(current_year_quarter - 1) * 3 + 1)
        elif schedule == 'semi-annually':
            is_second_half = math.floor((today.month - 1) / 6)
            date_from = today.replace(day=1, month=7) if is_second_half else today.replace(day=1, month=1)
        elif schedule == 'annually':
            date_from = today.replace(day=1, month=1)
        elif schedule == 'weekly':
            week_day = today.weekday()
            date_from = today + relativedelta(days=-week_day)
        elif schedule == 'bi-weekly':
            week = int(today.strftime("%U") if week_start == '7' else today.strftime("%W"))
            week_day = today.weekday()
            is_second_week = week % 2 == 0
            date_from = today + relativedelta(days=-week_day - 7 * int(is_second_week))
        elif schedule == 'bi-monthly':
            current_year_slice = math.ceil(today.month / 2)
            date_from = today.replace(day=1, month=(current_year_slice - 1) * 2 + 1)
        else:  # if not handled, put the monthly behaviour
            date_from = today.replace(day=1)
            if self.date_from:
                date_from = self.date_from
        if self.contract_id and date_from < self.contract_id.date_start:
            date_from = self.contract_id.date_start
        return date_from

    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to')
    def _compute_worked_days_line_ids(self):
        super(HrPayslip, self)._compute_worked_days_line_ids()
        attendance = self.env.ref('hr_work_entry.work_entry_type_attendance').id
        for payslip in self:
            days_total = sum([line.number_of_days for line in payslip.worked_days_line_ids.filtered(lambda l: l.work_entry_type_id.id != attendance)])
            if payslip.worked_days_line_ids.filtered(lambda l: l.work_entry_type_id.id == attendance):
                worked_days_line_id = payslip.worked_days_line_ids.filtered(lambda l: l.work_entry_type_id.id == attendance)[0]
                worked_days_line_id.update({'number_of_days': 30 - days_total,
                                            'number_of_hours': (30 - days_total) * payslip.contract_id.resource_calendar_id.hours_per_day})

    @api.depends('worked_days_line_ids.number_of_hours', 'worked_days_line_ids.is_paid')
    def _compute_worked_hours(self):
        for payslip in self:
            payslip.sum_worked_hours = sum([line.number_of_hours for line in payslip.worked_days_line_ids.filtered(lambda l: not l.work_entry_type_id.extra_hours)])

    def _compute_input_line_ids(self):
        super(HrPayslip, self)._compute_input_line_ids()
        for slip in self:
            slip.input_line_ids.unlink()
            worked_entry_extra_hours = self.env['hr.work.entry'].search([('date_start', '>=', slip.date_from),
                                                                         ('date_stop', '<=', slip.date_to),
                                                                         ('work_entry_type_id.extra_hours', '=', True),
                                                                         ('contract_id', '=', slip.contract_id.id)])
            dayofweek = [int(attendance.dayofweek) for attendance in self.contract_id.resource_calendar_id.attendance_ids]
            dateholidays = self.env['resource.calendar.leaves'].search([('date_from', '>=', slip.date_from), ('date_to','<=', slip.date_to)])
            holidays = [fecha_hora.day for fecha_hora in dateholidays.mapped('date_from')]
            work_holidays = self.env['hr.work.entry']
            work_out_contract = self.env['hr.work.entry']
            work_extra = self.env['hr.work.entry']
            for line in worked_entry_extra_hours:
                if line.date_start.astimezone(zona_horaria).day in holidays:
                    work_holidays |= line
                elif line.date_start.astimezone(zona_horaria).weekday() not in dayofweek:
                    work_out_contract |= line
                else:
                    work_extra |= line
            hours_work_holidays = sum(p.duration for p in work_holidays)
            hours_work_out_contract = sum(p.duration for p in work_out_contract)
            assignment_family = 0
            if slip.employee_id.children > 0:
                assignment_family = slip.contract_id.rmv * 0.1
            hours_work_extra_25 = 0
            hours_work_extra_35 = 0
            for hours in work_extra:
                if hours.duration > 3:
                    hours_work_extra_25 += 3
                    hours_work_extra_35 += hours.duration - 3
                else:
                    hours_work_extra_25 += hours.duration
            res = []
            pay_hours = slip.contract_id.wage/slip.sum_worked_hours if slip.sum_worked_hours > 0 else 0
            pay_hours_extra = (slip.contract_id.wage + assignment_family) / 240
            if hours_work_holidays > 0 and pay_hours > 0:
                res.append((0, 0, {'input_type_id': self.env.ref('l10n_pe_hr_payroll.input_attachment_salary_he_feriado').id,
                                   'name': str(round(hours_work_holidays)) + ' horas de trabajo en feriado',
                                   'amount': pay_hours_extra * hours_work_holidays * 2}))
            if hours_work_out_contract > 0 and pay_hours > 0:
                res.append((0, 0, {'input_type_id': self.env.ref('l10n_pe_hr_payroll.input_attachment_salary_he_100').id,
                                   'name': str(round(hours_work_out_contract)) + ' horas de trabajo en dia no laboral',
                                   'amount': pay_hours_extra * hours_work_out_contract * 2}))
            if hours_work_extra_25 > 0 and pay_hours > 0:
                res.append((0, 0, {'input_type_id': self.env.ref('l10n_pe_hr_payroll.input_attachment_salary_he_25').id,
                                   'name': str(round(hours_work_extra_25)) + ' horas de trabajo',
                                   'amount': (pay_hours_extra * hours_work_extra_25) * 1.25}))
            if hours_work_extra_35 > 0 and pay_hours > 0:
                res.append((0, 0, {'input_type_id': self.env.ref('l10n_pe_hr_payroll.input_attachment_salary_he_35').id,
                                   'name': str(round(hours_work_extra_35)) + ' horas de trabajo',
                                   'amount': (pay_hours_extra * hours_work_extra_35) * 1.35}))
            if slip.contract_id.mov and slip.worked_days_line_ids:
                if slip.contract_id.mov_libre > 0:
                    res.append((0, 0, {'input_type_id': self.env.ref('l10n_pe_hr_payroll.input_attachment_mov_libre').id,
                                       'name': 'Movilidad libre disponible',
                                       'amount': slip.contract_id.mov_libre}))
                if slip.contract_id.mov_sup > 0:
                    number_work_days = sum(days_work.number_of_days for days_work in slip.worked_days_line_ids.filtered(lambda l: l.work_entry_type_id.id ==1)) or 0
                    res.append((0, 0, {'input_type_id': self.env.ref('l10n_pe_hr_payroll.input_attachment_mov_sup').id,
                                       'name': 'Movilidad libre disponible',
                                       'amount': round(slip.contract_id.mov_sup * number_work_days)}))
            slip.update({'input_line_ids': res})

    def compute_fifth_category(self, hbasic):
        method_type = self.company_id.method_type
        wage = self.contract_id.wage
        uit = self.contract_id.uit
        mov_libre = self.contract_id.mov_libre
        expenses = round(self.contract_id.expenses * 30)
        mov_sup = round(self.contract_id.mov_sup * 30)
        feeding = round(self.contract_id.feeding * 30)
        assignment_family = self.contract_id.rmv * 0.1 if self.employee_id.children > 0 else 0
        amount_rent = 0
        amount = 0
        seven_uit = self.contract_id.uit * 7
        proyeccion = self.compute_proyeccion() if method_type == '2' else 0
        fixed_income = wage + assignment_family + mov_libre + mov_sup + expenses + feeding
        estimate_input_month = (fixed_income) * (12 - self.date_from.month)
        before_input_month, before_rent_month = self.compute_before_month(fixed_income)
        estimate_gratification = self.compute_gratification(fixed_income)
        rent_neta = (estimate_input_month + hbasic + before_input_month + estimate_gratification) - seven_uit
        if rent_neta > 0:
            for line in [[5, 8], [20, 14], [35, 17], [45, 20], [45, 30]]:
                if rent_neta > 0:
                    value = rent_neta if rent_neta < line[0] * uit else line[0] * uit
                    amount_rent += value * (line[1]/100)
                    rent_neta -= line[0] * uit
            amount = (amount_rent + before_rent_month)/(13-self.date_from.month)
        return amount

    def compute_before_month(self, fixed_income):
        input_amount = 0
        rent_amount = 0
        date_from = (self.date_from.year, 1, 1)
        date_to = self.date_from
        hr_paylib = self.env['hr.payslip'].search([('date_from', '>=', date_from),
                                                   ('date_to', '<=', date_to),
                                                   ('employee_id', '=', self.employee_id.id),
                                                   ('state', 'in', ['paid', 'done', 'verify'])])
        input_id = self.env.ref('l10n_pe_hr_payroll.hr_salary_rule_pe_haber_basic_general').id
        rent_id = self.env.ref('l10n_pe_hr_payroll.hr_salary_rule_pe_quinta_categoria').id
        if hr_paylib:
            rent_amount = sum(x.amount for x in hr_paylib.line_ids.filtered(lambda x: x.salary_rule_id.id == rent_id))
            input_amount = sum(x.amount for x in hr_paylib.line_ids.filtered(lambda x: x.salary_rule_id.id == input_id))

        else:
            if self.contract_id.date_start.month < self.date_from.month:
                input_amount = fixed_income * self.date_from.month - self.contract_id.date_start.month
        hr_paylib = hr_paylib + self
        rent_amount = rent_amount + sum(x.amount for x in hr_paylib.input_line_ids.filtered(lambda x: x.input_type_id.code == "PRE-RET"))
        input_amount = input_amount + sum(x.amount for x in hr_paylib.input_line_ids.filtered(lambda x: x.input_type_id.code == "PRE-ING"))
        return input_amount, rent_amount

    def compute_gratification(self, fixed_income):
        first_date, second_date = self.compute_date_gratification(self.date_from, self.contract_id.date_start)
        month = self.date_from.month
        self.contract_id.date_start
        if month <= 6:
            gratification_first = ((fixed_income * first_date)/6) * 1.09
        else:
            gratification_first = 0.0
        if month >= 7 and month <= 12:
            gratification_second = ((fixed_income * second_date)/6) * 1.09
        else:
            gratification_second = fixed_income * 1.09
        return gratification_first + gratification_second

    def compute_date_gratification(self, date_from, date_start):
        if date_start.year < date_from.year:
            return 6, 6
        else:
            add_month = 0
            if date_start.day > 1:
                add_month = 1
            if date_start.month < 7:
                return 7 - date_start.month + add_month, 6
            else:
                return 0, 13 - date_start.month + add_month

    def compute_proyeccion(self):
        amount = 0
        date_projection = []
        for line in [1, 2, 3]:
            date_projection.append(self.date_from - relativedelta(months=line))
        hr_paylib = self.env['hr.payslip'].search([('date_from', 'in', date_projection),
                                                   ('employee_id', '=', self.employee_id.id),
                                                   ('state', 'in', ['paid', 'done', 'verify'])])
        category_extra = self.env.ref('l10n_pe_hr_payroll.extra_hours').id
        movilidad_sup = self.env.ref('l10n_pe_hr_payroll.hr_salary_rule_pe_general_c1263').id
        if hr_paylib:
            projection_extra = sum(x.amount for x in hr_paylib.line_ids.filtered(lambda x: x.category_id.id == category_extra))/3
            projection_mov_sup = sum(x.amount for x in hr_paylib.line_ids.filtered(lambda x: x.salary_rule_id.id == movilidad_sup))/3
            amount = projection_extra + projection_mov_sup
        return amount

    def generar_array_while(self, month, min_range):
        haber_basic = self.env.ref('l10n_pe_hr_payroll.hr_salary_rule_pe_haber_basic_general').id
        amount = 0
        result = []
        date_range = []
        while month > min_range:
            month -= 1
            result.append(month)
        for line in result:
            date_range.append((fields.datetime.now().year, line, 1))
        hr_paylib = self.env['hr.payslip'].search([('date_from', 'in', date_range),
                                                   ('employee_id', '=', self.employee_id.id),
                                                   ('state', 'in', ['paid', 'done', 'verify'])])
        if hr_paylib:
            amount = sum(x.amount for x in hr_paylib.line_ids.filtered(lambda x: x.salary_rule_id.id == haber_basic))
        return amount

    def compute_paycheck_advance(self):
        res = 0.0
        paycheck_advance = self.env.ref('l10n_pe_hr_payroll.hr_payroll_structure_pe_biweekly_general').id
        hr_paylib = self.env['hr.payslip'].search([('date_from', '>=', self.date_from),
                                                   ('date_to', '<=', self.date_to),
                                                   ('employee_id', '=', self.employee_id.id),
                                                   ('struct_id', '=', paycheck_advance)], limit=1)
        if hr_paylib:
            res = hr_paylib.line_ids.filtered(lambda x: x.category_id.code =='NET').total
        return res

    def action_print_payment(self):
        info ={}
        return self.env.ref('l10n_pe_hr_payroll.action_hr_payslip_pe').report_action(self, data=info)

    def action_print_payment_cts(self):
        info ={}
        return self.env.ref('l10n_pe_hr_payroll.action_hr_payslip_pe_cts').report_action(self, data=info)

    def month_name(self, month):
        month_name = calendar.month_name[month]
        return month_name.capitalize()

    def compute_worked_days_unpaid(self):
        worked_days_line_ids = self.worked_days_line_ids.filtered(lambda l: self.struct_id.id in l.work_entry_type_id.unpaid_structure_ids.ids)
        days = 0
        if worked_days_line_ids:
            for line in worked_days_line_ids:
                days += line.number_of_days
        return days

    def compute_average_rules(self, values):
        struct_month = self.env.ref('l10n_pe_hr_payroll.hr_payroll_structure_pe_general').id
        hr_payslip_ids = self.env['hr.payslip'].search([('date_to', '<=', self.date_to),
                                                        ('date_from', '>=', self.date_from),
                                                        ('struct_id', '=', struct_month),
                                                        ('employee_id', '=', self.employee_id.id)])
        total = 0
        for line in values:
            if len(hr_payslip_ids.mapped('line_ids').filtered(lambda l: l.code == line)) > 2:
                total += sum(x.total for x in hr_payslip_ids.mapped('line_ids').filtered(lambda l: l.code == line))/6
        return total

    def compute_rule_gratification(self):
        date_from = False
        date_to = False
        if self.date_from.month == 7:
            date_from = fields.date(self.date_from.year, 1, 1)
            date_to = fields.date(self.date_from.year, 6, 30)
        if self.date_from.month == 12:
            date_from = fields.date(self.date_from.year, 7, 1)
            date_to = fields.date(self.date_from.year, 12, 31)
        res = 0.0
        gratification = self.env.ref('l10n_pe_hr_payroll.hr_payroll_structure_gtfct').id
        if date_to and date_from:
            hr_payslip_id = self.env['hr.payslip'].search([('date_to', '<=', date_to),
                                                            ('date_from', '>=', date_from),
                                                            ('struct_id', '=', gratification),
                                                            ('employee_id', '=', self.employee_id.id)])
            if hr_payslip_id:
                res = hr_payslip_id.line_ids.filtered(lambda x: x.code == 'AGTFCC').total
        return res




