from fastapi import FastAPI, Request, responses, templating


class DocumentationRoute:
    @staticmethod
    def init_documentation(app: FastAPI, file_name: str, templates: templating.Jinja2Templates):
        @app.get('/', response_class=responses.HTMLResponse, include_in_schema=False)
        async def root(request: Request):
            urls = {
                'Docs': f'{request.base_url}docs',
                'Redoc': f'{request.base_url}redoc',
            }

            return templates.TemplateResponse(
                name=file_name,
                context={
                    'request': request,
                    'urls': urls,
                    'title': getattr(app, 'title'),
                },
            )
