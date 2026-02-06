# -*- coding: utf-8 -*-
def _stock_post_init(env):
    env.cr.execute("""UPDATE ir_model_fields_selection 
                   SET name = '{"en_US": "Consignación", "es_PE": "Consignación"}'::jsonb
                   WHERE value='05' and name->> 'es_PE'= 'Envío';""")

from . import models