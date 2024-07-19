import logging
import logging.config

import dotenv

# "DEBUG" if dotenv.dotenv_values().get("DEV_MODE", 0) else "INFO"

_loggerConfig = {  # type: ignore
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "basic": {"format": "%(levelname)s - [%(module)s - %(lineno)d]: %(message)s"},
    },
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "formatter": "basic",
            "stream": "ext://sys.stderr",
        }
    },
    "loggers": {
        "root": {
            "level": "DEBUG" if dotenv.dotenv_values().get("DEV_MODE") == "TRUE" else "INFO",
            "handlers": ["stderr"],
        }
    },
}

logging.config.dictConfig(config=_loggerConfig)

LOGGER = logging.getLogger("kancolatex")
