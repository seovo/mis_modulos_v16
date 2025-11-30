import psycopg2
from psycopg2 import sql

class AccountMove(models.Model):
    _name = 'account.move'
    invoice_id = field.Integer
