from flask import Blueprint, jsonify

from src import logging

home = Blueprint(
    "home",
    __name__,
    url_prefix=f"/api/home"
)


logger = logging.getLogger(__name__)


@home.get("/")
def handle_get():
    return jsonify({
        "message": "Application is running."
    })
