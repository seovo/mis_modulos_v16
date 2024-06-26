from odoo import models, exceptions, fields , _

class PlanningSlot(models.Model):
    _inherit = 'planning.slot'
    attendance_check_ids = fields.One2many('attendance.check','planning_slot')

    def complete_attendance(self):
        if not self.attendance_check_ids and self.resource_id and self.role_id:
            employess = self.env['hr.employee'].search([
                ('resource_jz_id','=',self.resource_id.id),
                ('role_jz_id','=',self.role_id.id )
            ])

            for employee in employess:
                self.attendance_check_ids += self.env['attendance.check'].new({
                    'hr_employee_id': employee.id ,
                    'date': self.start_datetime.date() ,
                })
