from config import SCHEMA

# Schema information
def get_schema_info(cursor):
    query = """
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = %s 
    ORDER BY table_name, ordinal_position;
    """
    cursor.execute(query, (SCHEMA,))
    schema_info = cursor.fetchall()
    
    # Convert to a structured dict
    tables_info = {}
    for table_name, column_name, data_type in schema_info:
        if table_name not in tables_info:
            tables_info[table_name] = []
        tables_info[table_name].append({'column_name': column_name, 'data_type': data_type})
    
    return tables_info
