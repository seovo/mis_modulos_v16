# -*- coding: utf-8 -*-

from datetime import datetime
from pytz import timezone
from datetime import datetime, timedelta
from odoo import fields, models, api, _
from dateutil.relativedelta import relativedelta

SBS_DATE_FORMAT = '%d/%m/%Y'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # from_update = fields.Date(
    #     string=_("Update Since"),
    #     default=lambda self: datetime.strptime("01/01/{}".format(datetime.now().year), "%d/%m/%Y")
    # )

    # def sbs_update_currency_rates_manual(self):
    #     # companies = self.env['res.company'].browse([record.company_id.id for record in self])
    #     self.ensure_one()
    #     if self.currency_next_execution_date:
    #         self.company_id.sbs_update_currency_rates(self.currency_next_execution_date.strftime(SBS_DATE_FORMAT))
    #     else:
    #         aux = datetime.now(timezone('America/Lima')).strftime(SBS_DATE_FORMAT)
    #         self.company_id.sbs_update_currency_rates(aux)
    #     return True

    def update_currency_rates_manually(self):
        if self.company_id.currency_next_execution_date < datetime.now(timezone('America/Lima')).date():
            self.company_id.update_currency_rates_range(self.company_id.currency_next_execution_date, datetime.now(timezone('America/Lima')).date())
            self.company_id.currency_next_execution_date = datetime.now(timezone('America/Lima')).date()
        super(ResConfigSettings, self).update_currency_rates_manually()


