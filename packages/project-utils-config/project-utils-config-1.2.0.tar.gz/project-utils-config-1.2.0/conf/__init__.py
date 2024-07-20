from .config import Config

config = CONFIG = Config.create_config(__file__)

__all__ = [
    "config",
    "CONFIG",
    "Config"
]
