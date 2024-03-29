# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models




class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    sql_server_host = fields.Char(related="company_id.sql_server_host",readonly=False)
    sql_server_user = fields.Char(related="company_id.sql_server_user",readonly=False)
    sql_server_password = fields.Char(related="company_id.sql_server_password",readonly=False)
    sql_server_database = fields.Char(related="company_id.sql_server_database",readonly=False)

    nine_box_start_date = fields.Date(related="company_id.nine_box_start_date",readonly=False)
    nine_box_end_date = fields.Date(related="company_id.nine_box_end_date",readonly=False)
    nine_box_days_per_month = fields.Integer(related="company_id.days_per_month",readonly=False)
    nine_box_type = fields.Integer(related="company_id.type",readonly=False)

    def sync_nine_box(self):
        self.sync_nine_box()