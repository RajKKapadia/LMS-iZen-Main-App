from flask import Blueprint, jsonify, request

from src.utils.conversation import handle_chat_completion
from src.utils.openai_functions import get_decision_response
from src.utils.prompts import get_decision_prompt
from src.utils.utils import chat_completion_open_web_ui
from src import logging

chat = Blueprint(
    "chat",
    __name__,
    url_prefix=f"/api/chat"
)


logger = logging.getLogger(__name__)


@chat.post("/")
def handle_get():
    data = request.get_json()
    messages = data["messages"]
    query = messages[-1]["content"]

    logger.info(query)
    logger.info(messages)

    decision_prompt = get_decision_prompt(query=query, messages=messages[:-1])
    response = get_decision_response(messages=[{
        "role": "user",
        "content": decision_prompt
    }])

    if response["needsDatabase"] == "yes":
        content = handle_chat_completion(query=query, messages=messages)
        logger.info(content)
        return jsonify({
            "message": content
        })
    else:
        content = chat_completion_open_web_ui(messages=messages)
        logger.info(content)
        return jsonify({
            "message": content
        })
