import snowflake.connector
from pymongo import MongoClient
from config import USER, PASSWORD, ACCOUNT, WAREHOUSE, DATABASE, SCHEMA, ROLE, MONGODB_URI


# Snowflake connection
def get_snowflake_connection():
    return snowflake.connector.connect(
        user=USER,
        password=PASSWORD,
        account=ACCOUNT,
        warehouse=WAREHOUSE,
        database=DATABASE,
        schema=SCHEMA,
        role=ROLE
    )
# MongoDB connection
def get_mongodb_connection():
    client = MongoClient(MONGODB_URI)
    return client