from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    datawave_ss_tienda = fields.Selection([('1','Z*Sigma*SQRT(LT)'),('2','0.5*Forecast*LT')],'Método stock de seguridad tienda',
                                         config_parameter='datawave.metodo_ss_tienda',default='1')


    datawave_ss_cd = fields.Selection([('1','Z*Sigma*SQRT(LT)'),('2','Forecast*LT')],'Método stock de seguridad CD',
                                        config_parameter='datawave.metodo_ss_cd',default='1')

    datawave_sigma_days = fields.Integer('Días usados para Sigma tienda',config_parameter='datawave.ventana_sigma_dias')
    datawave_z_tienda   = fields.Float('Z por tienda (fallback)',config_parameter='datawave.z_tienda')
    datawave_metodo_frecuencia_tienda = fields.Selection([('1','Fija'),('2','LT+Delta'),('3','Días objetivo')],
                                                         default='1',
                                                         config_parameter='datawave.metodo_frecuencia_tienda')
