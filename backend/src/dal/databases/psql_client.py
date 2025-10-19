from dotenv import load_dotenv
import psycopg2
from psycopg2 import Error, OperationalError
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
        if not hasattr(self, "_initialized"):
            self.database_url = os.getenv("DATABASE_URL")
            self.connection = None
            self._initialized = True
            self.connect()

    def connect(self):
        """Establish or re-establish the connection."""
        if self.connection and not self.connection.closed:
            return self.connection
        try:
            self.connection = psycopg2.connect(self.database_url)
            self.connection.autocommit = False
            print("Connected to PostgreSQL successfully.")
        except Error as e:
            print(f"Connection failed: {e}")
            self.connection = None
        return self.connection

    def execute_sql(self, sql: str, params=None):
        """Execute SQL, keeping persistent connection alive."""
        conn = self.connect()
        if not conn:
            print("No active connection.")
            return

        try:
            with conn.cursor() as cursor:
                statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]
                for stmt in statements:
                    cursor.execute(stmt, params)
                conn.commit()
        except (Error, OperationalError) as e:
            print(f"Error executing SQL: {e}")
            if conn:
                conn.rollback()
                # Try reconnecting if connection dropped
                self.connection = None
        return

    def close(self):
        """Manually close the connection."""
        if self.connection and not self.connection.closed:
            self.connection.close()
            print("Connection closed.")
