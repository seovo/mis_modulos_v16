from odoo.exceptions import ValidationError

import psycopg2
from psycopg2 import sql
from odoo import api, fields, models , _


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

class TaxMigrationJz(models.Model):
    _name  = 'tax.migration.jz'
    name = fields.Char(required=True)
    id_sql = fields.Integer(required=True)
    migrate_id = fields.Many2one('migrate.jz',required=True)
    tax_id = fields.Many2one('account.tax')

class LocationMigrationJz(models.Model):
    _name  = 'location.migration.jz'
    name = fields.Char(required=True)
    id_sql = fields.Integer(required=True)
    migrate_id = fields.Many2one('migrate.jz',required=True)
    location_id = fields.Many2one('stock.location')
