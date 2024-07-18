from pydantic import BaseModel, Field


class CheckInstanceModel(BaseModel):
    ok: bool = Field(default=True, description='If the Check is OK')
    message: str = Field(default='ok', description='The message of the Check')


class CheckModel(CheckInstanceModel):
    name: str = Field(..., description='The name of the Check')
