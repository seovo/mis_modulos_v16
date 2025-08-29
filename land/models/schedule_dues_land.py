from odoo import api, fields, models , _
from odoo.exceptions import ValidationError

class ScheduleDuesLand(models.Model):
    _name          = 'schedule.dues.land'
    _description   = 'schedule.dues.land'
    number_due     = fields.Integer(string="Cuota")
    date           = fields.Date(string="Fecha Prevista")
    balan          = fields.Float(string="Balance")
    amount         = fields.Float(string="Mensualidad")
    #note           = fields.Text(string="Nota")
    is_paid        = fields.Boolean(string="Pagado?")
    order_id       = fields.Many2one('sale.order',string='Venta')
    line_move_id = fields.Many2one('account.move.line', string="Factura")
    id_line_move_id = fields.Integer()
    move_id        = fields.Many2one('account.move',related='line_move_id.move_id',string="Factura")
    invoice_date   = fields.Date(related='move_id.invoice_date',string="Fecha Pagada",store=True)
    currency_id    = fields.Many2one('res.currency',related='move_id.currency_id')
    amount_due_land = fields.Float(related='line_move_id.price_unit',string="Monto Pagado")
    amount_mora_land = fields.Float(related='move_id.amount_mora_land',string="Mora")
    nro_internal_land =  fields.Char(string="Expediente",related='order_id.nro_internal_land',store=True)

    name = fields.Char(compute="get_name_jz",store=True)
    order_identificador = fields.Char(compute="get_name_jz",store=True,string="Expediente - Venta")
    description = fields.Char(compute="get_name_jz",string="Descripción")

    # 0 -> Inicial , 1 --> Cuota , 3 --> Adelantos ,  3 --> Independizacion
    type_number_schedule = fields.Integer(string="Tipo de Schedule")

    @api.depends('move_id','nro_internal_land','order_id','line_move_id','type_number_schedule')
    def get_name_jz(self):
        for record in self:
            n = f'''  {record.move_id.display_name }  {record.nro_internal_land}  {record.order_id.display_name}'''
            n += f''' {record.line_move_id.display_name} {record.number_due}  '''
            record.name = n

            description = '*'
            if record.type_number_schedule  == 0:
                description = 'INICIAL'

            if record.type_number_schedule  == 1:
                description = f'CUOTA #{record.number_due}'

            if record.type_number_schedule  == 2:
                description = f'ADELANTO CUOTA #{record.number_due}'

            record.description = description

            record.order_identificador = f" {record.order_id.nro_internal_land}  - {record.order_id.name}"





    _order = 'number_due asc ,  invoice_date asc '

    def invoice_here_land(self):
        pass

    def update_all_cronogramas(self):
        #select * FROM schedule_dues_land ;

        ventas = self.env['sale.order'].search([
            #('nro_internal_land','!=',False),
            #('stage_land','!=','cancel'),
            #('stage_land','!=',False),
            ('schedule_land_ids','=',False),
            ('invoice_ids','!=',False)
        ],limit=50)

        #raise ValidationError(str(ventas))


        ventas.update_schedule()









