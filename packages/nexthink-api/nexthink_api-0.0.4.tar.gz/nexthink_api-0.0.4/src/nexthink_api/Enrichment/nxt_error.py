""" An error composed of a message and a code """

from pydantic import BaseModel, Field

__all__ = ["NxtError"]


class NxtError(BaseModel):
    message: str = Field(min_length=1)
    code: str = Field(min_length=1)
