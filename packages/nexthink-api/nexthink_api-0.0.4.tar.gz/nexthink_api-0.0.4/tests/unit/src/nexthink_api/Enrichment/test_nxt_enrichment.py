"""Unit test file for nexthink_api"""
import json
from typing import Iterator
from pydantic import ValidationError
import pytest


from nexthink_api import NxtIdentification, NxtIdentificationName, NxtField, NxtFieldName, NxtEnrichment


class TestNxtEnrichment:

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

    #  NxtEnrichment object can be created with valid identification and fields
    def test_valid_identification_and_fields(self, value_iter):
        identification = [NxtIdentification(name=NxtIdentificationName.BINARY_BINARY_UID, value=next(value_iter))]
        fields = [NxtField(name=NxtFieldName.ENVIRONMENT_NAME, value=next(value_iter))]
        nxt_enrichment = NxtEnrichment(identification=identification, fields=fields)
        assert nxt_enrichment.identification == identification
        assert nxt_enrichment.fields == fields

    #  NxtEnrichment object can be serialized to JSON without errors
    def test_serialize_to_json_without_errors(self, value_iter):
        identification = [NxtIdentification(name=NxtIdentificationName.BINARY_BINARY_UID, value=next(value_iter))]
        fields = [NxtField(name=NxtFieldName.ENVIRONMENT_NAME, value=next(value_iter))]
        nxt_enrichment = NxtEnrichment(identification=identification, fields=fields)

        try:
            json.loads(nxt_enrichment.model_dump_json())
        except Exception as e:
            pytest.fail(f"Serialization to JSON failed with error: {e}")

    #  NxtEnrichment object cannot be created without identification
    def test_missing_identification(self, value_iter):
        fields = [NxtField(name=NxtFieldName.ENVIRONMENT_NAME, value=next(value_iter))]

        with pytest.raises(ValidationError):
            NxtEnrichment(identification=[], fields=fields)

    #  NxtEnrichment object cannot be created without fields
    def test_missing_fields(self, value_iter):
        identification = [NxtIdentification(name=NxtIdentificationName.BINARY_BINARY_UID, value=next(value_iter))]
        with pytest.raises(ValidationError):
            NxtEnrichment(identification=identification, fields=[])

    #  NxtEnrichment object cannot have more than one identification
    def test_multiple_identifications(self, value_iter):
        identification1 = [NxtIdentification(name=NxtIdentificationName.BINARY_BINARY_UID, value=next(value_iter))]
        identification2 = [NxtIdentification(name=NxtIdentificationName.USER_USER_SID, value=next(value_iter))]
        fields = [NxtField(name=NxtFieldName.ENVIRONMENT_NAME, value=next(value_iter))]
        with pytest.raises(ValidationError):
            NxtEnrichment(identification=[identification1, identification2], fields=fields)

    def test_multiple_fields(self, value_iter):
        identification = [NxtIdentification(name=NxtIdentificationName.BINARY_BINARY_UID, value=next(value_iter))]
        fields = [
            NxtField(name=NxtFieldName.ENVIRONMENT_NAME, value=next(value_iter)),
            NxtField(name=NxtFieldName.DISK_IMAGE, value=next(value_iter))
        ]
        nxt_enrichment = NxtEnrichment(identification=identification, fields=fields)
        assert nxt_enrichment.identification == identification
        assert nxt_enrichment.fields == fields
        assert len(nxt_enrichment.fields) == 2

        #  NxtEnrichment object can have custom field names with custom values
    def test_custom_field_names(self, value_iter):
        identification = [NxtIdentification(name=NxtIdentificationName.DEVICE_DEVICE_NAME,
                                            value=next(value_iter),
                                            customValue=next(value_iter))]
        fields = [NxtField(name=NxtFieldName.ENVIRONMENT_NAME, value=next(value_iter))]
        nxt_enrichment = NxtEnrichment(identification=identification, fields=fields)
        assert nxt_enrichment.identification == identification
        assert nxt_enrichment.fields == fields
