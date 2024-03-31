def sync_nine_box_range_date(self):
    return

    # raise ValueError(self.get_connection_string())
    if not self.get_connection_string():
        return
    data = self.fetch_data_from_sql_server(self.get_connection_string(),
                                           f'SELECT * FROM RangeConfigs WHERE TenantId = {self.tenant_id};')
    for index, row in data.iterrows():
        name_start = ''
        name_end = ''
        letra = str(row['RangeString']).lower()
        if row['RangeType'] == 'ABC':
            name_start = f'abc_{letra}_start'
            name_end = f'abc_{letra}_end'

        if row['RangeType'] == 'ABC_MC':
            name_start = f'abc_{letra}_start_mc'
            name_end = f'abc_{letra}_end_mc'

        if row['RangeType'] == 'XYZ':
            name_start = f'xyz_{letra}_start'
            name_end = f'xyz_{letra}_end'

        if row['RangeType'] == 'XYZ_MC':
            name_start = f'xyz_{letra}_start_mc'
            name_end = f'xyz_{letra}_end_mc'

        # self.write({
        #    name_start: row['RangeStart'] ,
        #    name_end: row['RangeEnd'],

        # })
