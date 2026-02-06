# -*- coding: utf-8 -*-

from odoo.exceptions import ValidationError
from odoo import models, fields, api
from odoo.tools.translate import _

CHOICE_TYPE = [('view', _('View')), ('normal', _('Normal'))]


# TODO: requiere añadir features Multicompany
# TODO: MEJORA FASE2 incluir un template de catalog. Mientras no se tenga, se hace a mano
class CatalogElement(models.Model):
    # Private attributes
    _name = "catalog.element"
    _description = "Elements in table of tables"

    # Default methods

    # compute and search fields, in the same order of fields declaration

    # Fields declaration
    table_id = fields.Many2one('catalog.table', string=_('Catalog Table'), index=True)
    name = fields.Char(string=_('Element Name'), size=64, index=True, required=True)
    description = fields.Text(string=_('Element Description'))
    percent = fields.Float()
    from_date = fields.Date(_('Effective Date From'))
    to_date = fields.Date(_('Effective Date To'))
    active = fields.Boolean(default=True)
    doc_serie_lenght = fields.Integer(string=_("serial number"), required=True)
    doc_number_lenght = fields.Integer(string=_("voucher number"), required=True)
    doc_serie_lenght_fixed = fields.Boolean(default=False)
    doc_number_lenght_fixed = fields.Boolean(default=False)
    company_id = fields.Many2one('res.company', _('Company'), index=True, related='table_id.company_id', store=True)

    # compute and search fields, in the same order of fields declaration

    # Constraints and onchanges
    _sql_constraints = [('table_name_unique', 'unique(id,table_id,name)',
                         _('The element code must be unique for this table!'))]

    # CRUD methods (and name_get, name_search, ...) overrides
    @api.depends('name', 'description')
    def name_get(self):
        names = []
        for fld in self:
            names.append((fld.id, fld.name + ' - ' + fld.description))
        return names

    def _get_datasource(self, catalog_table, name_or_code=None):
        domain = [('table_id.code', 'ilike', catalog_table)]
        if name_or_code:
            domain.append(('name', '=', name_or_code))
        return self.search(domain)


class CatalogTable(models.Model):
    # Private attributes
    _name = "catalog.table"
    _description = "Catalog Table of Tables"
    _order = "code"

    # Default methods

    # compute and search fields, in the same order of fields declaration

    # Fields declaration
    company_id = fields.Many2one('res.company', string=_('Company'), index=True)
    country_id = fields.Many2one('res.country', string=_('Country'), index=True)
    code = fields.Char(size=32, required=True, index=True)
    name = fields.Char(size=2048, translate=True, index=True)
    complete_name = fields.Char(compute='_compute_name')
    description = fields.Text(_('Table Description'))
    parent_id = fields.Many2one('catalog.table',
                                string=_('Parent Table'),
                                index=True,
                                domain=[('type', '=', 'view')])
    child_ids = fields.One2many('catalog.table', inverse_name='parent_id', string=_('Child Tables'))
    type = fields.Selection(CHOICE_TYPE, default='normal', string=_('Table Type'))
    active = fields.Boolean(default=True)
    element_ids = fields.One2many('catalog.element', inverse_name='table_id', string=_('Elements'))
    number = fields.Char(string="Numero", compute='_compute_number')

    # compute and search fields, in the same order of fields declaration
    def _compute_name(self):
        res = self.name_get()
        return dict(res)

    def _compute_number(self):
        for line in self:
            # line.number =
            line.number = line[0].description.split(sep=':')[0]