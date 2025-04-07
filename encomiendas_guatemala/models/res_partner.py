from odoo import api, fields, models
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit       = 'res.partner'
    use_whatsapp = fields.Boolean(string='Tiene Wasap')
    file_vat     = fields.Binary(string="Adjunto Documento")
    name_file_vat     = fields.Char()
    dpi = fields.Char()
    #name_invoice = fields.Char(string="Nombre Factura")
    #adress_invoice = fields.Char(string="Dirección Factura")
    #date_born = fields.Date(string="Fecha Nacimiento")
    #is_destinatario = fields.Boolean()

    @api.model
    def default_get(self, default_fields):
        """Add the company of the parent as default if we are creating a child partner.
        Also take the parent lang by default if any, otherwise, fallback to default DB lang."""
        values = super().default_get(default_fields)



        # protection for `default_type` values leaking from menu action context (e.g. for crm's email)
        values['is_company'] = False

        return values

    def write(self,values):
        #raise ValueError(values)
        res = super().write(values)
        return res

