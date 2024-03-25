from odoo import models, exceptions, fields , _

class TotalNineBox(models.Model):
    _name = "total.nine.box"
    _description = "total.nine.box"

    '''
    DECLARE @StartDate DATE = '20200101';
    DECLARE @EndDate DATE = '20200731';
    DECLARE @DaysPerMonth INT = 20;
    DECLARE @Type INT = 1;

    EXEC GetTotalNineBox @StartDate, @EndDate, @DaysPerMonth, @Type;
    
    "stored_procedure": "exec [dbo].[GetTotalNineBox] '2020-01-01' , '2020-07-31' ,  20 , 1  , 1",
    '''
    id_sql = fields.Integer()
    sku = fields.Char()
    total_quantity_sold = fields.Float()
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