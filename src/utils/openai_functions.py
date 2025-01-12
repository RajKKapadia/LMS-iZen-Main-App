from typing import Dict, List
import json

from openai import OpenAI
from openai.types.chat import ChatCompletion

from config import config
from src import logging
from src.utils.database_functions import DatabaseManager, get_database_schema_string
from src.utils.prompts import get_chat_completion_request_system_message, get_sql_tool
from src.utils.utils import ChatRequest

logger = logging.getLogger(__name__)

client = OpenAI(
    base_url=config.FIREWORKS_API_ENDPOINT,
    api_key=config.FIREWORKS_API_KEY
)


db_manager = DatabaseManager()


def get_decision_response(messages: List[Dict[str, str]]) -> Dict[str, str]:
    try:
        response = client.chat.completions.create(
            messages=messages,
            model=config.FIREWORKS_TOOL_MODEL,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        content = content.replace(
            "```json", "").replace("```", "").strip()
        print(content)
        print(type(content))

        return json.loads(content)
    except Exception as e:
        logger.error(e)
        return {
            "needsDatabase": "no"
        }


def tool_chat_completion(new_chat: ChatRequest) -> ChatCompletion | None:
    sql_tool = get_sql_tool(
        database_schema_string=get_database_schema_string(
            db_manager=db_manager,
            chat_history=new_chat.messages,
            user_query=new_chat.query
        ), user_id=new_chat.user_id)
    logger.info(sql_tool)
    try:
        new_messages = []
        system_message = get_chat_completion_request_system_message()
        new_messages.append(system_message)
        for message in new_chat.messages:
            new_messages.append(message)

        response = client.chat.completions.create(
            messages=new_messages,
            tools=sql_tool,
            model=config.FIREWORKS_TOOL_MODEL,
            temperature=0.7,
            max_tokens=1024
        )

        return response
    except Exception as e:
        logger.error(e)
        return None


def general_chat_completion(messages: List[Dict[str, str]]) -> str:
    try:
        response = client.chat.completions.create(
            model=config.FIREWORKS_BASE_MODEL,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(e)
        return config.ERROR_MESSAGE
