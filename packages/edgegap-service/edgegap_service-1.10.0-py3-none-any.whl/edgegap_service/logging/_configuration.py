from edgegap_settings import SettingsFactory
from pydantic import BaseModel

from .._environment import EnvironmentConfiguration

env_config: EnvironmentConfiguration = SettingsFactory.from_settings(EnvironmentConfiguration)


class LoggingConfiguration(BaseModel):
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        'default': {
            '()': 'edgegap_logging.DefaultFormatter',
            'fmt': env_config.log_format,
        },
        'access': {
            '()': 'edgegap_service.AccessFormatter',
            'fmt': env_config.log_access_format,
        },
    }
    handlers: dict = {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'access': {
            'formatter': 'access',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    }
    loggers: dict = {
        'root': {
            'handlers': ['default'],
            'level': env_config.log_level,
        },
        'uvicorn': {
            'handlers': ['default'],
            'level': env_config.log_level,
            'propagate': False,
        },
        'uvicorn.error': {
            'level': env_config.log_level,
        },
        'uvicorn.access': {
            'handlers': ['access'],
            'level': env_config.log_level,
            'propagate': False,
        },
        'gunicorn.error': {
            'level': env_config.log_level,
            'handlers': ['default'],
            'propagate': False,
        },
        'gunicorn.access': {
            'level': env_config.log_level,
            'handlers': ['access'],
            'propagate': False,
        },
        'elasticapm': {
            'level': 'INFO',
            'handlers': ['default'],
            'propagate': False,
        },
        'urllib3': {
            'level': 'INFO',
            'handlers': ['default'],
            'propagate': False,
        },
    }
    root: dict = {
        'level': env_config.log_level,
        'handlers': ['default'],
    }
