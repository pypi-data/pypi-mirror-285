import importlib
import json
import logging
import os
from pathlib import Path
from urllib.parse import unquote

import typer
from flask import Flask as BaseFlask
from flask import Response
from flask import request
from flask.logging import default_handler
from werkzeug.exceptions import HTTPException

from artorias.flask.exception import APIException
from artorias.flask.json import JSONProvider
from artorias.flask.utils import find_blueprints
from artorias.flask.utils import find_commands


class Flask(BaseFlask):
    json_provider_class = JSONProvider

    def __init__(
        self,
        import_name: str,
        static_url_path: str | None = None,
        static_folder: str | os.PathLike | None = "static",
        static_host: str | None = None,
        host_matching: bool = False,
        subdomain_matching: bool = False,
        template_folder: str | os.PathLike | None = "templates",
        instance_path: str | None = None,
        instance_relative_config: bool = False,
        root_path: str | None = None,
    ):
        super().__init__(
            import_name,
            static_url_path,
            static_folder,
            static_host,
            host_matching,
            subdomain_matching,
            template_folder,
            instance_path,
            instance_relative_config,
            root_path,
        )

        self.init()

    def init(self):
        self.load_settings()
        self.init_logger()
        os.chdir(os.path.dirname(self.root_path))
        self.logger.debug(f"Current work dir: {os.getcwd()}")

        self.load_blueprints()
        self.load_exts()
        self.load_commands()
        self.load_error_handlers()

    def load_exts(self):
        from artorias.flask import celery
        from artorias.flask.exts import cors
        from artorias.flask.exts import db
        from artorias.flask.exts import jwt
        from artorias.flask.exts import migrate
        from artorias.flask.exts import redis

        db.init_app(self)
        migrate.init_app(self)
        cors.init_app(self)
        jwt.init_app(self)

        if self.config.get("CELERY"):
            celery.init_app(self)

        @self.shell_context_processor
        def make_shell_context():
            return {"redis": redis}

    def load_settings(self):
        from artorias.flask.settings import DefaultSettings

        try:
            setting_module = importlib.import_module(f"{self.name}.settings")
            settings_obj: DefaultSettings = setting_module.settings
        except AttributeError:
            settings_path = Path(self.root_path) / "settings.py"
            self.logger.warning(f"Can't import settings from '{settings_path}', will use default settings.")
            settings_obj = DefaultSettings()

        self.settings = settings_obj
        self.config.from_mapping(settings_obj.model_dump())

        if self.debug:
            print(" Project Config ".center(80, "#"))
            print(settings_obj.model_dump_json(indent=4))

    def load_blueprints(self):
        blueprints_package = f"{os.path.basename(self.root_path)}.apis"
        for blueprint in find_blueprints(blueprints_package):
            self.logger.debug(f"Found blueprint '{blueprint}'")
            self.register_blueprint(blueprint)

    def load_commands(self):
        commands_package = f"{os.path.basename(self.root_path)}.commands"
        for command in find_commands(commands_package):
            click_obj = typer.main.get_command(command)
            self.logger.debug(f"Found command '{click_obj}'")
            self.cli.add_command(click_obj, click_obj.name)

    def init_logger(self):
        self.logger.handlers.clear()
        self.logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        default_handler.setFormatter(logging.Formatter(self.config["LOGGER_FORMAT_STRING"]))
        self.logger.addHandler(default_handler)

        @self.before_request
        def log_request():
            content = f"{request.method} {unquote(request.full_path)}"
            if request.is_json:
                content += f" JSON: {request.json}"
            if request.form:
                content += f"FORM: {request.form}"
            self.logger.info(f"--> {content}")

        @self.after_request
        def log_response(resp: Response):
            self.logger.info(f"<-- {json.dumps(resp.json, ensure_ascii=False)} {resp.status_code}")
            self.logger.info("")
            return resp

    def load_error_handlers(self):
        @self.errorhandler(HTTPException)
        def http_exception(e: HTTPException):
            return APIException.from_http_exception(e).to_response()

        @self.errorhandler(APIException)
        def api_exception(e: APIException):
            return e.to_response()

        for error, handler in self.settings.CUSTOM_ERROR_HANDLERS.items():
            self.errorhandler(error)(handler)

        @self.errorhandler(Exception)
        def exception(e: Exception):
            self.logger.exception(e)
            return APIException.from_exception(e).to_response()
