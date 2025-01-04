from pydantic import BaseModel
from typing import Dict, List, Optional

import requests

from src import logging
from config import config


logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    messages: List[Dict[str, str]] = []
    user_id: Optional[str] = ""
    database_schema_string: Optional[str] = ""
    query: Optional[str] = ""


def chat_completion_open_web_ui(new_chat: ChatRequest) -> str:
    # API endpoint
    url = f"{config.OPEN_WEB_UI_ENDPOINT}/api/chat/completions"

    headers = {
        "Authorization": f"Bearer {config.OPEN_WEB_UI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": config.OPEN_WEB_UI_MODEL,
        "messages": new_chat.messages,
        "files": [
            {"type": "collection", "id": "19e01a6a-2aed-4fa4-8ca7-54fff508546d"}
        ]
    }

    try:
        # Send the request
        response = requests.post(url, headers=headers, json=payload)
        # Check if the response is successful
        response.raise_for_status()
        # Parse and return the response
        response = response.json()
        logger.info(response)
        return response["choices"][0]["message"]["content"]

    except Exception as e:
        logger.error(f"Error making chat completion request: {e}")
        return config.ERROR_MESSAGE
