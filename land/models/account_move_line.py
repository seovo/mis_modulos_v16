from odoo import api, fields, models , _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class AccountMoveLine(models.Model):
    _inherit   = 'account.move.line'
    partner_commision_id = fields.Many2one('res.partner',string='Comissión')
    number_advance_land = fields.Integer(string='N° Cuota Adelanto')
    order_advance_land = fields.Many2one('sale.order',string='Venta Adelanto')
    sale_available_ids = fields.Many2many('sale.order',compute='get_sale_available_ids')

    @api.depends('move_id')
    def get_sale_available_ids(self):
        for record in self:
            sale_available_ids = []
            for line in record.move_id.invoice_line_ids:
                if line.sale_line_ids:
                    for lin in line.sale_line_ids:
                        if lin.order_id:
                            sale_available_ids.append(lin.order_id.id)

            record.sale_available_ids = sale_available_ids if sale_available_ids else  False


    @api.model
    def create(self,vals):
        #raise ValueError(vals)
        res = super(AccountMoveLine, self).create(vals)

        for re in res:
            if re.order_advance_land:
                if re.number_advance_land <= 0:
                    raise  ValidationError('NUMERO DE ADELANTO INCORRECTO')

                if re.price_unit <= 0:
                    raise  ValidationError('PRECIO INCORRECTO')

        return res

    #@api.model_create_multi
    #def create(self, vals_list):
    #    raise ValueError(vals_list)
    #    res = super(AccountMove, self).create(vals_list)
    #    return res

    def unlink(self):

        sales = []

        for record in self:
            if record.sale_line_ids:
                sales.append(record.sale_line_ids[0].order_id)

        res = super().unlink()
        for sale in sales:
            sale.update_schedule()
        return res


    def write(self,vals):
        #raise ValueError(vals)
        res = super().write(vals)

        if 'price_unit' in vals:
            if self.move_id.state != 'draft':
                return res
                raise ValueError('Modificacion no permitida')

        return res

    def edit_desc_jz(self):
        view = self.env.ref('land.edit_account_move_line')
        return {
            "name": f"EDIT DESCRIPCION:   {self.name}",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "account.move.line",
            "target": "new",
            "res_id": self.id ,
            "view_id": view.id
        }

    def next_due_land(self):
        for record in self:
            if record.move_id.state == 'draft':
                new_line = record.copy()


                if record.sale_line_ids:
                    record.sale_line_ids[0].order_id.update_schedule()

                    new_line.name = record.sale_line_ids.get_descript_next_due(record.sale_line_ids)
                    new_line.sale_line_ids = [(6, 0, record.sale_line_ids.ids)]



    @api.onchange('product_id')
    def change_product_autocomplete_description_jz(self):


        for record in self:
            continue
            if record.move_id.is_separation_land and record.product_id :
                raise ValueError('DESACTIVADO')
                if record.move_id.mz_land_separation_id and record.move_id.lot_land_separation_id and  record.move_id.sector_land_separation_id:
                    name = record.name or ''
                    name += f''' MZ. : {record.move_id.mz_land_separation_id.name} , LOTE: {record.move_id.lot_land_separation_id.name} , ETAPA: {record.move_id.sector_land_separation_id.name} '''
                    record.name = name
