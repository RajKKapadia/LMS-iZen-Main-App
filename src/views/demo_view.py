from flask import Blueprint, render_template

from src import logging

demo = Blueprint(
    "demo",
    __name__,
    url_prefix=f"/demo"
)


logger = logging.getLogger(__name__)


@demo.route("/")
def handle_get():
    return render_template("index.html")
