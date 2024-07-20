from flask import Flask
from typing import Optional
from project_utils.conf import ConfigTemplate


def create_app(config: ConfigTemplate, import_name: str = __name__,
               static_url_path: Optional[str] = None,
               static_folder: str = "static") -> Flask:
    app: Flask = Flask(
        import_name=import_name,
        static_url_path=static_url_path,
        static_folder=static_folder
    )
    app.config.from_object(config)
    return app


def start(app: Flask, **kwargs):
    app.run(**kwargs)
