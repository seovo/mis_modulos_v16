from odoo import api, fields, models , _
#from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

import psycopg2
from psycopg2 import sql


class MigrateIrModelFields(models.Model):
    _name  = 'migrate.ir.model.fields'
    name = fields.Char(required=True)
    model = fields.Char(required=True)
    ir_model_fields_id = fields.Many2one('ir.model.fields',compute="get_ir_model_fields_id")
    migrate_id = fields.Many2one('migrate.jz',required=True)
    id_sql = fields.Integer()

    def get_ir_model_fields_id(self):
        for record in self:
            value = None
            model = self.env['ir.model.fields'].search([('name','=',record.name),('model_id.model','=',record.model)])
            if model:
                value = model.id
            record.ir_model_fields_id =  value


class MigrateModelColumnsJz(models.Model):
    _name  = 'migrate.model.columns.jz'
    name             = fields.Char(required=True)
    ignore           = fields.Boolean(string="Ignorar")
    type_field       = fields.Selection([
        ('jsonb_text','jsonb a Texto'),
        ('text_jsonb','Texto a jsonb')],string='Convertir a')
    migrate_model_id = fields.Many2one('migrate.model.jz')
    value_set        = fields.Text()
    is_field         = fields.Boolean(string="Es un Campo Odoo")

    #insert_as_jsonb   = fields.Boolean()
