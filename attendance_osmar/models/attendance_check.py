from odoo import models, exceptions, fields , api , _
import datetime

class AttendanceCheck(models.Model):
    _name           = "attendance.check"
    _description    = "attendance.check"
    hr_employee_id  = fields.Many2one('hr.employee',string="Empleado",required=True)
    date            = fields.Date(required=True)
    planning_slot   = fields.Many2one('planning.slot')
    hr_attendance_id   =   fields.Many2one('hr.attendance',string="Asistencia")
    state              = fields.Many2one('attendance.check.state',string="Estado")

    _sql_constraints = [
        (
            "unique_date_employee",
            "unique(date,hr_employee_id)",
            "No se puede duplicar  Asistencia",
        )
    ]

    def verifi_attendance(self):
        if self.state.register_attendance:
            if not self.hr_attendance_id:
                hour_start = int(self.state.start_hour) + 5
                hour_end = int(self.state.end_end) + 5

                start_date = self.date
                start_datetime = datetime.datetime(start_date.year, start_date.month, start_date.day, hour_start, 0, 0)
                end_datetime = datetime.datetime(start_date.year, start_date.month, start_date.day, hour_end, 0, 0)
                asistencia = self.env['hr.attendance'].create({
                    'employee_id': self.hr_employee_id.id ,
                    'check_in': start_datetime ,
                    'check_out': end_datetime
                })
                self.hr_attendance_id = asistencia.id
        else:
            if self.hr_attendance_id:
                self.hr_attendance_id.unlink()


    @api.model
    def create(self,vals):
        res = super().create(vals)
        for record in res:
            record.verifi_attendance()
        return res

    def write(self,vals):
        res = super().write(vals)
        for record in self:
            record.verifi_attendance()
        return res



class AttendanceCheckState(models.Model):
    _name           = "attendance.check.state"
    _description    = "attendance.check.state"
    name            = fields.Char(required=True)
    register_attendance = fields.Boolean(string="Registrar Asistencia")
    start_hour          = fields.Float(string="Hora Inicio")
    end_end             = fields.Float(string="Hora Fin")
