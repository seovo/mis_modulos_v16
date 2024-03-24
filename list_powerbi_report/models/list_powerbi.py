from odoo import models, exceptions, fields , _

class ListPowerBi(models.Model):
    _name = "list.powerbi"
    _description = "list.powerbi"
    name = fields.Char(required=True)
    url = fields.Char(compute='get_url')
    def get_url(self):
        for record in self:
            record.url = '/ui/powerbi/' + str(record.id)

    ####
    authentication_mode = fields.Selection([
        ('serviceprincipal','Service Principal'),
        ('masteruser','MasterUser')
    ],default='serviceprincipal',required=True)
    client_id = fields.Char()
    authority_url = fields.Char(default='https://login.microsoftonline.com/organizations',required=True)
    power_bi_user = fields.Char()
    power_bi_pass = fields.Char()
    tenant_id = fields.Char()
    client_secret = fields.Char()
    scope_base = fields.Char(default='https://analysis.windows.net/powerbi/api/.default',required=True)
    workspace_id = fields.Char()
    report_id = fields.Char()


    def powerbi_ui(self):
        import pandas as pd
        import pymssql
        #import psycopg2
        #import psycopg2.extras

        # Function to fetch data from SQL Server data table
        def fetch_data_from_sql_server(server, database, username, password, table_name):
            connection = pymssql.connect(server=server, database=database, user=username, password=password)

            query = f'SELECT * FROM {table_name};'
            data = pd.read_sql(query, connection)
            connection.close()

            return data

            # Configuration for SQL Server
        sql_server_config = {
                "server": "dbserverdatawave.database.windows.net",
                "database": "Datawave",
                "username": "datawaveuser",
                "password": "JT5j]6u2?XZzdw4fS#CK[pWBH!QxsD$t",
                "table_name": "Products",
        }

        data = fetch_data_from_sql_server(**sql_server_config)

        raise ValueError(data)
        return
        self.ensure_one()

        # self.rename_sequence_shf()
        url = 'ui/powerbi/' + str(self.id)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': url,
        }