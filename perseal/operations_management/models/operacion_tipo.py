# -*- coding: utf-8 -*-

from odoo import fields, models, api


class OperacionTipo(models.Model):
    _name = 'operacion.tipo'
    _inherit = 'mail.thread'
    _description = 'Tipo de operación'

    name = fields.Char(string='Nombre')
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario',
    )
    cuenta_ingreso_id = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta de ingreso',
    )
    cuenta_gasto_fdg_id = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta de gasto FDG',
    )
    cuenta_gasto_interes_id = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta de gasto intereses',
    )
    cuenta_gasto_desembolso_id = fields.Many2one(
        comodel_name='account.account',
        string='Cuenta de gasto desembolso',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
    )
    distribucion_ids = fields.One2many(
        comodel_name='operacion.tipo.distribucion',
        inverse_name='operacion_tipo_id',
        string='Distribución',
    )
    
    def get_account(self, type):
        line = self.distribucion_ids.filtered(lambda l: l.concepto == type)
        if line:
            if line.debito_id:
                account_id = line.debito_id.id
            elif line.credito_id:
                account_id = line.credito_id.id
            else:
                account_id = False
        return account_id


class OperacionTipoDistribucion(models.Model):
    _name = 'operacion.tipo.distribucion'
    _inherit = 'mail.thread'
    _description = 'Distribución del tipo de operación'

    operacion_tipo_id = fields.Many2one(
        comodel_name='operacion.tipo',
        string='Tipo de operación',
    )
    porcentaje = fields.Float(
        string='%',
    )
    concepto = fields.Selection(selection=[
        ('ingreso', 'Cuenta de ingreso'),
        ('fdg', 'Cuenta de gasto FDG'),
        ('interes', 'Cuenta de gasto intereses'),
        ('desembolso', 'Cuenta de gasto desembolso'),
    ], string='Concepto')
    debito_id = fields.Many2one(
        comodel_name='account.account',
        string='Débito',
    )
    credito_id = fields.Many2one(
        comodel_name='account.account',
        string='Crédito',
    )
    etiqueta = fields.Char(
        string='Etiqueta',
    )
    
    @api.onchange("credito_id")
    def onchange_credit(self):
        self.debito_id = False
        
    @api.onchange("debito_id")
    def onchange_debit(self):
        self.credito_id = False
