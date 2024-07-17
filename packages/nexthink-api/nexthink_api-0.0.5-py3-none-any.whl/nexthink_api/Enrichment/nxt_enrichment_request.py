""" Objects to be enriched (with desired fields and values) and domain (configurable) """

from pydantic import BaseModel, conlist, Field

from .nxt_enrichment import NxtEnrichment

__all__ = ["NxtEnrichmentRequest", "NxtEnrichment"]


class NxtEnrichmentRequest(BaseModel):
    enrichments: conlist(NxtEnrichment, min_length=1, max_length=5000)
    domain: str = Field(min_length=1)
