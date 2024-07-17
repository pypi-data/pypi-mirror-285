"""Unit test file for nexthink_api"""
from typing import Iterator
from pydantic import ValidationError
import pytest


from nexthink_api import (NxtEnrichmentRequest,
                          NxtIdentification,
                          NxtIdentificationName,
                          NxtField,
                          NxtFieldName,
                          NxtEnrichment,
                          )


class TestNxtEnrichmentRequest:

    @staticmethod
    def value_generator() -> Iterator[str]:
        counter = 1
        while True:
            for suffix in ['a', 'b', 'c', 'd', 'e', 'f']:
                yield f"test{counter}-{suffix}"
            counter += 1

    @pytest.fixture
    def value_iter(self) -> Iterator[str]:
        return self.value_generator()

    #  Validate that the class accepts a list of 1 to 5000 NxtEnrichment objects
    def test_accepts_valid_enrichment_range(self, value_iter):
        # working values
        ident = [NxtIdentification(name=NxtIdentificationName.BINARY_BINARY_UID, value=next(value_iter))]
        f = [NxtField(name=NxtFieldName.ENVIRONMENT_NAME, value=next(value_iter))]

        # test for 1 to 5000
        enrichments = [NxtEnrichment(identification=ident, fields=f)]
        request = NxtEnrichmentRequest(enrichments=enrichments, domain="test.com")
        assert len(request.enrichments) == 1

        enrichments = enrichments * 1000
        request = NxtEnrichmentRequest(enrichments=enrichments, domain="test.com")
        assert len(request.enrichments) == 1000

        enrichments = enrichments * 5
        request = NxtEnrichmentRequest(enrichments=enrichments, domain="test.com")
        assert len(request.enrichments) == 5000

    # test for 0 and 5001
    def test_bounds_enrichment_range(self, value_iter):
        # working values
        ident = [NxtIdentification(name=NxtIdentificationName.BINARY_BINARY_UID, value=next(value_iter))]
        f = [NxtField(name=NxtFieldName.ENVIRONMENT_NAME, value=next(value_iter))]
        enrichments = [NxtEnrichment(identification=ident, fields=f)]

        # test for 0
        with pytest.raises(ValidationError):
            NxtEnrichmentRequest(enrichments=[], domain="test.com")

        enrichments = enrichments * 5001
        with pytest.raises(ValidationError):
            NxtEnrichmentRequest(enrichments=enrichments, domain="test.com")

    #  Ensure that the domain field accepts a non-empty string
    def test_domain_accepts_non_empty_string(self, value_iter):
        # working values
        ident = [NxtIdentification(name=NxtIdentificationName.BINARY_BINARY_UID, value=next(value_iter))]
        f = [NxtField(name=NxtFieldName.ENVIRONMENT_NAME, value=next(value_iter))]
        enrichments = [NxtEnrichment(identification=ident, fields=f)]

        request = NxtEnrichmentRequest(enrichments=enrichments, domain="test.com")
        assert request.domain == "test.com"

    #  Attempt to initialize with an empty string for the domain field
    def test_empty_domain_field(self, value_iter):
        # working values
        ident = [NxtIdentification(name=NxtIdentificationName.BINARY_BINARY_UID, value=next(value_iter))]
        f = [NxtField(name=NxtFieldName.ENVIRONMENT_NAME, value=next(value_iter))]
        enrichments = [NxtEnrichment(identification=ident, fields=f)]

        with pytest.raises(ValueError):
            NxtEnrichmentRequest(enrichments=enrichments, domain="")
