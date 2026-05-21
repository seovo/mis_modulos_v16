from odoo import api, fields, models

state_sales = [
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Sales Done'),
        ('cancel', 'Cancelled'),
    ]


class SaleReport(models.Model):
    _name = "sale.report.sensotek"
    _description = "Sales Analysis Report"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    sale_line_id = fields.Many2one('sale.order.line', readonly=True, string="Linea de Venta")
    name               = fields.Char('Order Reference', readonly=True)
    date               = fields.Datetime('Order Date', readonly=True)
    user_id            = fields.Many2one('res.users', 'Vendedor', readonly=True)
    partner_id         = fields.Many2one('res.partner', 'Cliente', readonly=True)
    order_id           = fields.Many2one('sale.order', 'Order #', readonly=True)
    client_order_ref   = fields.Char(related='order_id.client_order_ref', string="Referencia cliente")
    state              = fields.Selection(state_sales, string='Status', readonly=True)
    product_id         = fields.Many2one('product.product', 'Producto', readonly=True)
    customer_lead      = fields.Float(string='Plazo de entrega', readonly=True)
    product_uom_qty    = fields.Float('Cantidad Ordenada', readonly=True)
    qty_delivered      = fields.Float('Cantidad Entregada', readonly=True)
    qty_to_invoice     = fields.Float('Cantidad a Facturar', readonly=True)
    qty_invoiced       = fields.Float('Cantidad Facturada', readonly=True)
    qty_to_deliver     = fields.Float('Cant. Por Entregar')
    free_qty_today     = fields.Float('Cant. Libre Hoy', related='sale_line_id.free_qty_today')
    create_date        = fields.Datetime(string='Creado El', readonly=True)
    purchase_id        = fields.Many2one('purchase.order',related='sale_line_id.purchase_id',string="Compra")
    purchase_create_date     = fields.Datetime(related='sale_line_id.purchase_create_date',string="Fecha Creada Compra")
    purchase_date_order      = fields.Datetime(related='sale_line_id.purchase_date_order', string="Fecha Compra")
    purchase_create_uid      = fields.Many2one('res.users', related='sale_line_id.purchase_create_uid', string="Compra creado por")
    purchase_product_qty     = fields.Float(related='sale_line_id.purchase_create_uid', string="Compra Cantidad")
    purchase_price_unit      = fields.Float(related='sale_line_id.purchase_price_unit', string="Compra P. Unit")
    purchase_qty_received    = fields.Float(related='sale_line_id.purchase_qty_received', string="Compra Cant Recibida")
    purchase_product_uom_qty = fields.Float(related='sale_line_id.purchase_product_uom_qty', string="Compra Cant Total")
    purchase_date_planned    = fields.Datetime(related='sale_line_id.purchase_date_planned', string="Fecha Prevista")
    purchase_partner_id      = fields.Many2one('res.partner', related='sale_line_id.purchase_partner_id', string="Proveedor")
    purchase_currency_id     = fields.Many2one('res.currency', related='sale_line_id.purchase_currency_id', string="Compra Moneda")
    purchase_paqueteria      = fields.Char(string="Paqueteria", related='sale_line_id.purchase_paqueteria')
    purchase_guia_envio      = fields.Char(string="Guia de Envio",related='sale_line_id.purchase_guia_envio')
    company_id               = fields.Many2one('res.company', 'Compañia', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        '''
        t.uom_id as product_uom,
        sum(l.price_total / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) as price_total,
        sum(l.price_subtotal / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) as price_subtotal,
        sum(l.untaxed_amount_to_invoice / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) as untaxed_amount_to_invoice,
        sum(l.untaxed_amount_invoiced / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) as untaxed_amount_invoiced,
        count(*) as nbr, 
        s.campaign_id as campaign_id,
        s.medium_id as medium_id,
        s.source_id as source_id,
        extract(epoch from avg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
        t.categ_id as categ_id,
        s.pricelist_id as pricelist_id,
        s.analytic_account_id as analytic_account_id,
        s.team_id as team_id,
        p.product_tmpl_id,
        
        partner.country_id as country_id,
        partner.industry_id as industry_id,
        partner.commercial_partner_id as commercial_partner_id,
        sum(p.weight * l.product_uom_qty / u.factor * u2.factor) as weight,
        sum(p.volume * l.product_uom_qty / u.factor * u2.factor) as volume,
        l.discount as discount,
        sum((l.price_unit * l.product_uom_qty * l.discount / 100.0 / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END)) as discount_amount,
        
        '''

        select_ = """
            min(l.id) as id,
            min(l.id) as sale_line_id,
            s.name as name,
            s.date_order as date,
            s.user_id as user_id,
            s.partner_id as partner_id,
            s.id as order_id,
            s.state as state,
            l.product_id as product_id,
            l.customer_lead as customer_lead,
            sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
            sum(l.qty_delivered / u.factor * u2.factor) as qty_delivered,
            sum(l.qty_to_invoice / u.factor * u2.factor) as qty_to_invoice,
            sum(l.qty_invoiced / u.factor * u2.factor) as qty_invoiced,
            l.qty_to_deliver_store as qty_to_deliver,
            l.create_date as  create_date ,
            s.company_id as company_id
        """

        for field in fields.values():
            select_ += field

        from_ = """
                sale_order_line l
                      join sale_order s on (l.order_id=s.id)
                      join res_partner partner on s.partner_id = partner.id
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join uom_uom u on (u.id=l.product_uom)
                    left join uom_uom u2 on (u2.id=t.uom_id)
                    left join product_pricelist pp on (s.pricelist_id = pp.id)
                %s
        """ % from_clause

        '''
        t.categ_id,
        s.campaign_id,
        s.medium_id,
        s.source_id ,
        s.pricelist_id,
        s.analytic_account_id,
        s.team_id,
        partner.country_id,
        partner.industry_id,
        partner.commercial_partner_id,
        l.discount,
        '''

        groupby_ = """
            s.name,
            s.date_order,
            s.user_id,
            s.partner_id,
            s.id,
            s.state,
            l.product_id,
            l.customer_lead,
            l.qty_to_deliver_store ,
            l.create_date ,
            s.company_id,
            l.order_id,
            t.uom_id,
            p.product_tmpl_id %s
        """ % (groupby)

        return '%s (SELECT %s FROM %s WHERE l.product_id IS NOT NULL GROUP BY %s)' % (with_, select_, from_, groupby_)

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))


