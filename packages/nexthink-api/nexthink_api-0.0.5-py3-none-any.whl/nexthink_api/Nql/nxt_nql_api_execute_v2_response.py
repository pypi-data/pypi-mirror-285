""" NQL Class answer object for NQL request with V2 date format """

from datetime import datetime
from typing import List
from pydantic import BaseModel, field_validator

__all__ = ["NxtNqlApiExecuteV2Response"]


class NxtNqlApiExecuteV2Response(BaseModel):
    queryId: str
    executedQuery: str
    rows: int
    executionDateTime: str
    data: List[dict[str, str]]

    # Avoid pycharm false positive
    # noinspection PyNestedDecorators
    @field_validator('executionDateTime')
    @classmethod
    def parse_execution_datetime(cls, value):
        datetime.fromisoformat(value)
        return value
