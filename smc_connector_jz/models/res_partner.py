from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"
    type_negocio_area_smc = fields.Selection([
        ('Armadora','Armadora'),
        ('Maquiladora','Maquiladora')
    ],string="Tipo Negocio")
    area_empresarial_smc = fields.Char(string="Area Empresarial")
    #clave_colonia_smc = fields.Many2one('catalogos.colonias',string='Colonia')