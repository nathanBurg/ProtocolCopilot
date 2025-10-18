from dotenv import load_dotenv
import mysql.connector
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


# Example usage:
if __name__ == "__main__":
    client = MySQLHeatwaveClient()
    conn = client.connect()
    print(conn)
