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
    account_move_line_ids = fields.One2many('account.move.line', 'commision_id')
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
                    ('sale_line_ids','!=',False),
                    ('move_id.invoice_user_id','=',record.user_id.id),
                    ('move_id.invoice_date','>=',record.date_start),
                    ('move_id.invoice_date', '<=', record.date_end),
                    ('move_id.state','in',['posted']),
                    #('commision_id.state','!=','done')
                ]
                sale_lines = self.env['account.move.line'].search(domain)

                ids_sales = []

                total_base = 0
                overrun_sale = 0

                for line in sale_lines:
                    if line.commision_id and line.commision_id == 'done':
                        continue
                    '''
                    price_unit = line.price_unit
                    
                    price_origin = line.price_unit_origin
                    if not price_origin or price_origin == 0:
                        price_origin = line.price_unit
                        sql = f''UPDATE account_move_line   SET price_unit_origin = {price_origin}  WHERE id = {line.id}''
                        self.env.cr.execute(sql)
                        #line.price_unit_origin = price_unit

                    diffx = price_unit - price_origin
                    sql = f''UPDATE account_move_line   SET diff_price = {diffx}  WHERE id = {line.id}''
                    self.env.cr.execute(sql)
                    #line.diff_price = diffx
                    '''

                    ids_sales.append(line.id)

                    #line.get_price_subtotal_origin()

                    total_base += line.price_subtotal
                    #overrun_sale += line.price_subtotal_overrun
                self.account_move_line_ids = [(6, 0, ids_sales)] if ids_sales else None

                #raise ValueError(total_base)

                self.amount_total_base_sale = total_base
                self.comission_amount_total_base_sale = total_base * ( record.percentage_total_base_sale / 100 )
                #self.overrun_sale = overrun_sale
                #self.comission_overrun_sale = overrun_sale * ( record.percentage_overrun_sale / 100 )
                self.amount_total = self.comission_amount_total_base_sale
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



