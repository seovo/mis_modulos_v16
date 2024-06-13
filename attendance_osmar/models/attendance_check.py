from odoo import models, exceptions, fields , _

class AttendanceCheck(models.Model):
    _name           = "attendance.check"
    _description    = "attendance.check"
    hr_employee_id  = fields.Many2one('hr.employee')
    date            = fields.Date()
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




class AttendanceCheckState(models.Model):
    _name           = "attendance.check.state"
    _description    = "attendance.check.state"
    name            = fields.Char(required=True)
    register_attendance = fields.Boolean(string="Registrar Asistencia")
    start_hour          = fields.Float(string="Hora Inicio")
    end_end             = fields.Float(string="Hora Fin")
