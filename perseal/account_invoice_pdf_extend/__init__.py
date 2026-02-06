# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# from odoo import api, SUPERUSER_ID


def _post_install(env):
    # env = api.Environment(cr, SUPERUSER_ID, {})
    company_ids = env["res.company"].search([])
    for company_id in company_ids:
        company_id.write({"show_code_invoice": True})
    return True


def _uninstall_hook(env):
    # env = api.Environment(cr, SUPERUSER_ID, {})
    company_ids = env["res.company"].search([])
    for company_id in company_ids:
        company_id.write({"show_code_invoice": False})
    return True