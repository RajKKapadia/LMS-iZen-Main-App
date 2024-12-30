from flask import Blueprint, send_file

widget_view = Blueprint('widget_view', __name__, url_prefix="/api/widget")


@widget_view.get("/")
def handle_get():
    return send_file('static/chatWidget.js', mimetype='application/javascript')
