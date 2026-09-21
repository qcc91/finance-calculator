import logging
from logging.handlers import RotatingFileHandler

from flask import Flask

from .config import Config
from .errors import register_error_handlers
from .extensions import cors, db
from .routes import BLUEPRINTS


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        if isinstance(config, dict):
            app.config.update(config)
        else:
            app.config.from_object(config)

    _configure_logging(app)
    db.init_app(app)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"])
    register_error_handlers(app)

    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

    if app.config["RUN_SCHEDULER"]:
        from .services.tasks import start_scheduler

        start_scheduler(app)

    return app


def _configure_logging(app):
    level = getattr(logging, app.config["LOG_LEVEL"], logging.INFO)
    app.logger.setLevel(level)
    if app.config.get("TESTING"):
        return

    log_file = app.config["LOG_FILE"]
    log_file.parent.mkdir(parents=True, exist_ok=True)
    if not any(isinstance(handler, RotatingFileHandler) for handler in app.logger.handlers):
        handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        handler.setLevel(level)
        app.logger.addHandler(handler)
