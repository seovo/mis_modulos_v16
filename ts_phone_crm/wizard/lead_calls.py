from odoo import models, fields, api


class LeadCallsWizard(models.TransientModel):
    _name = 'lead.calls.wizard'
    _description = 'Lead Calls Wizard'

    def _get_default_mobile(self):
        if self.env.context.get('mobile'):
            return self.env.context.get('mobile')

    def _get_default_notes(self):
        if self.env.context.get('notes'):
            return self.env.context.get('notes')

    def _get_default_name(self):
        if self.env.context.get('name'):
            return self.env.context.get('name')

    def create_lead(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        crm_brw = self.env['phone.calls'].browse(active_id)
        vals = {'name': self.name,
                'email_from': self.email_from or False,
                # 'mobile': self.call_from or False,
                'description': (self.notes) or False,
                }

        if 'lead_interaction_source' in self.env['crm.lead']._fields:
            vals['lead_interaction_source'] = self.interaction_source
        if 'medium_id' in self.env['crm.lead']._fields:
            vals['medium_id'] = self.medium_id.id
        if 'source_id' in self.env['crm.lead']._fields:
            vals['source_id'] = self.source_id.id
        if 'lead_source' in self.env['crm.lead']._fields:
            vals['lead_source'] = self.lead_source
        record = self.env['crm.lead'].create(vals)
        crm_brw.lead_id = record.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "crm.lead",
            "views": [[False, "form"]],
            "res_id": record.id,
            "target": "self",
        }

    name = fields.Char(string="Call Title", default=_get_default_name)
    email_from = fields.Char(string="Email")
    call_from = fields.Char(string="Caller Phone", default=_get_default_mobile)
    notes = fields.Html(string="Notes", default=_get_default_notes)
    lead_source = fields.Selection([('1', 'Email Marketing'), ('2', 'Website - SSC India'),
                                    ('3', 'Website - Technians'), ('4', 'Facebook'), ('5', 'Data CC'),
                                    ('6', 'Linkedin'), ('7', 'Cold Call'), ('8', 'Apollo'),
                                    ('9', 'Reference'), ('10', 'Social Media'),
                                    ('11', 'fundoodata'), ('12', 'JustDial'), ('13', 'Sulekha'),
                                    ('14', 'Other'), ('15', 'Zomato'), ('16', 'Upwork'),
                                    ('17', 'Google Ads'), ('18', 'Phone Call')], string="Lead Source",
                                   store=True, readonly=False, tracking=True, default='18')
    interaction_source = fields.Char(string="Interaction Source", default="Phone call")
    source_id = fields.Many2one('utm.source', string="UTM Source")
    medium_id = fields.Many2one('utm.medium', string="UTM Medium")