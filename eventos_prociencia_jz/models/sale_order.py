from jinja2.filters import do_min
from odoo import models, exceptions, fields , api , _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

def jaccard_similarity(text1, text2):
    set1 = set(text1.split())
    set2 = set(text2.split())
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)


similarity_value = 0.8

class SaleOrder(models.Model):
    _inherit = "sale.order"
    place_event_id          = fields.Many2one('place.event',string="Ubicacion")
    date_event              = fields.Datetime(string='Fecha Evento')
    name_event              = fields.Char(string='Evento')

    date_event_install       = fields.Datetime(string='Fecha Instalación')
    date_event_install_end   = fields.Datetime(string='Fecha Fin Instalación')

    date_event_uninstall     = fields.Datetime(string='Fecha Desistalación')
    date_event_uninstall_end = fields.Datetime(string='Fecha Fin Desistalación')

    date_event_sound = fields.Datetime(string='Fecha Prueba Sonido')
    date_event_sound_end = fields.Datetime(string='Fecha Fin Prueba Sonido')

    date_event_uninstall = fields.Datetime(string='Fecha Desistalación')
    date_event_uninstall_end = fields.Datetime(string='Fecha Fin Desistalación')

    crm_lead_id              = fields.Many2one('crm.lead')
    note_event_start         = fields.Text(string="Listado Inicial")
    note_event_end           = fields.Text(string="Listado Final")
    event_line_ids           = fields.One2many('sale.order.items.event','order_id')
    state_event = fields.Selection([
        ('in_progress', 'En Progreso'),
        ('embarked', 'Embarcado'),
        ('collect', 'Recoger'),
        ('done', 'Finalizado'),
        ('cancel', 'Cancelado')
    ], string="Estado del Evento", default='in_progress', copy=False)
    payments_sale_order = fields.One2many('payment.sale.order','sale_id')

    def action_view_delivery(self):
        pickings = self.env['stock.picking'].search([('sale_event_id','=',self.id)])
        return self._get_action_view_picking(self.picking_ids+pickings)

    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        for order in self:
            pickings = self.env['stock.picking'].search([('sale_event_id', '=', order.id)])
            order.delivery_count = len(order.picking_ids)+ len(pickings)

    def get_checklist_url(self):
        return f'/my/checklist/{self.id}'


    @api.onchange('note_event_end')
    def change_note_event_end(self):
        for record in self:
            if not record.note_event_end:
                continue

            record.event_line_ids = False

            lines = record.note_event_end.splitlines()
            for line in lines:
                if not line or line == '':
                    continue

                dx = {'name': line}
                linee = line.strip()

                line_split = linee.split(' ')
                text_product = []

                try:
                    qty = int(line_split[0])
                    dx.update({
                        'quantity': qty
                    })
                    cc = 0
                    for ll in line_split:
                        if cc > 0:
                            text_product.append(ll)
                        cc += 1

                except:
                    dx.update({
                        'display_type': 'line_section'
                    })

                record.event_line_ids += self.env['sale.order.items.event'].new(dx)

                record.event_line_ids.change_namex()



    def change_note_event_endx(self):
        products = self.env['product.product'].search([])
        for record in self:


            if not record.note_event_end:
                continue

            if record.event_line_ids:
                record.event_line_ids = False



            #record.event_line_ids.unlink()

            lines = record.note_event_end.splitlines()
            for line in lines:
                if not line or line == '':
                    continue

                dx  = {'name': line}
                linee = line.strip()

                line_split = linee.split(' ')
                text_product = []


                try:
                    qty = int(line_split[0])
                    dx.update({
                        'quantity': qty
                    })
                    cc = 0
                    for ll in line_split:
                        if cc > 0:
                            text_product.append(ll)
                        cc += 1

                except:
                    dx.update({
                        'display_type': 'line_section'
                    })

                if text_product:
                    productt = None
                    text_product = " ".join(text_product)

                    similarity_master = 0

                    if products:
                        for product in products:
                            similarity = jaccard_similarity(product.name.lower(), text_product.lower())
                            if similarity > similarity_master and similarity >= similarity_value:
                                productt = product.id
                    dx.update({
                        'product_id': productt
                    })



                record.event_line_ids += self.env['sale.order.items.event'].new(dx)


    @api.onchange('date_event')
    def change_date_event(self):
        for record in self:
            record.date_event_install = record.date_event

    @api.onchange('date_event_install')
    def change_date_event_install(self):
        for record in self:
            if record.date_event_install:
                record.date_event_install_end = record.date_event_install + timedelta(hours=1)
            else:
                record.date_event_install_end = False


    @api.onchange('date_event_install_end')
    def change_date_event_install_end(self):
        for record in self:
            record.date_event_uninstall = record.date_event_install_end

    @api.onchange('date_event_uninstall')
    def change_date_event_uninstall(self):
        for record in self:
            if record.date_event_uninstall:
                record.date_event_uninstall_end = record.date_event_uninstall + timedelta(hours=1)
            else:
                record.date_event_uninstall_end = None



    @api.model
    def create(self,vals):
        res = super().create(vals)
        #for record in res:
        #    raise ValueError(record.crm_lead_id.message_attachment_count)

        return res

    @api.onchange('company_id')
    def _onchange_company_id_warning(self):
        self.show_update_pricelist = True
        if self.order_line and self.state == 'draft' and self.id:
            return {
                'warning': {
                    'title': _("Warning for the change of your quotation's company"),
                    'message': _("Changing the company of an existing quotation might need some "
                                 "manual adjustments in the details of the lines. You might "
                                 "consider updating the prices."),
                }
            }


    #def action_confirm(self):
    #    res = super().action_confirm()
    #    return res


    def action_confirm_event(self):
        for record in self:

            if not record.date_event_install :
                raise UserError('INDIQUE FECHA DE INSTALACION')

            if not record.date_event_install_end :
                raise UserError('INDIQUE FECHA DE FIN INSTALACION')

            if not record.date_event_uninstall:
                raise UserError('INDIQUE FECHA DE DESINSTALACION')

            if not record.date_event_uninstall_end:
                raise UserError('INDIQUE FECHA DE FIN DESINSTALACION')

            if not record.event_line_ids:
                raise UserError('NO SE INDICO LINEAS DE CHECK LIST')


            lines_picking = []

            for line in record.event_line_ids:

                if not line.display_type:
                    '''
                    dx = {
                        'name': line.name,
                        # 'resource_id': resource.id,
                        # 'role_id': role1.id,
                        'start_datetime': record.date_event_install,
                        'end_datetime': record.date_event_uninstall_end,
                        # 'sale_line_id': line.id
                    }
                    self.env['planning.slot'].create(dx)
                    '''
                    if line.product_id:
                        lines_picking.append(line)



            partner_ids = []
            users = self.env['res.users'].search([])

            for user in users:
                partner_ids.append(user.partner_id.id)

            if partner_ids:
                wizard = self.env['mail.wizard.invite'].create({
                    'res_id': self.id,
                    'res_model': self._name,
                    'partner_ids': [(6, 0, partner_ids)]
                })
                wizard.add_followers()

            #generar picking

            picking_type_id = self.env['stock.picking.type'].search([('is_fictic_warehouse','=',True)])



            if lines_picking:
                dx = {
                    'partner_id': self.partner_id.id ,
                    'origin': self.name ,
                    'picking_type_id': picking_type_id.id ,
                    'sale_event_id': self.id ,
                }

                picking = self.env['stock.picking'].create(dx)

                for ll in lines_picking:
                    picking.move_ids_without_package += self.env['stock.move'].new({
                        'product_id': ll.product_id.id,
                        'product_uom_qty': ll.quantity ,
                        'location_id': picking.location_id.id ,
                        'location_dest_id': picking.location_dest_id.id ,
                        'name': ll.product_id.name ,
                    })


