from pydantic import BaseModel, Field

from .checks import CheckModel


class HealthResponse(BaseModel):
    name: str = Field(..., description='The name of the Service')
    version: str = Field(..., description='The Version of the Service')
    all_ok: bool = Field(..., description='If all checks are OK')
    checks: list[CheckModel] = Field(..., description='List of the Checks executed')
