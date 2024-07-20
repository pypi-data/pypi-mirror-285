from tqdm import tqdm
import pymysql
import pandas as pd


def check_connection(host , port , username , password , database):
    connection = pymysql.connect(host=host, port=int(port), user=username , password=password , database=database)
    return connection



def read_table(table_name , database):
    connection = check_connection(database)
    connection = pymysql.connect(host=connection.host, port=connection.port, user=connection.user, password=connection.password)

    sql_query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(sql_query, connection)

    return df


def database_exist(database_name):
    connection = check_connection(database_name)
    
    cursor = connection.cursor()
    cursor.execute(f"SHOW DATABASES LIKE '{database_name}'")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(f"CREATE DATABASE {database_name}")
        connection = pymysql.connect(host=connection.host , user=connection.user , password=connection.password , database=database_name)
    else:
        connection = pymysql.connect(host=connection.host , user=connection.user , password=connection.password , database=database_name)
    return connection




def create_partition_table_shamsi(df , table_name , connection , range_key , primary_key_list , start_year_partition , end_year_partition):

    start_year = start_year_partition
    start_month = 1
    end_year = end_year_partition
    end_month = 12
    year = start_year
    month = start_month
    partition_query = ''
    first_iteration = True

    while year <= end_year:
        while (year < end_year and month <= 12) or (year == end_year and month <= end_month):
            partition_name = f"p{year}m{month:02}"
            partition_value = int(f"{year}{month:02}32")
            partition_clause = f"PARTITION `{partition_name}` VALUES LESS THAN ({partition_value}) ENGINE = InnoDB"
            
            if first_iteration:
                partition_query += partition_clause
                first_iteration = False
            else:
                partition_query += f", {partition_clause}"
            
            month += 1
            if month > 12:
                month = 1
                year += 1
                
        break


    cursor = connection.cursor()
    column_data_types = {"int32":'INT' , 'int64': 'INT', 'float64': 'FLOAT', 'datetime64': 'DATETIME', 'bool': 'BOOL', 'object': 'VARCHAR(70)'}
    columns = ', '.join([f'`{column}` {column_data_types[str(data_type)]}' for column, data_type in df.dtypes.items()])
    query_set_partition = f'''CREATE TABLE {table_name} ({columns}, KEY `{table_name}_index` ({' , '.join(primary_key_list)})) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci PARTITION BY RANGE (`{range_key}`) ({partition_query})'''
    cursor.execute(query_set_partition)
    connection.commit()



def create_partition_table_miladi(df , table_name , connection , range_key , primary_key_list , start_year_partition , end_year_partition):


    if not table_exists(table_name , connection):

        start_year = start_year_partition
        start_month = 1
        end_year = end_year_partition
        end_month = 12
        year = start_year
        month = start_month
        partition_query = ''
        first_iteration = True

        while year <= end_year:
            while (year < end_year and month <= 12) or (year == end_year and month <= end_month):
                partition_name = f"p{year}m{month:02}"
                partition_value = int(f"{year}{month:02}32")
                partition_clause = f"PARTITION `{partition_name}` VALUES LESS THAN ({partition_value}) ENGINE = InnoDB"
                
                if first_iteration:
                    partition_query += partition_clause
                    first_iteration = False
                else:
                    partition_query += f", {partition_clause}"
                
                month += 1
                if month > 12:
                    month = 1
                    year += 1
                    
            break

        cursor = connection.cursor()
        column_data_types = {"int32":'INT' , 'int64': 'INT', 'float64': 'FLOAT', 'datetime64': 'DATETIME', 'bool': 'BOOL', 'object': 'VARCHAR(70)'}
        columns = ', '.join([f'`{column}` {column_data_types[str(data_type)]}' for column, data_type in df.dtypes.items()])
        query_set_partition = f'''CREATE TABLE {table_name} ({columns}, KEY `{table_name}_index` ({' , '.join(primary_key_list)})) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci PARTITION BY RANGE (`{range_key}`) ({partition_query})'''
        cursor.execute(query_set_partition)
        connection.commit()
    else:
        pass



def create_table(df, table_name, connection):
    cursor = connection.cursor()
    
    column_data_types = {"int32": 'INT', 'int64': 'INT', 'float64': 'FLOAT', 'datetime64': 'DATETIME', 'bool': 'BOOL', 'object': 'LONGTEXT'}
    columns = []

    for column, data_type in df.dtypes.items():
        if data_type == 'object':
            max_length = df[column].str.len().max()
            if max_length >= 70:
                columns.append(f"`{column}` LONGTEXT")
            else:
                columns.append(f"`{column}` VARCHAR(70)")
        else:
            columns.append(f"`{column}` {column_data_types[str(data_type)]}")

    columns_str = ', '.join(columns)
    
    query = f"CREATE TABLE {table_name} ({columns_str})"
    cursor.execute(query)
    connection.commit()


def table_exists(table_name , connection):
    
    cursor = connection.cursor()
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    result = cursor.fetchone()
    if result == None:
        return False
    else:
        return True



def sql_saver(df, table_name , connection):

    if not table_exists(table_name , connection):
        create_table(df, table_name , connection)

    cursor = connection.cursor()
    columns = ', '.join([f'`{column}`' for column in df.columns])
    values_str = ','.join(['%s'] * len(df.columns))
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({values_str})"
    for row in tqdm(df.values):
        data = tuple(row)
        cursor.execute(query, data)
    connection.commit()



def sql_saver_with_primarykey(df, table_name , primary_key_list , connection):

    if not table_exists(table_name , connection):
        create_table(df, table_name , connection)

    cursor = connection.cursor()
    columns = ', '.join([f'`{column}`' for column in df.columns])
    values_str = ','.join(['%s'] * len(df.columns))
    query = f"INSERT IGNORE INTO {table_name} ({columns}) VALUES ({values_str});"
    connection.commit()
    query3 = f"ALTER TABLE {table_name} DROP PRIMARY KEY;"
    query_check_key = f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY';"
    cursor.execute(query_check_key)
    if cursor.fetchone() is not None:
        cursor.execute(query3)
        connection.commit()
    else:
        pass
    query2 = f"ALTER TABLE {table_name} ADD PRIMARY KEY ({' , '.join(primary_key_list)})"
    cursor.execute(query2)
    connection.commit()
    
    for row in tqdm(df.values):
        data = tuple(row)
        cursor.execute(query, data)
    connection.commit()



def sql_saver_with_primarykey_and_update(df, table_name , primary_key_list , connection):

    
    if not table_exists(table_name , connection):
        create_table(df, table_name , connection)

    cursor = connection.cursor()
    columns = ', '.join([f'`{column}`' for column in df.columns])
    values_str = ','.join(['%s'] * len(df.columns))
    query = f"INSERT IGNORE INTO {table_name} ({columns}) VALUES ({values_str});"
    connection.commit()
    update_str = ', '.join([f'`{column}` = VALUES(`{column}`)' for column in df.columns])
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({values_str}) ON DUPLICATE KEY UPDATE {update_str};"
    connection.commit()
    query3 = f"ALTER TABLE {table_name} DROP PRIMARY KEY;"
    query_check_key = f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY';"
    cursor.execute(query_check_key)
    if cursor.fetchone() is not None:
        cursor.execute(query3)
        connection.commit()
    else:
        pass
    query2 = f"ALTER TABLE {table_name} ADD PRIMARY KEY ({' , '.join(primary_key_list)})"
    cursor.execute(query2)
    connection.commit()
    
    for row in tqdm(df.values):
        data = tuple(row)
        cursor.execute(query, data)
    connection.commit()