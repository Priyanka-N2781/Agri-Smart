"""
AgriSmart – Flask application factory
"""

import os
import logging
from flask import Flask
from flask_cors import CORS

from .config import config
from .routes import main_bp


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
    )

    # Config
    app.config["SECRET_KEY"]         = config.SECRET_KEY
    app.config["DEBUG"]              = config.DEBUG
    app.config["UPLOAD_FOLDER"]      = config.UPLOAD_FOLDER
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

    # Create required directories
    os.makedirs(config.MODELS_DIR,  exist_ok=True)
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

    # Extensions
    CORS(app)

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    )

    # Blueprint
    app.register_blueprint(main_bp)

    return app
