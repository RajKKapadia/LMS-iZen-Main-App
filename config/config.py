import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = os.getenv('MYSQL_PORT')
MYSQL_DB_NAME = os.getenv('MYSQL_DB_NAME')

FIREWORKS_API_KEY = os.getenv('FIREWORKS_API_KEY')
FIREWORKS_BASE_MODEL = os.getenv('FIREWORKS_BASE_MODEL')
FIREWORKS_TOOL_MODEL = os.getenv("FIREWORKS_TOOL_MODEL")
FIREWORKS_API_ENDPOINT = os.getenv('FIREWORKS_API_ENDPOINT')

OPEN_WEB_UI_ENDPOINT = os.getenv("OPEN_WEB_UI_ENDPOINT")
OPEN_WEB_UI_API_KEY = os.getenv("OPEN_WEB_UI_API_KEY")

ERROR_MESSAGE = "An error occurred. Please try again later."
