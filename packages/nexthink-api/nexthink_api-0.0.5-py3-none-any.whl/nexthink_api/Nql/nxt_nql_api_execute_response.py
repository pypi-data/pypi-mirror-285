""" NQL class answer object for V1 request """

from pydantic import BaseModel, NonNegativeInt

from .nxt_date_time import NxtDateTime

__all__ = ["NxtNqlApiExecuteResponse"]


class NxtNqlApiExecuteResponse(BaseModel):
    queryId: str
    executedQuery: str
    rows: NonNegativeInt
    executionDateTime: NxtDateTime
    headers: list[str]
    data: list[list]
