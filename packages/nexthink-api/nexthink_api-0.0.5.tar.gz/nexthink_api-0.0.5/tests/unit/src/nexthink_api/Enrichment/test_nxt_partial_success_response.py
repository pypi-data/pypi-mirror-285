"""Unit test file for nexthink_api"""
from typing import Iterator
from pydantic import ValidationError
import pytest

from nexthink_api import (
    NxtPartialSuccessResponse,
    NxtIndividualObjectError,
    NxtError,
    NxtIdentification,
    NxtIdentificationName
)


class TestNxtPartialSuccessResponse:

    # test value generator
    @staticmethod
    def value_generator() -> Iterator[str]:
        counter = 1
        while True:
            for suffix in ['a', 'b', 'c', 'd', 'e', 'f']:
                yield f"test{counter}-{suffix}"
            counter += 1

    # Fixture to use the value generator
    @pytest.fixture
    def value_iter(self) -> Iterator[str]:
        return self.value_generator()

    #  instantiate valide response
    def test_valid_instantiation(self, value_iter):
        value = next(value_iter)
        message = next(value_iter)
        code = next(value_iter)
        identifications = [NxtIdentification(name=NxtIdentificationName.DEVICE_DEVICE_NAME, value=value)]
        error = [NxtError(message=message, code=code)]
        errors = [NxtIndividualObjectError(identification=identifications, errors=error)]
        response = NxtPartialSuccessResponse(errors=errors)
        assert len(response.errors) == 1
        assert response.status == "partial_success"

    #  Attempt instantiation with an empty errors list and expect validation failure
    def test_empty_errors_list_validation_failure(self):
        with pytest.raises(ValidationError):
            NxtPartialSuccessResponse(errors=[])
