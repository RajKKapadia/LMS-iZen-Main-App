import decimal
import json
import datetime
from typing import Generator, List, Dict, Any, Optional, Tuple
from contextlib import contextmanager

from mysql.connector import pooling, Error as MySQLError
from mysql.connector.connection import MySQLConnection

from config import config


class DatabaseConfig:
    def __init__(self):
        self.pool_config = {
            "pool_name": "mypool",
            "pool_size": 10,
            "host": config.MYSQL_HOST,
            "port": config.MYSQL_PORT,
            "user": config.MYSQL_USER,
            "password": config.MYSQL_PASSWORD,
            "database": config.MYSQL_DB_NAME,
        }
        self.connection_pool = self._create_pool()

    def _create_pool(self) -> pooling.MySQLConnectionPool:
        try:
            return pooling.MySQLConnectionPool(**self.pool_config)
        except MySQLError as e:
            print(f"Failed to create connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self) -> Generator[MySQLConnection, None, None]:
        conn = None
        try:
            conn = self.connection_pool.get_connection()
            yield conn
        except MySQLError as e:
            print(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()


class NumberFormatter:
    @staticmethod
    def truncate_float(number: float, places: int) -> float:
        return int(number * (10 ** places)) / 10 ** places

    @staticmethod
    def format_number(amount: float) -> str:
        if amount < 1e3:
            return str(amount)
        if 1e3 <= amount < 1e5:
            return f"{NumberFormatter.truncate_float((amount / 1e3), 2)}K"
        if 1e5 <= amount < 1e7:
            return f"{NumberFormatter.truncate_float((amount / 1e5), 2)}L"
        return f"{NumberFormatter.truncate_float(amount / 1e7, 2)}Cr"


class DataSerializer:
    @staticmethod
    def serialize(obj: Any) -> str:
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, decimal.Decimal):
            return NumberFormatter.format_number(float(obj))
        raise TypeError(f"Object of type {type(obj)} is not serializable")


class DatabaseManager:
    def __init__(self):
        self.db_config = DatabaseConfig()

    def get_table_names(self) -> List[str]:
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s
        """
        with self.db_config.get_connection() as conn:
            with conn.cursor(prepared=True) as cursor:
                cursor.execute(query, (config.MYSQL_DB_NAME,))
                return [table[0] for table in cursor]

    def get_column_info(self, table_name: str) -> List[Tuple[str, str]]:
        query = """
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """
        with self.db_config.get_connection() as conn:
            with conn.cursor(prepared=True) as cursor:
                cursor.execute(query, (config.MYSQL_DB_NAME, table_name))
                return [(col[0], col[1]) for col in cursor]

    def get_database_info(self) -> List[Dict[str, Any]]:
        return [
            {
                "table_name": table_name,
                "column_names": self.get_column_info(table_name)
            }
            for table_name in self.get_table_names()
        ]

    def execute_query(self, query: str, params: Optional[tuple] = None) -> str:
        try:
            with self.db_config.get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, params)
                    results = [row for row in cursor]
                    return json.dumps(results, default=DataSerializer.serialize)
        except MySQLError as e:
            print(f"Query execution error: {e}")
            raise


def get_database_schema_string(db_manager: DatabaseManager) -> str:
    schema_info = db_manager.get_database_info()
    return "\n".join(
        f"Table: {table['table_name']}\nColumns:\n" +
        "\n".join(f"  - {col[0]} ({col[1]})" for col in table['column_names'])
        for table in schema_info
    )
