from odoo import api, fields, models , _
from datetime import datetime, timedelta
class AccountMoveLine(models.Model):
    _inherit   = 'account.move.line'

    @api.onchange('product_id')
    def change_product_autocomplete_description_jz(self):
        for record in self:
            if record.move_id.is_separation_land and record.product_id :
                if record.move_id.mz_land_separation and record.move_id.lot_land_separation and  record.move_id.sector_land_separation:
                    name = record.name or ''
                    name += f''' MZ : {record.move_id.mz_land_separation} , LOTE: {record.move_id.lot_land_separation} , ETAPA: {record.move_id.sector_land_separation} '''
                    record.name = name
