from odoo import api, fields, models
import datetime

class PlanningSlotWizard(models.TransientModel):
    _name = "planning.slot.wizard"
    _description  = "planning.slot.wizard"
    resource_ids  = fields.Many2many('resource.resource',domain=[('resource_type','=','user')],string="Guardias",required=True)
    role_ids      = fields.Many2many('planning.role',string="Sectores",required=True)
    start_date    = fields.Date(string="Fecha Inicio",required=True)
    end_date      = fields.Date(string="Fecha Fin",required=True)
    number        = fields.Integer(string="Dias a Intercalar",required=True)


    def create_slots(self):


        diff = self.end_date - self.start_date

        diff = int(diff.days / (self.number ) )



        for resource in self.resource_ids:
            for rolex in self.role_ids:
                days_init = 0
                start_date = self.start_date

                for i in range(diff + 1):

                    if days_init > 0:
                        start_date = self.start_date + datetime.timedelta(days=days_init)

                    if start_date > self.end_date:
                        break

                    start_datetime = datetime.datetime(start_date.year, start_date.month, start_date.day, 8, 0, 0)
                    end_datetime = datetime.datetime(start_date.year, start_date.month, start_date.day, 16, 0, 0)

                    if not resource:
                        raise ValueError(i)

                    if not rolex:
                        raise ValueError(i)

                    dx = {
                        'resource_id': resource.id,
                        'role_id': rolex.id,
                        'repeat': True,
                        'repeat_interval': 1,
                        'repeat_unit': 'day',
                        'repeat_type': 'x_times',
                        'repeat_number': self.number,
                        'start_datetime': start_datetime,
                        'end_datetime': end_datetime,
                    }
                    wizard = self.env['planning.slot'].create(dx)
                    wizard._check_repeat_until()
                    wizard._onchange_repeat_until()

                    sin_role = self.env['planning.slot'].search([('resource_id','=',False)])
                    for sin in sin_role:
                        sin.resource_id = resource.id

                    # wizard.action_send()

                    days_init += self.number * 2






