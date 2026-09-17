from odoo import api, exceptions, fields, models
import phonenumbers


class PhoneCalls(models.Model):
    _name = 'phone.calls'
    _description = 'Phone Calls'
    _inherit = 'mail.thread'

    name = fields.Char(string="Sequence", tracking=True)
    call_from = fields.Char(string="Caller Phone", tracking=True)
    call_to = fields.Integer(string="Receiver Phone", tracking=True)
    call_start_time = fields.Datetime(string="Call Started", tracking=True)
    call_end_time = fields.Datetime(string="Call Ended", tracking=True)
    call_duration = fields.Char(string="Duration", compute="_compute_duration", store=True)
    call_notes = fields.Html(string="Notes", tracking=True)
    call_type = fields.Selection([('in', 'Inbound'), ('out', 'Outbound')], string="Type", store=True, readonly=False,
                                 tracking=True)
    call_status = fields.Selection([('draft', 'Unknown'), ('missed', 'Missed'), ('received', 'Answered'),
                                    ('disconnected', 'Disconnected')], string="Status", default="draft", store=True,
                                   readonly=False, tracking=True)
    call_summary_id = fields.Many2one('calls.summary', string="Summary", tracking=True)
    call_tag_ids = fields.Many2many('calls.tags', string="Tags", tracking=True)
    call_responsible_id = fields.Many2one('res.users', string="Responsible", tracking=True)
    similar_calls = fields.Integer(string='Similar Calls', compute='similar_calls_count')

    def similar_calls_count(self):
        for record in self:
            record.similar_calls = self.env['phone.calls'].search_count([('call_from', 'ilike', self.call_from),
                                                                         ('id', '!=', self.id)])

    # Compute call duration from call start time and end time
    @api.depends("call_start_time", "call_end_time")
    def _compute_duration(self):
        for record in self:
            if record.call_start_time and record.call_end_time:
                duration = (record.call_end_time - record.call_start_time)
                record.call_duration = duration
            else:
                record.call_duration = 0.0

    # # Override Create method to do necessary changes before saving any record
    # @api.model
    # def create(self, vals):
    #     vals['name'] = self.env['ir.sequence'].next_by_code('calls.sequence')
    #     res_id = super(PhoneCalls, self).create(vals)
    #     return res_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('calls.sequence') or '/'

        return super(PhoneCalls, self).create(vals_list)

    # Server Action to Format Phone number manually
    def calls_format_phone(self):
        for record in self:
            mobile = record.call_from
            if (mobile):
                formatted_phone_number = phonenumbers.format_number(phonenumbers.parse(mobile,
                                                                                       self.env.company.country_id.code),
                                                                    phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                record.write({'call_from': formatted_phone_number})


# Function to return calls from similar phone number
class search(models.Model):
    _inherit = 'phone.calls'

    def get_similar_calls(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Calls',
            'view_mode': 'tree,form',
            'res_model': 'phone.calls',
            'domain': [('call_from', 'ilike', self.call_from), ('id', '!=', self.id)],
            'context': "{'create': True}"
        }