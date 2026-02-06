# -*- coding: utf-8 -*-

from . import models


def update_res_currency_provider(cr, registry):
    cr.execute(
        """update res_company set currency_provider = 'sbs',currency_interval_unit = 'daily',
           currency_next_execution_date = now() + interval '1 day'""")
    cr.commit()
