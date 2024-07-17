""" Datetime class object for NQL answer """

from datetime import datetime
from typing import Any, Self
from typing_extensions import Annotated
from pydantic import BaseModel, Field, field_validator, model_validator

__all__ = ["NxtDateTime"]


class NxtDateTime(BaseModel):
    year: Annotated[int, Field(strict=True)]
    month: Annotated[int, Field(strict=True, ge=1, le=12)]
    day: Annotated[int, Field(strict=True, ge=1, le=31)]
    hour: Annotated[int, Field(strict=True, ge=0, le=23)]
    minute: Annotated[int, Field(strict=True, ge=0, le=59)]
    second: Annotated[int, Field(strict=True, ge=0, le=59)]

    # noinspection PyNestedDecorators
    @field_validator('year', mode='before')
    @classmethod
    def validate_year(cls, value: Any):
        if value <= 99:
            value += 2000
        elif value > 9999:
            raise ValueError("Year must be either 2 digits or 4 digit number)")
        return value

    @model_validator(mode='after')
    def validate(self) -> Self:
        try:
            datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)
        except ValueError as e:
            raise ValueError(f'date parameters are not valid: {e}') from e
        return self
