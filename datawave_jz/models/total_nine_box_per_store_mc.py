from odoo import models, exceptions, fields , _


#stored_procedure": "exec [dbo].[GetTotalNineBoxPerStoreMc] '2020-01-01' , '2020-07-31' ,  20 , 1  , 2 , 1",

class TotalNineNoxPerStoreMC(models.Model):
    _name = "total.nine.box.per.store.mc"
    _description = "total.nine.box.per.store.mc"
    id_sql = fields.Integer()
    sku = fields.Char()
    total_quantity_sold = fields.Char()
    total_sale_cost = fields.Float()
    total_sale_amount = fields.Float()
    contribution_margin = fields.Float()
    accumulated_sale_cost_percentage = fields.Float()
    abc = fields.Char()
    accumulated_contribution_margin_percentage = fields.Float()
    xyz = fields.Char()
    nine_box = fields.Char()
    average_quantity = fields.Float()
    cost_per_unit = fields.Float()
    inventory_average_cost = fields.Float()
    stock_days = fields.Float()
    gmroi = fields.Float()
    name = fields.Char()
    company_id = fields.Many2one('res.company')