""" NQL request class object """

from typing import Annotated
from pydantic import BaseModel, Field


__all__ = ["NxtNqlApiExecuteRequest"]


class NxtNqlApiExecuteRequest(BaseModel):
    queryId: Annotated[
        str,
        Field(
            min_length=2,  # the sharp and at lest a character
            pattern=r'^#[a-z0-9_]{1,255}$'  # regex constraint
        )
    ]
    parameters: dict[str, str] = Field(default={})
