# from odoo import fields, models, api
# import phonenumbers
#
#
# class CRMLead(models.Model):
#     _inherit = 'crm.lead'
#     _description = 'CRM Lead'
#
#     lead_calls_count = fields.Integer(compute='compute_calls')
#
#     def compute_calls(self):
#         for record in self:
#             record.lead_calls_count = self.env['phone.calls'].search_count([('lead_id', '=', self.id)])
#
#     @api.model
#     def create(self, vals):
#         if vals.get('phone') or vals.get('mobile'):
#             company = self.env.company
#             if company and company.country_id and company.country_id.code:
#                 if 'phone' in vals and vals['phone']:
#                     search_lead_phone = vals['phone']
#                     formatted_lead_phone = phonenumbers.format_number(
#                         phonenumbers.parse(search_lead_phone, company.country_id.code),
#                         phonenumbers.PhoneNumberFormat.INTERNATIONAL)
#                     vals['phone'] = formatted_lead_phone
#                 if 'mobile' in vals and vals['mobile']:
#                     search_lead_mobile = vals['mobile']
#                     formatted_lead_mobile = phonenumbers.format_number(
#                         phonenumbers.parse(search_lead_mobile, company.country_id.code),
#                         phonenumbers.PhoneNumberFormat.INTERNATIONAL)
#                     vals['mobile'] = formatted_lead_mobile
#         res_id = super(CRMLead, self).create(vals)
#         return res_id
#
#     def write(self, vals):
#         if 'phone' in vals or 'mobile' in vals:
#             company = self.env.company
#             if company and company.country_id and company.country_id.code:
#                 for record in self:
#                     if 'phone' in vals and vals['phone']:
#                         search_lead_phone = vals['phone'] or record.phone
#                         formatted_lead_phone = phonenumbers.format_number(
#                             phonenumbers.parse(search_lead_phone, company.country_id.code),
#                             phonenumbers.PhoneNumberFormat.INTERNATIONAL)
#                         vals['phone'] = formatted_lead_phone
#
#                     if 'mobile' in vals and vals['mobile']:
#                         search_lead_mobile = vals['mobile'] or record.mobile
#                         formatted_lead_mobile = phonenumbers.format_number(
#                             phonenumbers.parse(search_lead_mobile, company.country_id.code),
#                             phonenumbers.PhoneNumberFormat.INTERNATIONAL)
#                         vals['mobile'] = formatted_lead_mobile
#         res = super(CRMLead, self).write(vals)
#         return res
#
#
# class search(models.Model):
#     _inherit = 'crm.lead'
#
#     def get_lead_calls(self):
#         self.ensure_one()
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Calls',
#             'view_mode': 'list,form',
#             'res_model': 'phone.calls',
#             'domain': [('lead_id', '=', self.id)],
#         }
#
#
# class PhoneCallCrm(models.Model):
#     _inherit = 'phone.calls'
#     _description = 'Phone Calls'
#
#     lead_id = fields.Many2one('crm.lead', string="Lead", tracking=True)
#
#     @api.model
#     def create(self, vals):
#         search_phone = vals['call_from']
#         formatted_phone = phonenumbers.format_number(phonenumbers.parse(search_phone, self.env.company.country_id.code),
#                                                      phonenumbers.PhoneNumberFormat.INTERNATIONAL)
#         vals['call_from'] = formatted_phone
#         lead_exist = self.env['crm.lead'].search([('mobile', 'ilike', formatted_phone)], limit=1,
#                                                  order='id desc')
#         if lead_exist:
#             if self.env['ir.config_parameter'].get_param('ts_phone_crm.lead_call_id'):
#                 vals['lead_id'] = lead_exist.id
#             else:
#                 vals['lead_id'] = False
#         res_id = super(PhoneCallCrm, self).create(vals)
#         if lead_exist:
#             if (vals['lead_id'] != False):
#                 body = 'Linked with existing Contact - ' + lead_exist.name
#                 res_id.message_post(body=body)
#         return res_id
#
#     def write(self, vals):
#         if 'call_from' in vals:
#             search_phone = vals['call_from']
#             formatted_phone = phonenumbers.format_number(
#                 phonenumbers.parse(search_phone, self.env.company.country_id.code),
#                 phonenumbers.PhoneNumberFormat.INTERNATIONAL)
#             vals['call_from'] = formatted_phone
#             lead_exist = self.env['crm.lead'].search([('mobile', 'ilike', formatted_phone)], limit=1,
#                                                      order='id desc')
#             if lead_exist:
#                 if self.env['ir.config_parameter'].get_param('ts_phone_crm.lead_call_id'):
#                     vals['lead_id'] = lead_exist.id
#                 else:
#                     vals['lead_id'] = False
#         res = super(PhoneCallCrm, self).write(vals)
#         if 'lead_id' in vals and vals['lead_id'] != False:
#             lead = self.env['crm.lead'].browse(vals['lead_id'])
#             body = 'Linked with existing lead - ' + lead.name
#             self.message_post(body=body)
#         return res
#
#     def call_to_lead(self):
#         notes_content = ('<strong> Notes - </strong>' + str(self.call_notes) + '<br><strong> Summary - </strong>' +
#                          str(self.call_summary_id.name)) or ''
#         return {
#             'type': 'ir.actions.act_window',
#             'res_model': 'lead.calls.wizard',
#             'name': 'Create Lead from Call',
#             'view_mode': 'form',
#             'target': 'new',
#             'context': {'mobile': self.call_from, 'notes': notes_content, 'name': self.name}
#         }
#
#
# class ResConfigSetting(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     lead_call_id = fields.Boolean(string='CRM Lead')
#
#     @api.model
#     def get_values(self):
#         res = super(ResConfigSetting, self).get_values()
#         res.update(lead_call_id=self.env['ir.config_parameter'].sudo().get_param('ts_phone_crm.lead_call_id'))
#         return res
#
#     def set_values(self):
#         super(ResConfigSetting, self).set_values()
#         self.env['ir.config_parameter'].sudo().set_param('ts_phone_crm.lead_call_id', self.lead_call_id)


