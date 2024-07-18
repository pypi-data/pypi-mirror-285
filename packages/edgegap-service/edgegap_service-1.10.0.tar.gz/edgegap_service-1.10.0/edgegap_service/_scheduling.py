from edgegap_scheduling import SchedulingSingleton, Task, errors
from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRouter
from pydantic import BaseModel, Field


class TaskParameters(BaseModel):
    parameters: dict | None = Field(default=None, description='The parameters to update in the tasks')


class UpdateTask(TaskParameters):
    every: str | None = Field(default=None, description='The interval to run the Task')
    delay: str | None = Field(default=None, description='Delay before starting the Task')


class SchedulingAPI:
    tags = ['Scheduling']

    def __init__(self):
        self.__instance = SchedulingSingleton.scheduler()

    def init_scheduling_api(self, app: FastAPI):
        router = APIRouter(prefix='/scheduling/tasks', tags=self.tags)

        @router.get('/', description='Get all Tasks')
        async def get_tasks() -> list[Task]:
            return await self.__instance.list()

        @router.get('/{identifier}', description='Get One Task')
        async def get_task(identifier: str) -> Task:
            try:
                return await self.__instance.get(identifier)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

        @router.post('/{identifier}', description='Start a stopped Task')
        async def start_task(identifier: str) -> Task:
            try:
                return await self.__instance.start(identifier)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

        @router.patch('/{identifier}', description='Update the Interval of a Task')
        async def update_task(identifier: str, task: UpdateTask) -> Task:
            try:
                return await self.__instance.update(
                    identifier=identifier,
                    every=task.every,
                    delay=task.delay,
                    parameters=task.parameters,
                )
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

        @router.delete('/{identifier}', description='Stop a running Task')
        async def stop_task(identifier: str) -> Task:
            try:
                return await self.__instance.stop(identifier)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

        @router.post('/run/{identifier}')
        async def run_rask(identifier: str, task_parameters: TaskParameters | None) -> Task:
            try:
                params = task_parameters.parameters if task_parameters else None
                return await self.__instance.run(identifier, params)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except errors.ManualRunNotAllowedError as e:
                raise HTTPException(status_code=403, detail=str(e))

        app.include_router(router)
