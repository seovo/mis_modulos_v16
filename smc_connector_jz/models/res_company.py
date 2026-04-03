from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"
    smc_category_ids = fields.Many2many('product.category',string="Categorias")
    smc_excluded_partner_ids = fields.Many2many('res.partner','smc_excluded_partner_ids',string="Excluidos")
    smc_usuario = fields.Char()
    smc_password = fields.Char()
    smc_dt = fields.Char()
    smc_name_dt = fields.Char()
    smc_active = fields.Boolean()
    smc_journal_ids = fields.Many2many('account.journal','smc_journal_ids',string="Diarios Permitidos")
    smc_date_after = fields.Date(string="Despues de")

    smc_channel_id =  fields.Many2one('mail.channel', string='Canal Anuncios')
    #mail.thread
    #mail.channel



    def  action_view_moves_smc(self,retornar=False,domain_add=[]):
        domain = [('company_id','=',self.id),('state','=','posted')]

        if self.smc_excluded_partner_ids:
            domain.append(('partner_id','not in', self.smc_excluded_partner_ids.ids))

        if self.smc_category_ids:
            domain.append(('line_ids.product_id.categ_id','in',self.smc_category_ids.ids))

        if self.smc_journal_ids:
            domain.append(('journal_id','in',self.smc_journal_ids.ids))


        if self.smc_date_after:
            domain.append(('invoice_date','>=',self.smc_date_after))

        if retornar:
            if domain_add:
                domain = domain + domain_add
            else:
                domain.append(
                    ('state_smc', '=', False),
                    ('partner_id.type_negocio_area_smc', '!=', False),
                    ('partner_id.area_empresarial_smc', '!=', False),
                    ('partner_id.clave_colonia_smc', '!=', False)
                )

            moves = self.env['account.move'].search(domain)
            return moves

        moves = self.env['account.move'].search(domain)

        return {
            "name": f"FACTURAS DE {self.name}",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            #"view_id": self.env.ref('land.add_terreno_sale').id,
            "res_model": "account.move",
            #"res_id": self.id,
            "target": "current",
            "domain":  [('id','in',moves.ids)] ,
            #"context": {
            #    'default_order_id': self.id
            #}

        }


