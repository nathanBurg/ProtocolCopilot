from dotenv import load_dotenv
import psycopg2
from psycopg2 import Error
import os
from threading import Lock

load_dotenv()

class PostgreSQLClient:
    _instance = None
    _lock = Lock()  

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PostgreSQLClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):  # prevent reinitialization
            self.database_url = os.getenv('DATABASE_URL')
            self.connection = None
            self._initialized = True

    def connect(self):
        # Always create a new connection for each request to avoid connection issues
        try:
            connection = psycopg2.connect(self.database_url)
            print("Connected to PostgreSQL successfully.")
            return connection
        except psycopg2.Error as err:
            print(f"Connection failed: {err}")
            return None

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

