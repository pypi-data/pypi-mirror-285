from typing import Any

from pydantic import BaseModel, Field
from pydantic_core import PydanticUndefined


class SourceValue(BaseModel):
    key: str = Field(..., description='The key of the value')
    value: Any = Field(..., description='The value')
    default: Any = Field(..., description='The default value')
    source: str = Field(..., description='The source of the value')
    exists: bool = Field(default=False, description='Whether the value exists in the source')

    @property
    def has_value(self) -> bool:
        return self.value is not None

    @property
    def has_default(self) -> bool:
        return self.default not in (None, PydanticUndefined)
