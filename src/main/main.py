from flask import Flask, render_template
from flask_cors import CORS
from flask_talisman import Talisman

from src.views.home_view import home
from src.views.widget_view import widget_view
from src.views.chat_view import chat

app = Flask(__name__)
CORS(app)
Talisman(app)


@app.route("/")
def handle_get():
    return render_template("index.html")


app.register_blueprint(home)
app.register_blueprint(widget_view)
app.register_blueprint(chat)
