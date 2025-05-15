from odoo import api, Command, fields, models, _
from odoo.tools import float_is_zero, format_amount, format_date, html_keep_url, is_html_empty
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    product_repair_id = fields.Many2one('product.product',string="Producto a reparar")
    cat_bycle_id = fields.Many2one('category.bycle',string='Categoria')
    under_warranty_bycle = fields.Selection([('taller','Taller'),('purchase','Compra')],string='Bajo Garantia')

    def action_quotation_send(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        self.ensure_one()
        #self.order_line._validate_analytic_distribution()
        lang = self.env.context.get('lang')
        #mail_template = self._find_mail_template()
        #if mail_template and mail_template.lang:
        #    lang = mail_template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'sale.order',
            'default_res_ids': self.ids,
            #'default_template_id': mail_template.id if mail_template else None,
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
