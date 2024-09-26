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
    date_commission       = fields.Date(string="Fecha Comission",required=True)
    user_id               = fields.Many2one('res.users',string="Vendedor",required=True)
    team_id               = fields.Many2one('crm.team',string="Equipo Venta",required=True)
    #goal                  = fields.Float(string="Meta",required=True)
    line_ids              = fields.One2many('commission.land.line', 'commission_land_id')
    state                 = fields.Selection(
        [('draft','Pendiente'),('done','Pagado'),('cancel','Cancelado')],
        default='draft'
    )
    note                                = fields.Text()
    amount_base                         = fields.Float(string="Comission Base")
    amount_discount                     = fields.Float(string=" - Descuento")
    amount_bonus                        = fields.Float(string=" + Bono ")

    amount_total                        = fields.Float(string="Monto Total")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    type_period_comission = fields.Selection([
        ('month', 'Mensual'),
        ('half', 'Quincenal'),
        ('week', 'Semanal'),

    ],
    string="Periodo Commision",required=True)


    @api.onchange('date_start')
    def change_date_start(self):
        for record in self:
            if record.date_start:
                if record.type_period_comission == 'month':
                    month =  record.date_start.month
                    year = record.date_start.year
                    if month < 12 :
                        month += 1
                    else:
                        month = 1
                        year += 1
                    fecha_especifica = date(year, month, 1) - timedelta(days=1)
                    record.date_end = fecha_especifica

    def get_week_range(self,datex):
        """
        Given a date, returns the start (Monday) and end (Sunday) of the week.

        Args:
        date (datetime.date): The date to find the week range for.

        Returns:
        tuple: A tuple containing the start date (Monday) and end date (Sunday) of the week.
        """
        # Get the weekday of the given date (0=Monday, 6=Sunday)
        weekday = datex.weekday()

        # Calculate the start and end dates of the week
        start_date = datex - timedelta(days=weekday)
        end_date = start_date + timedelta(days=6)

        return (start_date, end_date)

    @api.onchange('type_period_comission','date_commission')
    def change_type_period_comission(self):
        for record in self:
            if record.type_period_comission == 'month' and record.date_commission:
                date_now = record.date_commission
                fecha_especifica = date(date_now.year, date_now.month, 1)  # Año, mes, día
                fecha_especifica = fecha_especifica - timedelta(days=1)
                fecha_especifica = date(fecha_especifica.year, fecha_especifica.month, 1)
                record.date_start = fecha_especifica

            if record.type_period_comission == 'week' and record.date_commission:
                date_now = record.date_commission
                fecha_especifica = date_now -  timedelta(weeks=1)
                week_start, week_end = self.get_week_range(fecha_especifica)
                record.date_start = week_start
                record.date_end = week_end

            if record.type_period_comission == 'half' and record.date_commission:
                date_now = record.date_commission
                if date_now.day > 15 :


                    fecha_especifica = date(date_now.year, date_now.month, 1)  # Año, mes, día
                    record.date_start = fecha_especifica

                    fecha_especifica2 = date(date_now.year, date_now.month, 15)
                    record.date_end = fecha_especifica2
                else:

                    fecha_especifica = date(date_now.year, date_now.month, 1)  # Año, mes, día
                    fecha_especifica = fecha_especifica - timedelta(days=1)
                    fecha_especifica = date(fecha_especifica.year, fecha_especifica.month, 15)




                    record.date_start = fecha_especifica

                    month = record.date_start.month
                    year = record.date_start.year
                    if month < 12:
                        month += 1
                    else:
                        month = 1
                        year += 1
                    fecha_especifica2 = date(year, month, 1) - timedelta(days=1)


                    record.date_end = fecha_especifica2





    @api.model
    def default_get(self,fieldsx):
        res = super().default_get(fieldsx)
        date_now = fields.Datetime.now() - timedelta(hours=5)

        #fecha_especifica = date(date_now.year, date_now.month, 1)  # Año, mes, día
        res.update({
            'date_commission': date_now.date()
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

            for team in self.env['crm.team'].search([]):
                for member in team.member_ids:
                    if member == record.user_id:
                        record.team_id = team.id
                        #meta = team.invoiced_target
                        record.type_period_comission = team.type_period_comission
                        #record.percentage_total_base_sale = team.percentage_total_base_sale
                        #record.percentage_overrun_sale = team.percentage_overrun_sale
                        break
            #record.goal = meta


    @api.onchange('line_ids','line_ids.desc','line_ids.amount')
    def calculate_totals(self):
        for record in self:
            total_base = 0
            amount_discount = 0

            for line in record.line_ids:
                total_base += line.amount
                amount_discount +=  line.amount * ( line.desc / 100 )

            record.amount_base = total_base
            record.amount_discount = amount_discount

            len_lines = len(record.line_ids)

            bonus = 0

            if record.team_id.number_sale_additional_commision >= len_lines and   record.user_id in record.team_id.members_additional_commision  :
                bonus = record.team_id.amount_sale_additional_commision

            record.amount_bonus = bonus
            record.amount_total = total_base -  amount_discount + bonus


    @api.onchange('date_start','date_end','user_id')
    def onchange_lines(self):
        for record in self:
            if record.line_ids :
                record.line_ids = False
            #record.line_ids.unlink()
            if record.date_start and record.date_end and record.user_id :
                domain = [
                    #('sale_line_ids','!=',False),
                    ('user_id','=',record.user_id.id),
                    ('date_sign_land','>=',record.date_start),
                    ('date_sign_land', '<=', record.date_end),
                    ('state','not in',['draft','cancel']),
                    #('commision_id.state','!=','done')
                ]
                sales = self.env['sale.order'].search(domain)

                len_sales = len(sales)

                #raise ValueError(sales)

                ids_sales = []


                overrun_sale = 0

                for sale in sales:
                    #if sale.commision_id and sale.commision_id.state == 'done':
                    #    continue

                    if not sale.commision_lan or sale.commision_lan == 0 :
                        sale.change_team_comission()


                    #ids_sales.append(sale.id)
                    record.line_ids += self.env['commission.land.line'].new({
                        'sale_id': sale.id ,
                        'amount': sale.commision_lan ,
                        'desc' : record.team_id.percentage_sale_discount_commision if  len_sales <= record.team_id.number_sale_discount_commision else 0
                    })
                record.calculate_totals()



    def action_cancel(self):
        self.state = 'cancel'


    def action_draft(self):

        self.state = 'draft'

    #def action_done(self):
    #    self.state = 'done'
    def action_confirm(self):
        if self.state == 'draft':
            self.calculate_totals()
            self.state = 'done'

    def update_comission(self):
        if self.state == 'draft':
            self.onchange_user_id()
            self.onchange_lines()

class CommissionRimanLine(models.Model):
    _name        = 'commission.land.line'
    _description = 'commission.land.line'
    commission_land_id = fields.Many2one('commission.land')
    sale_id            = fields.Many2one('sale.order')
    date_sign_land = fields.Date(related='sale_id.date_sign_land')
    date_order = fields.Datetime(related='sale_id.date_order',string="Fecha Pedido")
    date_order_store = fields.Datetime(related='sale_id.date_order', string="Fecha Pedido")
    amount             = fields.Float(string='Monto')
    desc               = fields.Float(string='Descuento')
    subtotal           = fields.Float(compute='get_subtotal',store=True)

    nro_internal_land = fields.Char(related='sale_id.nro_internal_land')
    commision_lan = fields.Float(related='sale_id.commision_lan')
    seller_lan_id = fields.Many2one('seller.land', string="Proveedor Terreno", required=True,
                                     related='sale_id.seller_land_id',store=True)
    user_id   = fields.Many2one('res.users',related='sale_id.user_id',string="Vendedor",store=True)


    @api.depends('desc','amount')
    def get_subtotal(self):
        for record in self:
            total = record.amount or 0
            discount = total * ( (record.desc or 0) / 100 )
            record.subtotal = total - discount




