from typing import Callable

from fastapi import Depends, FastAPI, Request, responses

from ._model import HealthResponse
from .checks import CheckInterface


class HealthCheck:
    def __init__(self, title: str, version: str, checks: list[type(CheckInterface)], depend: Callable):
        self.__title = title
        self.__version = version

        self.__checks = [
            check if isinstance(check, CheckInterface) else check()  # Instantiate if not
            for check in checks
        ]
        self.__depend = depend

    def init_health_check(self, app: FastAPI):
        def empty_depend():
            return None

        @app.get('/health', response_model=HealthResponse, tags=['Monitoring'])
        async def health(
            request: Request,
            session=Depends(self.__depend or empty_depend),
        ) -> responses.JSONResponse:
            checks = []
            kwargs = {'session': session, 'request': request}

            for check in self.__checks:
                checks.append(check.check(**kwargs))

            all_ok = all([check.ok for check in checks])
            response = HealthResponse(
                name=self.__title,
                version=self.__version,
                all_ok=all_ok,
                checks=checks,
            )

            return responses.JSONResponse(
                content=response.model_dump(),
                status_code=200 if all_ok else 500,
            )
