""" NQL Status response for export request """

from typing import Optional
from pydantic import BaseModel, HttpUrl, field_serializer

from .nxt_nql_status import NxtNqlStatus

__all__ = ["NxtNqlApiStatusResponse"]


class NxtNqlApiStatusResponse(BaseModel):
    status: NxtNqlStatus
    resultsFileUrl: Optional[HttpUrl] = None
    errorDescription: Optional[str] = None

    @field_serializer('status', when_used='json')
    def serialize_status(self, value: NxtNqlStatus) -> str:
        return value.value