class SaleOrderItemsEvent(models.Model):
    _name = "sale.order.items.event"
    _description = "sale.order.items.event"
    order_id     = fields.Many2one('sale.order')
    name_event = fields.Char(string='Evento',related='order_id.name_event')
    date_event_install = fields.Datetime(string='Fecha Instalación',related='order_id.date_event_install')
    date_event_uninstall_end = fields.Datetime(string='Fecha Fin Desistalación',related='order_id.date_event_uninstall_end')

    name          = fields.Char()
    product_id    = fields.Many2one('product.product',string="Producto")
    qty_available = fields.Float(compute='get_qty_available',string="Disponible")
    quantity      = fields.Float(string="Cantidad")
    margin_stock_danger = fields.Integer(string="Margen Stock Rojo",related='product_id.margin_stock_danger')
    margin_stock_warning = fields.Integer(string="Margen Stock Amarillo",related='product_id.margin_stock_warning')
    check1        = fields.Boolean(string="Embarque")
    user1         = fields.Many2one('res.users', string="Usuario Embarque")
    check2 = fields.Boolean(string="Recojo")
    user2 = fields.Many2one('res.users', string="Usuario Recojo")
    check3 = fields.Boolean(string="Recepcion")
    user3 = fields.Many2one('res.users', string="Usuario Recepcion")

    check = fields.Boolean(compute="get_check")
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False)
    sequence = fields.Integer(string="Sequence", default=10)
    is_external = fields.Boolean(string="Es Externo")

    def get_lines_dates(self):
        if not self.product_id:
            return

        record = self

        items_sale = self.env['sale.order.items.event'].search([
            ('product_id', '=', record.product_id.id),
            ('order_id.state', '!=', 'cancel'),

            ('order_id.date_event_uninstall_end', '>', record.order_id.date_event_install),
            # ('order_id.date_event_install', '>=', record.order_id.date_event_install),
            # ('order_id.date_event_uninstall_end', '<=', record.order_id.date_event_uninstall_end),
        ])

        items_sale2 = self.env['sale.order.items.event'].search([
            ('product_id', '=', record.product_id.id),
            ('order_id.state', '!=', 'cancel'),

            ('order_id.date_event_install', '>', record.date_event_uninstall_end),

            # '|',
            # ('order_id.date_event_uninstall_end', '<=', record.order_id.date_event_install),
            # ('order_id.date_event_install', '>=', record.date_event_uninstall_end)
            # ('order_id.date_event_install', '>=', record.order_id.date_event_install),
            # ('order_id.date_event_uninstall_end', '<=', record.order_id.date_event_uninstall_end),
        ])

        #view = self.env.ref('land.edit_account_move_line')
        domain = [
                    ('product_id', '=', self.product_id.id),
                    ('order_id.state', '!=', 'cancel'),
                    #('id', '!=', self.id),
                    #('order_id.date_event_install', '>=', self.order_id.date_event_install),
                    #('order_id.date_event_uninstall_end', '<=', self.order_id.date_event_uninstall_end),
                    '|',
                    ('order_id.date_event_uninstall_end', '<=', self.order_id.date_event_install),
                    ('order_id.date_event_install', '>=', self.date_event_uninstall_end)
                ]

        domain = [('id','in',items_sale2.ids+items_sale.ids)]
        return {
            "name": f"Disponibilidad {self.product_id.name}",
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "res_model": "sale.order.items.event",
            "target": "new",
            "domain": domain
            #"res_id": self.id,
            #"view_id": view.id
        }

    def get_qty_available(self):
        for record in self:
            record.qty_available = 0

            qty_available = 0
            qty_sales = 0
            if record.product_id:
                if not record.id :
                    continue
                qty_available = record.product_id.qty_available
                id_line = record.id

                items_sale = self.env['sale.order.items.event'].search([
                    ('product_id', '=', record.product_id.id),
                    ('order_id.state', '!=', 'cancel'),
                    ('id', '!=', id_line),
                    ('order_id.date_event_uninstall_end', '>', record.order_id.date_event_install),
                    #('order_id.date_event_install', '>=', record.order_id.date_event_install),
                    #('order_id.date_event_uninstall_end', '<=', record.order_id.date_event_uninstall_end),
                ])

                items_sale2 = self.env['sale.order.items.event'].search([
                    ('product_id', '=', record.product_id.id),
                    ('order_id.state', '!=', 'cancel'),
                    ('id', '!=', id_line),
                    ('order_id.date_event_install', '>', record.date_event_uninstall_end),

                    #'|',
                    #('order_id.date_event_uninstall_end', '<=', record.order_id.date_event_install),
                    #('order_id.date_event_install', '>=', record.date_event_uninstall_end)
                    #('order_id.date_event_install', '>=', record.order_id.date_event_install),
                    #('order_id.date_event_uninstall_end', '<=', record.order_id.date_event_uninstall_end),
                ])



                items_sales = []

                for line in items_sale + items_sale2:
                    if line not in items_sales:
                        items_sales.append(line)



                if items_sales:
                    for itemx in items_sale:
                        qty_sales += itemx.quantity


            record.qty_available = qty_available - qty_sales



    @api.onchange('name')
    def change_namex(self):


        #products = self.env['product.product'].search([])

        self.env.cr.execute('''
        SELECT PP.id , PT.name
        FROM product_product PP   
        JOIN product_template PT  ON PP.product_tmpl_id = PT.id
         ''')
        products = self.env.cr.fetchall()

        for lineee in self:

            dx = {}

            if not lineee.name:
                continue

            linee = lineee.name.strip()

            line_split = linee.split(' ')

            text_product = []





            try:
                qty = int(line_split[0])

                dx.update({
                    'quantity': qty
                })
                cc = 0
                for ll in line_split:
                    if cc > 0 :
                        text_product.append(ll)
                    cc += 1

            except:
                if not  lineee :
                    dx.update({
                        'display_type': 'line_section'
                    })





            if text_product:
                productt = None
                text_product = " ".join(text_product)


                similarity_store = 0


                for product in products:
                    similarity1 = jaccard_similarity(product[1]['en_US'].lower(), text_product.lower())
                    similarity2 = jaccard_similarity(product[1]['es_PE'].lower(), text_product.lower())
                    similarity = max(similarity1,similarity2)




                    if similarity >= similarity_value :
                        productt = product[0]
                        lineee.product_id = productt
                        similarity_store = similarity

                    #if product[0] == 18 :
                    #    raise ValueError([productt,similarity,product])



            if dx:
                #raise ValueError(dx)
                lineee.write(dx)


    def get_check(self):


        for record in self:
            check = False
            if record.order_id.state_event == 'in_progress':
                check = bool(record.check1)
            if record.order_id.state_event == 'embarked':
                check = bool(record.check2)
            if record.order_id.state_event in ['collect','done']:
                check = bool(record.check3)

            if   record.display_type :
                check = True
            record.check = check
