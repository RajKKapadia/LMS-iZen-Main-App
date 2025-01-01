from flask import Flask
from flask_cors import CORS

from src.views.home_view import home
from src.views.widget_view import widget_view
from src.views.chat_view import chat
from src.views.demo_view import demo

app = Flask(__name__)
CORS(app)


app.register_blueprint(home)
app.register_blueprint(widget_view)
app.register_blueprint(chat)
app.register_blueprint(demo)
