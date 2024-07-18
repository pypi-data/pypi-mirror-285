import asyncio
import inspect
import logging
import os
from logging.config import dictConfig
from pathlib import Path

from edgegap_logging import Color, Format
from edgegap_scheduling import Scheduler
from edgegap_settings import ProjectBaseSettings
from elasticapm.contrib import starlette
from fastapi import FastAPI, staticfiles, templating

from ._configuration import ServiceConfiguration
from ._documentation import DocumentationRoute
from ._scheduling import SchedulingAPI
from ._templating import TemplateRenderer
from .health import HealthCheck

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


class ServiceFactory:
    def __init__(self, configuration: ServiceConfiguration) -> None:
        self.__configuration = configuration
        self.__static_folder = os.path.join(self.__configuration.root_dir, self.__configuration.static_dir)
        self.__logger: logging.Logger | None = None
        self.__app: FastAPI = None

    def create_app(self) -> FastAPI:
        self.__app = FastAPI(
            title=self.__configuration.name,
            description=self.__configuration.description,
            configuration=self.__configuration,
            openapi_tags=self.__configuration.tags_definition,
        )

        Path(self.__static_folder).mkdir(parents=True, exist_ok=True)

        for router in self.__configuration.routers:
            self.__app.include_router(router)

        for exception_class, handler in self.__configuration.exception_handlers:
            self.__app.add_exception_handler(exception_class, handler)

        self.__app.mount(
            '/static',
            staticfiles.StaticFiles(
                directory=self.__static_folder,
                packages=[('edgegap_service', 'static')],
            ),
            name='static',
        )

        self.__logger = self.__init_logging()

        service_string = f'{self.__configuration.name} ({self.__configuration.version})'
        self.__logger.info(
            f'Service {Format.squared(service_string, Color.GREEN)} is initializing',
        )

        self.__init_root()
        self.__init_health()
        self.__init_template_renderer()
        self.__init_apm()
        self.__init_startup_functions()
        self.__init_scheduling()
        self.__init_sigterm()

        return self.__app

    def __init_root(self):
        folder = os.path.join(current_dir, 'static', 'html')
        file_name = 'index.html'
        is_defined = isinstance(self.__configuration.html_index_path, str)

        if is_defined:
            full_path = os.path.join(self.__configuration.root_dir, self.__configuration.html_index_path)

            if os.path.isfile(full_path):
                folder = os.path.dirname(full_path)
                file_name = os.path.basename(full_path)

        templates = templating.Jinja2Templates(directory=folder)
        DocumentationRoute.init_documentation(self.__app, file_name, templates)
        self.__logger.info(
            f'Initialized root path and documentation with folder: {Format.squared(folder, Color.GREEN)}',
        )

    def __init_health(self):
        health_check = HealthCheck(
            title=self.__configuration.name,
            version=self.__configuration.version,
            checks=self.__configuration.checks,
            depend=self.__configuration.depend,
        )
        health_check.init_health_check(self.__app)

        self.__logger.info(f"Initialized Health route at {Format.squared('/health', Color.GREEN)}")

    def __init_template_renderer(self):
        assert isinstance(
            TemplateRenderer.get_templates(configuration=self.__configuration),
            templating.Jinja2Templates,
        )
        self.__logger.info('Initialized Template Renderer')

    def __init_logging(self) -> logging.Logger:
        self.__init_logstash()

        dictConfig(self.__configuration.log_config.model_dump())
        logger = logging.getLogger(self.__configuration.name)
        logger.info(f'Logging for service {Format.squared(self.__configuration.name, Color.GREEN)} is configured')

        if (
            isinstance(self.__configuration.settings, ProjectBaseSettings)
            and self.__configuration.settings.logstash.enabled
        ):
            logger.info('Logstash is enabled')

        return logger

    def __init_apm(self):
        if isinstance(self.__configuration.settings, ProjectBaseSettings):
            apm = self.__configuration.settings.apm

            if apm.enabled:
                self.__logger.info('Apm is enabled')
                client = starlette.make_apm_client({
                    'SERVICE_NAME': self.__configuration.name,
                    'SECRET_TOKEN': apm.token,
                    'SERVER_URL': f'{apm.scheme}://{apm.server}:{apm.port}',
                })
                data = {
                    'middleware_class': starlette.ElasticAPM,
                    'client': client,
                }
                self.__app.add_middleware(**data)

    def __init_logstash(self):
        if isinstance(self.__configuration.settings, ProjectBaseSettings):
            logstash = self.__configuration.settings.logstash

            if logstash.enabled:
                formatter = {
                    'logstash': {
                        'class': 'logstash_async.formatter.LogstashFormatter',
                        'fmt': self.__configuration.env_config.log_format,
                    },
                }
                handlers = {
                    'logstash': {
                        'class': 'logstash_async.handler.AsynchronousLogstashHandler',
                        'formatter': 'logstash',
                        'transport': 'logstash_async.transport.TcpTransport',
                        'args': "('%(host)s', %(port)s, '%(database_path)s', '%(transport)s', "
                        "%(ssl_enable)s, %(ssl_verify)s, '%(keyfile)s', '%(certfile)s', "
                        "'%(ca_certs)s', %(enable)s)",
                        'host': logstash.server,
                        'port': logstash.port,
                        'enable': logstash.enabled,
                        'ssl_enable': False,
                        'ssl_verify': False,
                        'database_path': None,
                    },
                }
                self.__configuration.log_config.root['handlers'] = ['default', 'logstash']
                self.__configuration.log_config.loggers['root']['handlers'] = ['default', 'logstash']
                self.__configuration.log_config.formatters.update(formatter)
                self.__configuration.log_config.handlers.update(handlers)

    def __init_scheduling(self):
        if isinstance(self.__configuration.scheduler, Scheduler):

            @self.__app.on_event('startup')
            def start_scheduling():
                SchedulingAPI().init_scheduling_api(self.__app)
                asyncio.create_task(self.__configuration.scheduler.start_all())

    def __init_sigterm(self):
        @self.__app.on_event('shutdown')
        async def handle():
            try:
                self.__logger.info(f'Shutting down {Format.squared(self.__configuration.name, Color.GREEN)}')

                if isinstance(self.__configuration.scheduler, Scheduler):
                    asyncio.ensure_future(self.__configuration.scheduler.stop_all())
            except Exception as e:
                self.__logger.exception(f'Exception while shutting down: {e}')

            for func in self.__configuration.shutdown_functions:
                try:
                    if inspect.iscoroutinefunction(func):
                        await func()
                    else:
                        func()
                except Exception as e:
                    self.__logger.exception(f'Could not shutdown correctly one of the shutdown functions: {e}')

    def __init_startup_functions(self):
        @self.__app.on_event('startup')
        async def init_startup_functions():
            for func in self.__configuration.startup_functions:
                try:
                    if inspect.iscoroutinefunction(func):
                        await func()
                    else:
                        func()
                except Exception as e:
                    self.__logger.exception(f'Could not initialize correctly one of the startup functions: {e}')
