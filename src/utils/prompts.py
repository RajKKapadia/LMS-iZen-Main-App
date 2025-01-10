from datetime import datetime
from typing import Dict, List

from src.utils.utils import ChatRequest


def get_sql_tool(database_schema_string: str, user_id: str) -> List[Dict]:
    sql_tool = [
        {
            "type": "function",
            "function": {
                "name": "ask_database",
                "description": "Use this function to answer user questions about Production data. Input should be a fully formed MySQL query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": f"""MySQL query extracting info to answer the user's question.
- Strictly use column names and table names explicitly defined in this database information: {database_schema_string}.
- Never reference or assume any columns or tables outside of this information.
- If the question pertains to user-specific data, include `WHERE user_id = {user_id}` in the query.
- Today's date is: {datetime.now().strftime("%Y-%m-%d")}
- The query should be returned in plain text, not in JSON."""
                        }
                    },
                    "required": ["query"],
                },
            }
        }
    ]

    return sql_tool


def get_decision_prompt(new_chat: ChatRequest) -> str:
    decision_prompt = f"""User's query: {new_chat.query}, in the context of the following chat history: {new_chat.messages}, Determine if the query requires accessing the learning management system database. Provide your output in the following JSON format:
    ```json
    {{
        "needsDatabase": "yes/no",
    }}
    ```"""

    return decision_prompt


def get_chat_completion_prompt(query: str, formated_chat_history: List[Dict]) -> str:
    chat_completion_prompt = f"""Consider yourself as a helpful data analyst. A user has asked a question: {query}, in the context of the following chat history: {formated_chat_history}, politely reply that you don"t have the answer for the question."""

    return chat_completion_prompt


def get_format_sql_response_messages(sql_response: str) -> List[Dict]:
    formatted_sql_response_messages = [
        {"role": "system", "content": "Consider yourself as a helpful data analyst. You help user get information about the data and answer their question."},
        {"role": "user", "content": f"""Convert the following MySQL data into natural language conversation, 
keep the response short and concise and never mention id of the MySQL data. SQL data: {sql_response}"""}
    ]

    return formatted_sql_response_messages


def get_chat_completion_request_system_message() -> Dict:
    system_message = {
        "role": "system", "content": "You are a data analyst. You help user get information about the database."}

    return system_message
