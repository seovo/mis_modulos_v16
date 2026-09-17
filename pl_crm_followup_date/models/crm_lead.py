from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    next_followup_date = fields.Date(tracking=True)
    followup_note = fields.Char(tracking=True)
