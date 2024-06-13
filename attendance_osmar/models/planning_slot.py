from odoo import models, exceptions, fields , _

class PlanningSlot(models.Model):
    _inherit = 'planning.slot'
    attendance_check_ids = fields.One2many('attendance.check','planning_slot')

    def create(self,vals):
        res = super().create(vals)
        for record in self:
            if not record.role_id:
                raise ValueError(record)
        return res