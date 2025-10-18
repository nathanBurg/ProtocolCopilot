from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
import os
from threading import Lock

load_dotenv()

class MySQLHeatwaveClient:
    _instance = None
    _lock = Lock()  

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MySQLHeatwaveClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):  # prevent reinitialization
            self.host = os.getenv('MYSQL_HEATWAVE_HOST')
            self.port = int(os.getenv('MYSQL_HEATWAVE_PORT'))
            self.user = os.getenv('MYSQL_HEATWAVE_USER')
            self.password = os.getenv('MYSQL_HEATWAVE_PASSWORD')
            self.database = os.getenv('MYSQL_HEATWAVE_DATABASE')
            self.connection = None
            self._initialized = True

    def connect(self):
        if self.connection and self.connection.is_connected():
            return self.connection

        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("Connected to MySQL HeatWave successfully.")
        except mysql.connector.Error as err:
            print(f"Connection failed: {err}")
            self.connection = None

        return self.connection

    def execute_sql(self, sql: str):
        """Execute a SQL string (single or multiple statements)."""
        conn = self.connect()
        if not conn:
            print("No active connection.")
            return

        cursor = conn.cursor()
        try:
            statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
            for stmt in statements:
                cursor.execute(stmt)
            conn.commit()
        except Error as e:
            print(f"Error executing SQL: {e}")
        finally:
            cursor.close()
            conn.close()

