# -*- coding:utf-8 -*-

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    vacation_scheme = fields.Selection(string="Esquema Vacacional", selection=[('15', '15 días'),
                                                                               ('30', '30 días')])
    rmv = fields.Float(string="RMV", related='company_id.rmv')
    uit = fields.Float(string="UIT", related='company_id.uit')
    insurance_stop = fields.Float(string="MONTO DEL TOPE DE AFP SEGURO", related='company_id.insurance_stop')
    mov = fields.Boolean('Movilidad', default=True)
    mov_libre = fields.Float(string="Mov libre")
    mov_sup = fields.Float(string="Mov sup.")
    bond_rotating_schedule = fields.Float(string="Bono horario rotativo")
    bond_forklift = fields.Float(string="Bono montacarga")
    bond_store = fields.Float(string="Bono almacén")
    bond_extra = fields.Float(string="Bono extra")

    expenses = fields.Float(string="Viaticos Sup.")
    commissions = fields.Float(string="Comisiones")
    feeding = fields.Float(string="Alimentación Sup.")


