from odoo import models, exceptions, fields , _

class ListPowerBi(models.Model):
    _name = "list.powerbi"
    _description = "list.powerbi"
    name = fields.Char(required=True)
    url = fields.Char(compute='get_url')
    def get_url(self):
        for record in self:
            record.url = '/ui/powerbi/' + str(record.id)

    ####
    authentication_mode = fields.Selection([
        ('serviceprincipal','Service Principal'),
        ('masteruser','MasterUser')
    ],default='serviceprincipal',required=True)
    client_id = fields.Char()
    authority_url = fields.Char(default='https://login.microsoftonline.com/organizations',required=True)
    power_bi_user = fields.Char()
    power_bi_pass = fields.Char()
    tenant_id = fields.Char()
    client_secret = fields.Char()
    scope_base = fields.Char(default='https://analysis.windows.net/powerbi/api/.default',required=True)
    workspace_id = fields.Char()
    report_id = fields.Char()

    def powerbi_ui(self):
        self.ensure_one()

        # self.rename_sequence_shf()
        url = 'ui/powerbi/' + str(self.id)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': url,
        }