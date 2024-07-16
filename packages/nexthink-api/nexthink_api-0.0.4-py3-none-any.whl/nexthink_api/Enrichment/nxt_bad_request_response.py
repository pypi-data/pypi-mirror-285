""" Error response when ALL objects in the request contain errors """

from typing import Literal
from pydantic import BaseModel, conlist, Field


from .nxt_individual_object_error import NxtIndividualObjectError

__all__ = ["NxtBadRequestResponse", "NxtIndividualObjectError"]


class NxtBadRequestResponse(BaseModel):
    status: Literal["error"] = Field(default="error")
    errors: conlist(NxtIndividualObjectError, min_length=1)
