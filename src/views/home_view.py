from flask import Blueprint, jsonify

home = Blueprint(
    "home",
    __name__,
    url_prefix=f"/api/home"
)


@home.get("/")
def handle_get():
    return jsonify({
        "message": "Application is running."
    })
