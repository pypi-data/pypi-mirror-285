""" Authentication request on the Nexthink API """

from typing import Dict
from pydantic import BaseModel, Field

__all__ = ["NxtTokenRequest"]


class NxtTokenRequest(BaseModel):
    data: Dict[str, str] = Field(default={'grant_type': 'client_credentials'}, frozen=True)

    def dict(self, *arg, **kwargs):
        return self.data

    def model_dump(self, *arg, **kwargs):
        return self.data
