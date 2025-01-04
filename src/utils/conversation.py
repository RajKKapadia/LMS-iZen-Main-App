import json

from src.utils.database_functions import DatabaseManager
from src.utils.openai_functions import tool_chat_completion, general_chat_completion
from src.utils.prompts import get_chat_completion_prompt, get_format_sql_response_messages
from config import config
from src import logging
from src.utils.utils import ChatRequest


db_manager = DatabaseManager()


logger = logging.getLogger(__name__)


def handle_chat_completion(new_chat: ChatRequest) -> str:
    chat_response = tool_chat_completion(new_chat=new_chat)
    if chat_response == None:
        return config.ERROR_MESSAGE
    assistant_message = chat_response.choices[0].message
    logger.info(assistant_message)
    if assistant_message.content == None:
        '''Call SQL and generate the response.
        '''
        if assistant_message.tool_calls[0].function.name == "ask_database":
            sql_query = json.loads(
                assistant_message.tool_calls[0].function.arguments)["query"]
            logger.info(f'SQL query -> {sql_query}')
            sql_response = db_manager.execute_query(sql_query)
            logger.info(f'SQL response -> {sql_response}')
        if sql_response == '':
            chat_completion_prompt = get_chat_completion_prompt(
                new_chat.query, new_chat.messages[:-1])
            messages = []
            messages.append(
                {'role': 'user', 'content': chat_completion_prompt})
            response = general_chat_completion(messages=messages)
        else:
            messages = get_format_sql_response_messages(
                sql_response=sql_response)
            response = general_chat_completion(messages=messages)
    else:
        response = assistant_message.content

    return response
