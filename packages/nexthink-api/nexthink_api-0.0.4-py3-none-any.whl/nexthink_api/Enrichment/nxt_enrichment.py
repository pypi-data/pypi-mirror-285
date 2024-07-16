""" Class for fields to be enriched and values to be assigned """

from pydantic import BaseModel, conlist

from .nxt_identification import NxtIdentification
from .nxt_field import NxtField


__all__ = ["NxtEnrichment", "NxtIdentification", "NxtField"]


class NxtEnrichment(BaseModel):
    identification: conlist(NxtIdentification, min_length=1, max_length=1)
    fields: conlist(NxtField, min_length=1)
