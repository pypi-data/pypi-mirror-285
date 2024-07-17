""" Nexthink API Authentification answer """

from pydantic import BaseModel, Field

__all__ = ["NxtTokenResponse"]


class NxtTokenResponse(BaseModel):
    code: int = Field(default=0)
    description: str = Field(default="")
