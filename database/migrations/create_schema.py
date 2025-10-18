import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.src.dal.databases.my_sql_heatwave_client import MySQLHeatwaveClient

client = MySQLHeatwaveClient()

with open("create_schema.sql", "r") as f:
    sql_script = f.read()

client.execute_sql(sql_script)