from odoo import fields, models, api
import phonenumbers
from phonenumbers import NumberParseException


class CRMLead(models.Model):
    _inherit = 'crm.lead'
    _description = 'CRM Lead'

    lead_calls_count = fields.Integer(compute='compute_calls')

    def compute_calls(self):
        for record in self:
            record.lead_calls_count = self.env['phone.calls'].search_count([('lead_id', '=', self.id)])

    @api.model_create_multi
    def create(self, vals_list):
        company = self.env.company
        if company and company.country_id and company.country_id.code:
            for vals in vals_list:
                if vals.get('phone'):
                    try:
                        vals['phone'] = phonenumbers.format_number(
                            phonenumbers.parse(vals['phone'], company.country_id.code),
                            phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                    except NumberParseException:
                        pass  # Keep original phone number if parsing fails

                if vals.get('mobile'):
                    try:
                        vals['mobile'] = phonenumbers.format_number(
                            phonenumbers.parse(vals['mobile'], company.country_id.code),
                            phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                    except NumberParseException:
                        pass  # Keep original mobile number if parsing fails

        return super(CRMLead, self).create(vals_list)

    def write(self, vals):
        if 'phone' in vals or 'mobile' in vals:
            company = self.env.company
            if company and company.country_id and company.country_id.code:
                for record in self:
                    if 'phone' in vals and vals['phone']:
                        try:
                            search_lead_phone = vals['phone'] or record.phone
                            formatted_lead_phone = phonenumbers.format_number(
                                phonenumbers.parse(search_lead_phone, company.country_id.code),
                                phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                            vals['phone'] = formatted_lead_phone
                        except NumberParseException:
                            pass  # Keep original phone number if parsing fails

                    if 'mobile' in vals and vals['mobile']:
                        try:
                            search_lead_mobile = vals['mobile'] or record.mobile
                            formatted_lead_mobile = phonenumbers.format_number(
                                phonenumbers.parse(search_lead_mobile, company.country_id.code),
                                phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                            vals['mobile'] = formatted_lead_mobile
                        except NumberParseException:
                            pass  # Keep original mobile number if parsing fails

        res = super(CRMLead, self).write(vals)
        return res


class search(models.Model):
    _inherit = 'crm.lead'

    def get_lead_calls(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Calls',
            'view_mode': 'list,form',
            'res_model': 'phone.calls',
            'domain': [('lead_id', '=', self.id)],
        }


class PhoneCallCrm(models.Model):
    _inherit = 'phone.calls'
    _description = 'Phone Calls'

    lead_id = fields.Many2one('crm.lead', string="Lead", tracking=True)

    # @api.model
    # def create(self, vals):
    #     search_phone = vals.get('call_from')
    #
    #     # Check if company and country_id exist before formatting
    #     company = self.env.company
    #     if search_phone and company and company.country_id and company.country_id.code:
    #         try:
    #             formatted_phone = phonenumbers.format_number(
    #                 phonenumbers.parse(search_phone, company.country_id.code),
    #                 phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    #             vals['call_from'] = formatted_phone
    #         except NumberParseException:
    #             # If parsing fails, keep the original phone number
    #             formatted_phone = search_phone
    #     else:
    #         # If no country code available, use the original phone number
    #         formatted_phone = search_phone
    #
    #     # Search for existing lead
    #     lead_exist = False
    #     if formatted_phone:
    #         lead_exist = self.env['crm.lead'].search(
    #             [('mobile', 'ilike', formatted_phone)],
    #             limit=1,
    #             order='id desc'
    #         )
    #
    #     if lead_exist:
    #         if self.env['ir.config_parameter'].sudo().get_param('ts_phone_crm.lead_call_id'):
    #             vals['lead_id'] = lead_exist.id
    #         else:
    #             vals['lead_id'] = False
    #
    #     res_id = super(PhoneCallCrm, self).create(vals)
    #
    #     if lead_exist and vals.get('lead_id'):
    #         body = 'Linked with existing Contact - ' + lead_exist.name
    #         res_id.message_post(body=body)
    #
    #     return res_id

    @api.model_create_multi
    def create(self, vals_list):
        company = self.env.company
        # Track, per-index, which lead (if any) got linked so we can post
        # the message after the records are actually created.
        linked_leads = {}

        for index, vals in enumerate(vals_list):
            search_phone = vals.get('call_from')

            if search_phone and company and company.country_id and company.country_id.code:
                try:
                    formatted_phone = phonenumbers.format_number(
                        phonenumbers.parse(search_phone, company.country_id.code),
                        phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                    vals['call_from'] = formatted_phone
                except NumberParseException:
                    # If parsing fails, keep the original phone number
                    formatted_phone = search_phone
            else:
                # If no country code available, use the original phone number
                formatted_phone = search_phone

            # Search for existing lead
            lead_exist = False
            if formatted_phone:
                lead_exist = self.env['crm.lead'].search(
                    [('phone', 'ilike', formatted_phone)],
                    limit=1,
                    order='id desc'
                )

            if lead_exist:
                if self.env['ir.config_parameter'].sudo().get_param('ts_phone_crm.lead_call_id'):
                    vals['lead_id'] = lead_exist.id
                    linked_leads[index] = lead_exist
                else:
                    vals['lead_id'] = False

        records = super(PhoneCallCrm, self).create(vals_list)

        for index, lead in linked_leads.items():
            body = 'Linked with existing Contact - ' + lead.name
            records[index].message_post(body=body)

        return records

    def write(self, vals):
        if 'call_from' in vals:
            search_phone = vals['call_from']

            # Check if company and country_id exist before formatting
            company = self.env.company
            if search_phone and company and company.country_id and company.country_id.code:
                try:
                    formatted_phone = phonenumbers.format_number(
                        phonenumbers.parse(search_phone, company.country_id.code),
                        phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                    vals['call_from'] = formatted_phone
                except NumberParseException:
                    # If parsing fails, keep the original phone number
                    formatted_phone = search_phone
            else:
                # If no country code available, use the original phone number
                formatted_phone = search_phone

            # Search for existing lead
            if formatted_phone:
                lead_exist = self.env['crm.lead'].search(
                    [('mobile', 'ilike', formatted_phone)],
                    limit=1,
                    order='id desc'
                )
                if lead_exist:
                    if self.env['ir.config_parameter'].sudo().get_param('ts_phone_crm.lead_call_id'):
                        vals['lead_id'] = lead_exist.id
                    else:
                        vals['lead_id'] = False

        res = super(PhoneCallCrm, self).write(vals)

        if 'lead_id' in vals and vals['lead_id']:
            lead = self.env['crm.lead'].browse(vals['lead_id'])
            body = 'Linked with existing lead - ' + lead.name
            self.message_post(body=body)

        return res

    def call_to_lead(self):
        notes_content = (
                '<strong> Notes - </strong>' + str(self.call_notes or '') +
                '<br><strong> Summary - </strong>' + str(self.call_summary_id.name if self.call_summary_id else '')
        )
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'lead.calls.wizard',
            'name': 'Create Lead from Call',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'mobile': self.call_from,
                'notes': notes_content,
                'name': self.name
            }
        }


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    lead_call_id = fields.Boolean(string='CRM Lead')

    @api.model
    def get_values(self):
        res = super(ResConfigSetting, self).get_values()
        res.update(
            lead_call_id=self.env['ir.config_parameter'].sudo().get_param('ts_phone_crm.lead_call_id')
        )
        return res

    def set_values(self):
        super(ResConfigSetting, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('ts_phone_crm.lead_call_id', self.lead_call_id)