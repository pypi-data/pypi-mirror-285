from pydantic import BaseModel, ConfigDict


class BaseModelForbidExtra(BaseModel):
    model_config = ConfigDict(extra="forbid")
