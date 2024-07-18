from edgegap_settings import EnvironmentField
from pydantic_settings import BaseSettings


class EnvironmentConfiguration(BaseSettings):
    log_level: str = EnvironmentField(
        key='LOG_LEVEL',
        description='The logging Level',
        default='DEBUG',
    )

    log_format: str = EnvironmentField(
        key='LOG_FORMAT',
        description='The Logging Format',
        default='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    )

    log_access_format: str = EnvironmentField(
        key='LOG_ACCESS_FORMAT',
        description='The Logging Format for API Access',
        default='%(asctime)s | %(levelname)s | %(name)s | %(client_addr)s - [%(request_line)s] %(status_code)s',
    )
