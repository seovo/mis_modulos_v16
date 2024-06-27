from odoo import api, fields, models , _
from datetime import datetime, timedelta
class AccountMoveLine(models.Model):
    _inherit   = 'account.move.line'

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
            if record.move_id.is_separation_land and record.product_id :
                if record.move_id.mz_land_separation and record.move_id.lot_land_separation and  record.move_id.sector_land_separation:
                    name = record.name or ''
                    name += f''' MZ : {record.move_id.mz_land_separation} , LOTE: {record.move_id.lot_land_separation} , ETAPA: {record.move_id.sector_land_separation} '''
                    record.name = name
