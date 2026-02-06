# -*- coding: utf-8 -*-

from odoo import fields, models

ONE = '1'
EIGTH = '8'
NINE = '9'
STATE_SUNAT_SELECTION = [(ONE, '1'), (EIGTH, '8'), (NINE, '9')]

TYPE_A = 'A'
TYPE_M = 'M'
TYPE_C = 'C'
TYPE_SUNAT_SELECTION =[(TYPE_A, 'Apertura del Ejercicio'), (TYPE_M, 'Movimiento del mes'), (TYPE_C, 'Cierre del Ejercicio')]

BALANCE = 'balance'
LOSS_GAIN = 'loss_gain'
TYPE_PLAN_SELECTION = [(BALANCE, 'Cuentas del Balance General'), (LOSS_GAIN, 'Cuentas de ganancia y pérdidas')]


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_pe_operation_state_sunat = fields.Selection(selection=STATE_SUNAT_SELECTION, string='Estado de Operación SUNAT', default=ONE)
    l10n_pe_operation_type_sunat = fields.Selection(selection=TYPE_SUNAT_SELECTION, string='Tipo de Operación SUNAT', default=TYPE_M)
    no_domiciled = fields.Boolean(string='No domiciliado')

    l10n_pe_fiscal_credit_doc_serie = fields.Char(
        ("Documento fiscal Serie"), copy=False
    )
    l10n_pe_fiscal_credit_doc_number = fields.Char(
        ("Documento fiscal Numero"), copy=False
    )
    l10n_pe_dua_year = fields.Integer(("Año de la Dua"),
                                      help=('Year of issue of the DUA or DSI that supports the tax credit'))

    # retention_mark_16 = fields.Char("Retention Mark",
    #                                 help="Marca del comprobante de pago sujeto a retención",
    #                                 default='')

    l10n_pe_tax_agreement = fields.Many2one('catalog.element',
                                            domain="[('table_id.code', 'ilike', 'PE.SUNAT.PLE_TABLE25')]",
                                            ondelete='restrict')

    l10n_pe_income_type = fields.Many2one('catalog.element',
                                          domain="[('table_id.code', 'ilike', 'PE.SUNAT.PLE_TABLE31')]",
                                          ondelete='restrict')



    def _get_fiscal_credit_doc_type(self):
        catele_model = self.env['catalog.element']
        table_list = []
        for e in catele_model._get_datasource('PE.SUNAT.PLE_TABLE10'):
            if e.active and e.name in ['00', '46', '50', '51', '53']:
                description = "%s - %s" % (e.name, e.description)
                table_list.append((e.name, description))
        return table_list

# class AccountAccountType(models.Model):
#     _inherit = 'account.account.type'
#
#     l10n_pe_type_plan = fields.Selection(selection=TYPE_PLAN_SELECTION, string='Tipo según Plan Contable', default=BALANCE)