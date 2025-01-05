from flask import Blueprint, jsonify, request

from src.utils.conversation import handle_chat_completion
from src.utils.openai_functions import get_decision_response
from src.utils.prompts import get_decision_prompt
from src.utils.utils import ChatRequest, chat_completion_open_web_ui
from src import logging

chat = Blueprint(
    "chat",
    __name__,
    url_prefix=f"/api/chat"
)


logger = logging.getLogger(__name__)


@chat.post("/talk")
def handle_get():
    data = request.get_json()
    new_chat = ChatRequest(**data)
    messages = new_chat.messages
    query = new_chat.messages[-1]["content"]
    new_chat.query = query

    logger.info(f"Query: {query}")
    logger.info(f"Messages: {messages}")
    logger.info(f"User id: {new_chat.user_id}")

    decision_prompt = get_decision_prompt(new_chat=new_chat)
    response = get_decision_response(messages=[{
        "role": "user",
        "content": decision_prompt
    }])

    if response["needsDatabase"] == "yes":
        content = handle_chat_completion(new_chat=new_chat)
        logger.info(content)
        return jsonify({
            "message": content
        })
    else:
        content = chat_completion_open_web_ui(new_chat=new_chat)
        logger.info(content)
        return jsonify({
            "message": content
        })
