from odoo.exceptions import ValidationError

import psycopg2
from psycopg2 import sql
from odoo import api, fields, models , _


class JournalMigrationJz(models.Model):
    _name  = 'journal.migration.jz'
    name = fields.Char(required=True)
    id_sql = fields.Integer(required=True)
    migrate_id = fields.Many2one('migrate.jz',required=True)
    journal_id = fields.Many2one('account.journal',required=True)
