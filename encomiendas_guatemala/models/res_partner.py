from odoo import api, fields, models
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit       = 'res.partner'
    use_whatsapp = fields.Boolean(string='Tiene Wasap')
    file_vat     = fields.Binary(string="Adjunto Documento")
    name_file_vat     = fields.Char()
    dpi = fields.Char()
    name_invoice = fields.Char(string="Nombre Factura")
    adress_invoice = fields.Char(string="Dirección Factura")
    date_born = fields.Date(string="Fecha Nacimiento")
    is_destinatario = fields.Boolean()
    carrier_id = fields.Many2one('delivery.carrier', string="Caja Banrural")

    @api.model
    def create(self,vals):
        res = super().create(vals)
        if 'name_invoice' in vals:
            dx = {
                'name': vals['name_invoice'] ,
                'parent_id' : res.id
            }
            if 'adress_invoice' in vals:
                dx.update({'street': vals['adress_invoice']})
            if 'date_born' in vals:
                dx.update({'date_born': vals['date_born']})
            if 'carrier_id' in vals:
                dx.update({'carrier_id': vals['carrier_id']})
            self.env['res.partner'].create(dx)
        return res

    @api.model
    def default_get(self, default_fields):
        values = super().default_get(default_fields)
        values['is_company'] = False

        return values

    def write(self,values):
        #raise ValueError(values)
        res = super().write(values)
        return res

