from odoo.exceptions import ValidationError

import psycopg2
from psycopg2 import sql
from odoo import api, fields, models , _


class PricelistMigratioJz(models.Model):
    _name  = 'pricelist.migration.jz'
    name = fields.Char(required=True)
    id_sql = fields.Integer(required=True)
    migrate_id = fields.Many2one('migrate.jz',required=True)
    pricelist_id = fields.Many2one('product.pricelist')

class JournalMigrationJz(models.Model):
    _name  = 'journal.migration.jz'
    name = fields.Char(required=True)
    id_sql = fields.Integer(required=True)
    migrate_id = fields.Many2one('migrate.jz',required=True)
    journal_id = fields.Many2one('account.journal')

class CurrencyMigrationJz(models.Model):
    _name  = 'currency.migration.jz'
    name = fields.Char(required=True)
    id_sql = fields.Integer(required=True)
    migrate_id = fields.Many2one('migrate.jz',required=True)
    currency_id = fields.Many2one('res.currency')

class AcountAcountMigrationJz(models.Model):
    _name  = 'account.migration.jz'
    name = fields.Char(required=True)
    id_sql = fields.Integer(required=True)
    code = fields.Char(required=True)
    migrate_id = fields.Many2one('migrate.jz',required=True)
    account_id = fields.Many2one('account.account')

class TaxGroupMigrationJz(models.Model):
    _name  = 'tax.group.migration.jz'
    #_order = 'type , id_sql'
    name = fields.Char(required=True)
    id_sql = fields.Integer(required=True)
    migrate_id = fields.Many2one('migrate.jz', required=True)
    tax_group_id = fields.Many2one('account.tax.group', domain=[('tax_group_migration_jz_ids', '=', False)])


class TaxMigrationJz(models.Model):
    _name  = 'tax.migration.jz'
    _order = 'type , id_sql'

    name = fields.Char(required=True)
    id_sql = fields.Integer(required=True)
    migrate_id = fields.Many2one('migrate.jz',required=True)
    tax_id = fields.Many2one('account.tax',domain=[('tax_migration_jz_ids','=',False)])
    type   = fields.Selection([
        ('sale','Ventas'),('purchase','Compras'),('none','Ninguno')
    ])
    amount = fields.Float()
    label_tax = fields.Char(related='tax_id.invoice_label')
    description_tax  = fields.Html(related='tax_id.description')

class LocationMigrationJz(models.Model):
    _name  = 'location.migration.jz'
    name = fields.Char(required=True)
    id_sql = fields.Integer(required=True)
    migrate_id = fields.Many2one('migrate.jz',required=True)
    location_id = fields.Many2one('stock.location')


class CountryMigrationJz(models.Model):
    _name  = 'country.migration.jz'
    name = fields.Char(required=True)
    id_sql = fields.Integer(required=True)
    migrate_id = fields.Many2one('migrate.jz',required=True)
    country_id = fields.Many2one('res.country')


class StateMigrationJz(models.Model):
    _name  = 'state.migration.jz'
    name = fields.Char(required=True)
    id_sql = fields.Integer(required=True)
    migrate_id = fields.Many2one('migrate.jz',required=True)
    state_id = fields.Many2one('res.country.state')

class CityMigrationJz(models.Model):
    _name  = 'city.migration.jz'
    name = fields.Char(required=True)
    id_sql = fields.Integer(required=True)
    migrate_id = fields.Many2one('migrate.jz',required=True)
    city_id = fields.Integer()
