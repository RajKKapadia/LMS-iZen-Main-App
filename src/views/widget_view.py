from flask import Blueprint, send_file, request

from src import logging

widget_view = Blueprint('widget_view', __name__, url_prefix="/api/widget")


logger = logging.getLogger(__name__)


@widget_view.get("/chatWidget.js")
def handle_get():
    data = request.args.to_dict()
    logger.info(data)
    return send_file('static/chatWidget.js', mimetype='application/javascript')
