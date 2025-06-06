from odoo import api, Command, fields, models, _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError
import ast

class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"
    is_whatsapp_evolution_api = fields.Boolean(string="Enviar Whatsapp")
    text_whatsapp_evolution_api = fields.Text(string='Texto Whatsapp')
    number_whatsapp_evolution_api = fields.Char(string='Enviar a')

    @api.onchange('res_ids','is_whatsapp_evolution_api')
    def change_res_ids_sale(self):
        if self.model in ['sale.order'] and self.is_whatsapp_evolution_api:
            url_main = self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')])

            array = ast.literal_eval(self.res_ids)

            objects = self.env[self.model].search([('id', 'in', array)])

            for object in objects:
                if self.model in ['sale.order'] and self.is_whatsapp_evolution_api:
                    if object.company_id.whatsapp_sale_msg_format:
                        url = object.action_preview_sale_order()['url']
                        url = f'''{url_main.value}{url}'''
                        testx = object.company_id.whatsapp_sale_msg_format.replace('%report',url)
                        self.text_whatsapp_evolution_api = testx

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    product_repair_id = fields.Many2one('product.product',string="Producto a reparar")
    cat_bycle_id = fields.Many2one('category.bycle',string='Categoria')
    warranty_bycle_id = fields.Many2one('garantia.bycle',string='Ingreso a servicio')

    def action_quotation_send(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        self.ensure_one()
        #self.order_line._validate_analytic_distribution()
        lang = self.env.context.get('lang')
        mail_template = self.company_id.whatsapp_template_id
        #if mail_template and mail_template.lang:
        #    lang = mail_template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'sale.order',
            'default_res_ids': self.ids,
            'default_template_id': mail_template.id if mail_template else None,
            'default_composition_mode': 'comment',
            #'mark_so_as_sent': True,
            #"'default_email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
            #'proforma': self.env.context.get('proforma', False),
            #'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
            'default_is_whatsapp_evolution_api': True ,
            'default_subtype_is_log': True ,
            'default_text_whatsapp_evolution_api': 'OK'

        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }




class CategoryBycle(models.Model):
    _name = 'category.bycle'
    _description = 'category.bycle'
    name = fields.Char()

class GarantiaBycle(models.Model):
    _name = 'garantia.bycle'
    _description = 'category.bycle'
    name = fields.Char()