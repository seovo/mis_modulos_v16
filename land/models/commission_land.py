from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from datetime import date

class CommissionRiman(models.Model):
    _name        = 'commission.land'
    _description = 'commission.land'
    name                  = fields.Char()
    date_start            = fields.Date(string="Fecha Inicial",required=True)
    date_end              = fields.Date(string="Fecha Final",required=True)
    user_id               = fields.Many2one('res.users',string="Vendedor",required=True)
    goal                  = fields.Float(string="Meta",required=True)
    sale_order_ids        = fields.One2many('sale.order', 'commision_id')
    state                 = fields.Selection(
        [('draft','Borrador'),('done','Realizado'),('cancel','Cancel')],
        default='draft'
    )
    note                                = fields.Text()
    amount_total_base_sale              = fields.Float(string="Monto Base Ventas")
    percentage_total_base_sale          = fields.Float(string="Porcentage Monto Base")
    comission_amount_total_base_sale    = fields.Float(string="Comission Monto Base")
    #overrun_sale                        = fields.Float(string="Monto Sobrecosto")
    #percentage_overrun_sale             = fields.Float(string="Porcentage Monto Sobrecosto")
    #comission_overrun_sale              = fields.Float(string="Comission Monto Sobrecosto")
    amount_total                        = fields.Float(string="Monto Total")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)


    @api.onchange('date_start')
    def change_date_start(self):
        for record in self:
            if record.date_start:
                fecha_especifica = date(record.date_start.year, record.date_start.month + 1, 1) - timedelta(days=1)
                record.date_end = fecha_especifica


    @api.model
    def default_get(self,fieldsx):
        res = super().default_get(fieldsx)
        date_now = fields.Datetime.now() - timedelta(hours=5)

        fecha_especifica = date(date_now.year, date_now.month, 1)  # Año, mes, día
        res.update({
            'date_start': fecha_especifica
        })
        #raise ValidationError(date_now.date())
        return res

    @api.model
    def create(self, vals):
        # raise ValueError(vals['type'])
        seq_date = None
        codex = 'commission_land'

        if 'company_id' in vals:
            vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                codex, sequence_date=seq_date) or 'New'
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code(codex, sequence_date=seq_date) or 'New'
        result = super(CommissionRiman, self).create(vals)
        return result


    @api.onchange('user_id')
    def onchange_user_id(self):
        for record in self:
            meta = 0
            for team in self.env['crm.team'].search([]):
                for member in team.member_ids:
                    if member == record.user_id:
                        meta = team.invoiced_target
                        record.percentage_total_base_sale = team.percentage_total_base_sale
                        #record.percentage_overrun_sale = team.percentage_overrun_sale
                        break
            record.goal = meta


    @api.onchange('date_start','date_end','user_id','goal')
    def onchange_lines(self):
        for record in self:
            if record.date_start and record.date_end and record.user_id and record.goal:
                domain = [
                    #('sale_line_ids','!=',False),
                    ('user_id','=',record.user_id.id),
                    ('date_order','>=',record.date_start),
                    ('date_order', '<=', record.date_end),
                    ('state','not in',['draft','cancel']),
                    #('commision_id.state','!=','done')
                ]
                sales = self.env['sale.order'].search(domain)

                ids_sales = []

                total_base = 0
                comission_amount = 0
                overrun_sale = 0

                for sale in sales:
                    if sale.commision_id and sale.commision_id.state == 'done':
                        continue


                    ids_sales.append(sale.id)

                    #line.get_price_subtotal_origin()

                    total_base += sale.amount_total
                    comission_amount += sale.commision_land
                    #overrun_sale += line.price_subtotal_overrun
                self.sale_order_ids = [(6, 0, ids_sales)] if ids_sales else None

                #raise ValueError(total_base)

                self.amount_total_base_sale = total_base
                self.comission_amount_total_base_sale = comission_amount
                #self.overrun_sale = overrun_sale
                #self.comission_overrun_sale = overrun_sale * ( record.percentage_overrun_sale / 100 )
                self.amount_total = comission_amount
    def action_cancel(self):
        self.state = 'cancel'


    def action_draft(self):

        self.state = 'draft'

    #def action_done(self):
    #    self.state = 'done'
    def action_confirm(self):
        if self.state == 'draft':
            self.onchange_lines()
            self.onchange_lines()
            if self.amount_total >= self.goal:
                self.state = 'done'
            else:
                raise ValidationError('NO CUMPLE LA META')

    def update_comission(self):
        if self.state == 'draft':
            self.onchange_user_id()
            self.onchange_lines()



