""" An error response for NQL request """

from typing import Optional
from pydantic import BaseModel

__all__ = ["NxtErrorResponse"]


class NxtErrorResponse(BaseModel):
    message: str
    code: int
    source: Optional[str] = None
