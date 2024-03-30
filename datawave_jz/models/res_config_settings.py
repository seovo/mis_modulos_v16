# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models




class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ################
    sql_server_host = fields.Char(related="company_id.sql_server_host",readonly=False)
    sql_server_user = fields.Char(related="company_id.sql_server_user",readonly=False)
    sql_server_password = fields.Char(related="company_id.sql_server_password",readonly=False)
    sql_server_database = fields.Char(related="company_id.sql_server_database",readonly=False)

    ################
    tenant_id = fields.Integer(related="company_id.tenant_id",readonly=False)

    # range filters
    # ABC
    abc_a_start = fields.Float(related="company_id.abc_a_start",readonly=False)
    abc_a_end = fields.Float(related="company_id.abc_a_end",readonly=False)

    abc_b_start = fields.Float(related="company_id.abc_b_start",readonly=False)
    abc_b_end = fields.Float(related="company_id.abc_b_end",readonly=False)

    abc_c_start = fields.Float(related="company_id.abc_c_start",readonly=False)
    abc_c_end = fields.Float(related="company_id.abc_c_end",readonly=False)

    # XYZ
    xyz_x_start = fields.Float(related="company_id.xyz_x_start",readonly=False)
    xyz_x_end = fields.Float(related="company_id.xyz_x_end",readonly=False)

    xyz_y_start = fields.Float(related="company_id.xyz_y_start",readonly=False)
    xyz_y_end = fields.Float(related="company_id.xyz_y_end",readonly=False)

    xyz_z_start = fields.Float(related="company_id.xyz_z_start",readonly=False)
    xyz_z_end = fields.Float(related="company_id.xyz_z_end",readonly=False)

    # ABC MC
    abc_a_start_mc = fields.Float(related="company_id.abc_a_start_mc",readonly=False)
    abc_a_end_mc = fields.Float(related="company_id.abc_a_end_mc",readonly=False)

    abc_b_start_mc = fields.Float(related="company_id.abc_b_start_mc",readonly=False)
    abc_b_end_mc = fields.Float(related="company_id.abc_b_end_mc",readonly=False)

    abc_c_start_mc = fields.Float(related="company_id.abc_c_start_mc",readonly=False)
    abc_c_end_mc = fields.Float(related="company_id.abc_c_end_mc",readonly=False)

    # XYZ
    xyz_x_start_mc = fields.Float(related="company_id.xyz_x_start_mc",readonly=False)
    xyz_x_end_mc = fields.Float(related="company_id.xyz_x_end_mc",readonly=False)

    xyz_y_start_mc = fields.Float(related="company_id.xyz_y_start_mc",readonly=False)
    xyz_y_end_mc = fields.Float(related="company_id.xyz_y_end_mc",readonly=False)

    xyz_z_start_mc = fields.Float(related="company_id.xyz_z_start_mc",readonly=False)
    xyz_z_end_mc = fields.Float(related="company_id.xyz_z_end_mc",readonly=False)

    ####################
    nine_box_start_date = fields.Date(related="company_id.nine_box_start_date",readonly=False)
    nine_box_end_date = fields.Date(related="company_id.nine_box_end_date",readonly=False)
    nine_box_days_per_month = fields.Integer(related="company_id.nine_box_days_per_month",readonly=False)
    nine_box_type = fields.Integer(related="company_id.nine_box_type",readonly=False)

    def sync_nine_box(self):
        self.company_id.sync_nine_box()