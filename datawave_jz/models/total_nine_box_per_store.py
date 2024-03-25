from odoo import models, exceptions, fields , _


#stored_procedure": "exec [dbo].[GetTotalNineBoxPerStoreMc] '2020-01-01' , '2020-07-31' ,  20 , 1  , 2 , 1",

class TotalNineNoxPerStore(models.Model):
    _name = "total.nine.box.per.store"
    _description = "total.nine.box.per.store"
    id_sql = fields.Integer()
    sku = fields.Char()
    name = fields.Char()
    total_quantity_sold = fields.Char()
    total_sale_cost = fields.Float()
    accumulated_sale_cost_percentage = fields.Float()
    abc = fields.Char()
    variability_percentage = fields.Float()
    xyz = fields.Char()
    nine_box = fields.Char()
    average_quantity = fields.Float()
    cost_per_unit = fields.Float()
    inventory_average_cost = fields.Float()
    stock_days = fields.Float()
