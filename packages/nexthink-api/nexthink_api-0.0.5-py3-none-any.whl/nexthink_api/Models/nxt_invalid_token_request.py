""" Error when authentication has failed """

from pydantic import BaseModel, Field

__all__ = ["NxtInvalidTokenRequest"]


class NxtInvalidTokenRequest(BaseModel):
    code: str = Field(min_length=1, default=401)
    message: str = Field(min_length=1, default="Unauthorized - invalid authentication credentials")
