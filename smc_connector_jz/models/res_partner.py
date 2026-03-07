from odoo import api, fields, models

class AreaEmpresarialSmc(models.Model):
    _name = "area.empresarial.smc"
    _description = "area.empresarial.smc"
    name =  fields.Char()


class ResPartner(models.Model):
    _inherit = "res.partner"
    type_negocio_area_smc = fields.Selection([
        ('Armadora','Armadora'),
        ('Maquiladora','Maquiladora')
    ],string="Tipo Negocio")
    area_empresarial_smc = fields.Many2one('area.empresarial.smc',string="Area Empresarial")
    clave_colonia_smc = fields.Many2one('catalogos.colonias',string='Colonia')