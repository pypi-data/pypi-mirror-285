import os
from typing import Callable, Optional, TypeVar

from edgegap_scheduling import Scheduler
from edgegap_settings import ProjectBaseSettings, SettingsFactory
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings
from starlette.types import ExceptionHandler

from ._environment import EnvironmentConfiguration
from .health.checks import CheckInterface
from .logging import LoggingConfiguration

Exc = TypeVar('Exc', bound=Exception)


def get_default_root_dir() -> str:
    return os.getenv("EDGEGAP_SERVICE_ROOT_DIR") or os.getcwd()


class ServiceConfiguration(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str = Field(..., description='The name of the Service')
    version: str = Field(..., description='The version of the Service')
    description: str = Field(..., description='The description of the Service')
    routers: list[APIRouter] = Field([], description='The FastAPI routers')
    exception_handlers: list[tuple[type[Exc], ExceptionHandler]] = Field(
        default_factory=list,
        description='The Exception Handlers to add to the FastAPI App',
    )
    root_dir: str = Field(default_factory=get_default_root_dir, description='The Root Directory of the Service')
    static_dir: str = Field(default='static', description='The Static Directory of the Service')
    html_index_path: str | None = Field(default=None, description='The full path to the html index file')
    checks: list[type(CheckInterface)] = Field([], description='The list of Checks to run on the Service')
    depend: Optional[Callable] = Field(default=None, description='The Base Depend Attribute for DB Session')
    port: int = Field(default=8000, description='The Port of the Service')
    host: str = Field(default='0.0.0.0', description='The Host of the Service')
    workers: int = Field(default=1, description='Numbers of Workers, (if you use the scheduler, keep to 1)')
    timeout: int = Field(default=300, description='Default Timeout for Connection')
    worker_class: str = Field(default='uvicorn.workers.UvicornWorker', description='The worker class for ASGI')
    scheduler: Scheduler | None = Field(default=None, description='A Scheduler to start at boot')
    startup_functions: list[Callable] = Field(default=[], description='All function will be called on startup')
    shutdown_functions: list[Callable] = Field(default=[], description='All function will be called on shutdown')
    env_config: EnvironmentConfiguration = Field(
        default=SettingsFactory.from_settings(EnvironmentConfiguration),
        description='The Configuration coming from the Environment Variables',
    )
    log_config: LoggingConfiguration = Field(
        default=LoggingConfiguration(),
        description='The Configuration for the Logging, will be passed as DictConfig to Python logging system',
    )
    settings: ProjectBaseSettings | BaseSettings | None = Field(
        default=None,
        description='Project Specific Settings to hold in the Service',
    )
    tags_definition: list[dict] = Field(
        default=[],
        description='See https://fastapi.tiangolo.com/tutorial/metadata/#use-your-tags for details',
    )
