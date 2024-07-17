""" Partial success response when some of the objects in the request contain errors but other objects are processed """

from typing import Literal
from pydantic import BaseModel, Field, conlist

from .nxt_individual_object_error import NxtIndividualObjectError

__all__ = ["NxtPartialSuccessResponse"]


# Note: NxtSuccessResponse already inherits from BaseModel
class NxtPartialSuccessResponse(BaseModel):
    status: Literal["partial_success"] = Field(default="partial_success")
    errors: conlist(NxtIndividualObjectError, min_length=1)
