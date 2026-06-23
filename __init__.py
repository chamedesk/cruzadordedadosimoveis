from flask import Flask
from .routes import bp
from .database import init_db


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "gold-captacao-dev"
    init_db()
    app.register_blueprint(bp)
    return app
