from odoo import models, fields

class HrPayslipXlsx(models.AbstractModel):
    _name = 'report.l10n_pe_hr_payroll_report.report_customer_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objs):
        for obj in objs:
            report_name = obj.name
            sheet = workbook.add_worksheet(report_name[:31])
            bold = workbook.add_format({'bold': True,  'font_size': 10})
            normal = workbook.add_format({'bold': False, 'font_size': 9})
            font_grey = workbook.add_format({'bold': False, 'font_size': 10,'font_color': 'white','bg_color': 'gray'})

            font_dark_blue = workbook.add_format({'bold': True, 'font_size': 10, 'font_color': 'white', 'bg_color': '#0c0fa9'})
            font_dark_blue.set_align('center')

            font_orange = workbook.add_format({'bold': True, 'font_size': 10, 'font_color': 'white', 'bg_color': '#e39532'})
            font_orange.set_align('center')

            font_sky_green = workbook.add_format({'bold': True, 'font_size': 10, 'font_color': 'black', 'bg_color': '#ccfce0'})
            font_sky_green.set_align('center')

            font_dark_green = workbook.add_format({'bold': True, 'font_size': 10, 'font_color': 'white', 'bg_color': '#116936'})
            font_dark_green.set_align('center')

            font_yellow = workbook.add_format({'bold': True, 'font_size': 10, 'font_color': 'black', 'bg_color': 'yellow'})
            font_yellow.set_align('center')

            sheet.set_column('A:BL', 14, bold)

            sheet.merge_range('B2:C2', 'CALCULO DE PLANILLAS', bold)
            sheet.merge_range('B3:C3', obj.name, bold)
            sheet.merge_range('B4:C4', 'REGIMEN GENERAL PRIVADO', bold)

            sheet.write('B5', 'Fecha de Inicio:', font_grey)
            sheet.write('C5', obj.date_start.strftime("%d/%m/%Y"), bold)

            sheet.write('B6', 'Fecha de Termino:', font_grey)
            sheet.write('C6', obj.date_end.strftime("%d/%m/%Y"), bold)

            sheet.write('B7', 'Minimo Vital', font_grey)
            sheet.write('B8', 'Minimo Nocturno', font_grey)
            sheet.write('B9', 'Remuneracion Asegurable AFP', font_grey)
            sheet.write('B10', '% Aporte Seguro AFP', font_grey)

            sheet.write('A11', 'DNI', font_dark_blue)
            sheet.write('B11', 'Trabajador', font_dark_blue)
            sheet.write('C11', 'Fecha de Nacimiento', font_dark_blue)
            sheet.write('D11', 'Fecha de Ingreso', font_dark_blue)
            sheet.write('E11', 'Fecha de Cese', font_dark_blue)
            sheet.write('F11', 'Puesto', font_dark_blue)
            sheet.write('G11', 'AFP o ONP', font_dark_blue)
            sheet.write('H11', 'CUSSP', font_dark_blue)

            sheet.write('I11', 'Dias a Trabajados', font_orange)
            sheet.write('J11', 'Dias DM', font_orange)
            sheet.write('K11', 'Dias Faltas', font_orange)
            sheet.write('L11', 'Dias LCGH', font_orange)
            sheet.write('M11', 'Dias Vac', font_orange)
            sheet.write('N11', '#HNOCT', font_orange)
            sheet.write('O11', 'Dias Subsidio', font_orange)

            sheet.write('P11', '#HHEE25%', font_sky_green)
            sheet.write('Q11', '#HHEE35%', font_sky_green)
            sheet.write('R11', '#HHEE100%', font_sky_green)
            sheet.write('S11', 'HORAS FERIADO', font_sky_green)

            sheet.write('T11', 'Sueldo Basico', font_dark_green)
            sheet.write('U11', 'Asignacion Familiar (Teorico)', font_dark_green)
            sheet.write('V11', 'Movilidad (Teorico)', font_dark_green)
            sheet.write('W11', 'Recargo Al Consumo (Teorico)', font_dark_green)
            sheet.write('X11', 'Total Estructura (Teorico)', font_dark_green)

            sheet.write('Y11', 'Haber Basico', font_dark_blue)
            sheet.write('Z11', 'Asignacion Familiar', font_dark_blue)
            sheet.write('AA11', 'Movilidad Libre', font_dark_blue)
            sheet.write('AB11', 'Viáticos Supeditado', font_dark_blue)
            sheet.write('AC11', 'Movilidad Supeditada', font_dark_blue)
            sheet.write('AD11', 'Alimentacion supeditada', font_dark_blue)

            sheet.write('AE11', 'Recargo al Consumo', font_dark_blue)
            sheet.write('AF11', 'Licencia Con goce H', font_dark_blue)
            sheet.write('AG11', 'Subsidio por maternidad', font_dark_blue)
            sheet.write('AH11', 'Subsidio por enfermedad', font_dark_blue)
            sheet.write('AI11', 'RC EXTRA ORDINARIO', font_dark_blue)
            sheet.write('AJ11', 'Vacaciones', font_dark_blue)
            sheet.write('AK11', 'Descanso Medico', font_dark_blue)
            sheet.write('AL11', 'Vacaciones', font_dark_blue)
            sheet.write('AM11', 'COMPRA DE VACACIONES', font_dark_blue)
            sheet.write('AN11', 'Comisiones', font_dark_blue)
            sheet.write('AO11', 'HHEE 25 %', font_dark_blue)
            sheet.write('AP11', '#HHEE35%', font_dark_blue)
            sheet.write('AQ11', '#HHEE100%', font_dark_blue)
            sheet.write('AR11', 'HORAS FERIADO', font_dark_blue)
            sheet.write('AS11', 'Horas Nocturnas', font_dark_blue)
            sheet.write('AT11', 'Gratificaciones', font_dark_blue)
            sheet.write('AU11', 'CTS', font_dark_blue)
            sheet.write('AV11', 'TOTAL INGRESOS', font_dark_blue)

            sheet.write('AW11', 'val', font_sky_green)

            sheet.write('AX11', 'Base de Calculo AFP', font_yellow)
            sheet.write('AY11', 'Base de Calculo ONP/ESSALUD', font_yellow)
            sheet.write('AZ11', 'Base de Calculo Quinta', font_yellow)
            sheet.write('BA11', 'Comision AFP', font_yellow)

            sheet.write('BB11', 'AFP Aporte Obligatorio', font_dark_blue)
            sheet.write('BC11', 'AFP Prima Comision', font_dark_blue)
            sheet.write('BD11', 'AFP Prima Seguro', font_dark_blue)
            sheet.write('BE11', 'ONP Aporte', font_dark_blue)
            sheet.write('BF11', 'Renta de Quinta - Mensual', font_dark_blue)
            sheet.write('BG11', 'OTRO DESCUENTO', font_dark_blue)
            sheet.write('BH11', 'Descuento - Prestamo', font_dark_blue)
            sheet.write('BI11', 'Retención judicial', font_dark_blue)
            sheet.write('BJ11', 'TOTAL DESCUENTOS', font_dark_blue)
            sheet.write('BK11', 'PAGO NETO', font_dark_blue)
            sheet.write('BL11', 'Aporte Essalud', font_dark_blue)

            fila = 11
            for l in obj.slip_ids:
                sheet.write(fila, 0,l.employee_id.work_contact_id.vat, normal)
                sheet.write(fila, 1, l.employee_id.name, normal)
                sheet.write(fila, 2, l.employee_id.birthday.strftime("%d/%m/%Y") if l.employee_id.birthday else '', normal)
                sheet.write(fila, 3, l.contract_id.date_start.strftime("%d/%m/%Y"), normal)
                sheet.write(fila, 4, 0, normal)
                sheet.write(fila, 5, l.employee_id.job_title, normal)
                sheet.write(fila, 6, l.employee_id.input_afp or l.employee_id.input_eps, normal)
                sheet.write(fila, 7, 0, normal)
                sheet.write(fila, 8, self.get_number_day(l, 'WORK100'), normal)
                sheet.write(fila, 9, 0, normal)
                sheet.write(fila, 10, self.get_number_day(l, 'C7042'), normal)
                sheet.write(fila, 11, self.get_number_day(l, 'C7021'), normal)
                sheet.write(fila, 12, self.get_number_day(l, 'C7050'), normal)
                sheet.write(fila, 13, self.get_number_hours(l, 'C7066'), normal)
                sheet.write(fila, 14, 0, normal)
                sheet.write(fila, 15, 0, normal)
                sheet.write(fila, 16, 0, normal)
                sheet.write(fila, 17, 0, normal)
                sheet.write(fila, 18, 0, normal)
                sheet.write(fila, 19, l.contract_id.wage, normal)
                sheet.write(fila, 20, l.contract_id.rmv * 0.1 if l.employee_id.children > 0 else 0, normal)
                sheet.write(fila, 21, l.contract_id.mov_libre, normal)
                sheet.write(fila, 22, l.contract_id.mov_sup, normal)
                column_23 = l.contract_id.wage +  l.contract_id.mov_libre + l.contract_id.mov_sup + l.contract_id.rmv * 0.1 if l.employee_id.children > 0 else 0
                sheet.write(fila, 23, column_23, normal)

                sheet.write(fila, 24, l.contract_id.wage, normal)
                sheet.write(fila, 25, l.contract_id.rmv * 0.1 if l.employee_id.children > 0 else 0, normal)
                sheet.write(fila, 26, l.contract_id.mov_libre, normal)
                sheet.write(fila, 27, l.contract_id.expenses, normal)
                sheet.write(fila, 28, l.contract_id.mov_sup, normal)
                sheet.write(fila, 29, l.contract_id.feeding, normal)
                sheet.write(fila, 30, 0, normal)

                sheet.write(fila, 31, self.get_amount(l, 'c7021'), normal)
                sheet.write(fila, 32, self.get_amount(l, 'c915'), normal)
                sheet.write(fila, 33, self.get_amount(l, 'c916'), normal)
                sheet.write(fila, 34, 0, normal)
                sheet.write(fila, 35, 0, normal)
                sheet.write(fila, 36, 0, normal)
                sheet.write(fila, 37, 0, normal)
                sheet.write(fila, 38, 0, normal)
                sheet.write(fila, 39, 0, normal)
                sheet.write(fila, 40, 0, normal)
                sheet.write(fila, 41, 0, normal)
                sheet.write(fila, 42, 0, normal)
                sheet.write(fila, 43, 0, normal)
                sheet.write(fila, 44, 0, normal)
                sheet.write(fila, 45, 0, normal)
                sheet.write(fila, 46, 0, normal)
                sheet.write_formula('AV'+ str(fila+1), '=SUM(Y'+str(fila+1)+':AU'+str(fila+1)+')')
                sheet.write(fila, 48, 0, normal)
                sheet.write(fila, 49, 0, normal)
                sheet.write(fila, 50, 0, normal)
                sheet.write(fila, 51, self.get_amount(l, 'HBASIC'), normal)
                sheet.write(fila, 52, 0, normal)
                sheet.write(fila, 53, self.get_amount(l, 'AFP'), normal)
                sheet.write(fila, 54, 0, normal)
                sheet.write(fila, 55, self.get_amount(l, 'AFP-S'), normal)
                sheet.write(fila, 56, self.get_amount(l, 'SNP'), normal)
                sheet.write(fila, 57, self.get_amount(l, 'QC'), normal)
                sheet.write(fila, 58, 0, normal)
                sheet.write(fila, 59, 0, normal)
                sheet.write(fila, 60, 0, normal)
                sheet.write(fila, 61, self.get_amount(l, 'C8990'), normal)
                sheet.write(fila, 62, self.get_amount(l, 'NETO'), normal)
                sheet.write(fila, 63, self.get_amount(l, 'ESSALUD-9'), normal)

                fila += 1

    def get_amount(self, payslip, code):
        line_id = payslip.line_ids.filtered(lambda l: l.code == code)
        return line_id.amount if line_id else 0

    def get_number_day(self, payslip, code):
        worked_days = payslip.worked_days_line_ids.filtered(lambda l: l.code == code)
        return worked_days.number_of_days if worked_days else 0

    def get_number_hours(self, payslip, code):
        worked_days = payslip.worked_days_line_ids.filtered(lambda l: l.code == code)
        return worked_days.number_of_hours if worked_days else 0

    def get_dni_partner(self, employee_id):
        name_array = employee_id.name.split(' ')
        for line in name_array:
            self.env['res.partner'].search([('name' , 'ilike', line)])
        return True







