from odoo import api, fields, models, _


class ConfigCostAnnual(models.Model):
    _name = 'config.cost.annual'
    _description = 'Para costo anual'
    
    company_id = fields.Many2one('res.company', string='Company', required=True)
    cost_inv = fields.Many2many('account.account', 'cost_inv_conf', 'config_id', 'account_id', string="Cos. Inv. inicial productos terminados")
    cost_production_prod = fields.Many2many('account.account', 'cost_production_prod_conf', 'config_id', 'account_id', string="Cos. produccion productos terminados")    
    cost_product_sale = fields.Many2many('account.account', 'cost_product_sale_conf', 'config_id', 'account_id', string="Cos. produccion productos ventas")
    cost_inv_final_term = fields.Many2many('account.account', 'cost_inv_final_term_conf', 'config_id', 'account_id', string="Cos. Inv final de productos terminados")
    ajust = fields.Many2many('account.account', 'ajust_conf', 'config_id', 'account_id', string="Ajustes diversos")

    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Solo puede haber una configuracion por compañia'),
    ]


class ConfigCostMensual(models.Model):
    _name = 'config.cost.mensual'
    _description = 'Para costo mensual'

    company_id = fields.Many2one('res.company', string='Company', required=True)
    materiales_direct = fields.Many2many('account.account', 'cost_materi_direc_conf', 'config_id', 'account_id', string="Materiales y suministros directos")
    mano_obra_direct = fields.Many2many('account.account', 'cost_mano_obra_direc_conf', 'config_id', 'account_id', string="Mano de obra directa")
    otros_costos = fields.Many2many('account.account', 'cost_otros_conf', 'config_id', 'account_id', string="Otros costos directos")
    materiales_indirect = fields.Many2many('account.account', 'cost_materi_ind_conf', 'config_id', 'account_id', string="Materiales y suministros indirectos")
    mano_obra_indirect = fields.Many2many('account.account', 'cost_mano_obra_indirec_conf', 'config_id', 'account_id', string="Mano de obra indirecta")
    otros_gastos_indirect = fields.Many2many('account.account', 'gast_otros_ind_conf', 'config_id', 'account_id', string="Otros gastos de produccion indirectos")

    _sql_constraints = [
        ('company_uniq', 'unique(company_id)', 'Solo puede haber una configuracion por compañia'),
    ]

