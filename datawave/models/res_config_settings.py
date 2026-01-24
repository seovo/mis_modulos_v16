from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    datawave_ss_tienda        = fields.Selection([('1','Z*Sigma*SQRT(LT)'),('2','0.5*Forecast*LT')],'Método stock de seguridad tienda',
                                         config_parameter='datawave.metodo_ss_tienda',default='1')
    datawave_max_tienda       = fields.Selection([('1', '(LT+FREQ)*Forecast+SS'), ('2', '14*Forecast+SS')],
                                          'Método stock máximo Tienda',
                                          config_parameter='datawave.metodo_max_tienda', default='1')
    datawave_frecuencia_tienda = fields.Selection([('1', 'Fija'), ('2', 'LT+Delta'), ('3', 'Días objetivo')],
                                                         default='1',
                                                         config_parameter='datawave.metodo_frecuencia_tienda')




    datawave_ss_cd             = fields.Selection([('1','Z*Sigma*SQRT(LT)'),('2','Forecast*LT')],'Método stock de seguridad CD',
                                        config_parameter='datawave.metodo_ss_cd',default='1')
    datawave_max_cd            = fields.Selection([('1', '2*Forecast*LT+Forecast*FREQ'), ('2', '(LT+FREQ)*Forecast+SS')],
                                           'Método stock máximo CD',
                                           config_parameter='datawave.metodo_max_cd', default='1')
    datawave_frecuencia_cd     = fields.Selection([('1', 'Empírica'), ('2', 'EOQ'), ('3', 'InvObj'),('4','LT+Delta'),('5','MOQ/Dem')],
                                                  default='1',
                                                  config_parameter='datawave.metodo_frecuencia_cd')



    datawave_sigma_days = fields.Integer('Días usados para Sigma tienda',config_parameter='datawave.ventana_sigma_dias')
    datawave_z_tienda   = fields.Float('Z por tienda (fallback)',config_parameter='datawave.z_tienda')

