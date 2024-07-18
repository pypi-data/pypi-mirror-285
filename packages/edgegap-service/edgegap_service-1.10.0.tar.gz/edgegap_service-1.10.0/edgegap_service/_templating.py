import os

from fastapi import templating

from ._configuration import ServiceConfiguration


class TemplateRenderer:
    __templates: templating.Jinja2Templates | None = None

    @classmethod
    def get_templates(cls, configuration: ServiceConfiguration = None) -> templating.Jinja2Templates:
        if isinstance(configuration, ServiceConfiguration) and cls.__templates is None:
            static_folder = os.path.join(configuration.root_dir, configuration.static_dir)
            cls.__templates = templating.Jinja2Templates(directory=static_folder)

        if not isinstance(cls.__templates, templating.Jinja2Templates):
            raise Exception(
                'Templating is not a Jinja2Templates instance, please pass a valid ServiceConfiguration first',
            )

        return cls.__templates

    @classmethod
    def depends_templates(cls) -> templating.Jinja2Templates:
        return cls.get_templates()

    @classmethod
    def clear_templates(cls) -> None:
        cls.__templates = None
