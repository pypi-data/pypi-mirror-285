""" Error response when no permissions """

from pydantic import BaseModel

__all__ = ["NxtForbiddenResponse"]


class NxtForbiddenResponse(BaseModel):
    message: str
