import decimal
import json
import datetime
from typing import Generator, List, Dict, Any, Optional, Tuple
from contextlib import contextmanager

from mysql.connector import pooling, Error as MySQLError
from mysql.connector.connection import MySQLConnection
from openai import OpenAI

from config import config
from src import logging

logger = logging.getLogger(__name__)

client = OpenAI(
    base_url=config.FIREWORKS_API_ENDPOINT,
    api_key=config.FIREWORKS_API_KEY
)


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

    def get_table_names(self) -> List[Tuple[str, str]]:
        query = """
            SELECT table_name , table_comment
            FROM information_schema.tables 
            WHERE table_schema = %s
        """
        with self.db_config.get_connection() as conn:
            with conn.cursor(prepared=True) as cursor:
                cursor.execute(query, (config.MYSQL_DB_NAME,))
                return [(table[0], table[1]) for table in cursor]

    def get_sample_row(self, table_name: str) -> Optional[Dict[str, Any]]:
        query = f"SELECT * FROM {table_name} LIMIT 1"
        try:
            with self.db_config.get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    row = cursor.fetchone()
                    return row
        except MySQLError as e:
            return None

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
                "columns": self.get_column_info(table_name),
                "sample_row": self.get_sample_row(table_name)
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
            return ""


def get_database_schema_string(
    db_manager: DatabaseManager,
    user_query: str,
    chat_history: List[Dict[str, str]],
) -> str:
    # Fetch all table names
    table_names = db_manager.get_table_names()

    formatted_table_strings = [
        f"Table name: {name}\nTable description: {comment}"
        for name, comment in table_names
    ]

    logger.info("Tables:")
    logger.info(formatted_table_strings)

    # Prepare prompt for OpenAI
    prompt = f"""You are an AI assistant tasked with analyzing database structures.
Based on the user's query and chat history, identify the tables relevant to the query.

User Query: {user_query}

Chat History: {chat_history}

Available Tables: {formatted_table_strings}

Provide a comma-separated list of the relevant table names:
"""

    # Call OpenAI API
    response = client.chat.completions.create(
        model=config.FIREWORKS_BASE_MODEL,
        messages=[{"role": "system", "content": prompt}]
    )

    # Parse the OpenAI response to extract table names
    relevant_tables = response.choices[0].message.content.strip().split(',')

    logger.info(relevant_tables)

    # Fetch details for the relevant tables
    schema_info = []
    for table_name in [table.strip() for table in relevant_tables]:
        columns = db_manager.get_column_info(table_name)
        sample_row = db_manager.get_sample_row(table_name)
        schema_info.append({
            "table_name": table_name,
            "columns": columns,
            "sample_row": sample_row
        })

    # Generate schema string
    result = []
    for table in schema_info:
        table_info = [f"Table: {table['table_name']}"]
        table_info.append("Columns:")
        table_info.extend(
            f"  - {col[0]} ({col[1]})" for col in table['columns']
        )

        if table['sample_row']:
            table_info.append("\nSample Row:")
            for col_name, value in table['sample_row'].items():
                formatted_value = json.dumps(
                    value, default=DataSerializer.serialize)
                table_info.append(f"  - {col_name}: {formatted_value}")

        result.append("\n".join(table_info))

    return "\n\n".join(result)
