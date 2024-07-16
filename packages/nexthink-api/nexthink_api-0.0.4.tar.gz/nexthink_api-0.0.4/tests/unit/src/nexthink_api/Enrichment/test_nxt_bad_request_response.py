"""Unit test file for nexthink_api"""
from typing import Iterator
from pydantic import ValidationError
import pytest

from nexthink_api import (
    NxtBadRequestResponse,
    NxtIndividualObjectError,
    NxtError,
    NxtIdentification,
    NxtIdentificationName
)


class TestNxtBadRequestResponse:

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

    # Instantiate with a single valid NxtIndividualObjectError
    def test_single_valid_error(self, value_iter):
        v1 = next(value_iter)
        message1 = next(value_iter)
        code1 = next(value_iter)
        identification = [NxtIdentification(name=NxtIdentificationName.DEVICE_DEVICE_NAME, value=v1)]
        errors = [NxtError(message=message1, code=code1)]
        objError = [NxtIndividualObjectError(identification=identification, errors=errors)]
        response = NxtBadRequestResponse(status="error", errors=objError)
        assert len(response.errors) == 1
        assert response.status == "error"

    #  Default status is set to 'error' when not explicitly provided
    def test_default_status_error(self, value_iter):
        v1 = next(value_iter)
        message1 = next(value_iter)
        code1 = next(value_iter)
        identification = [NxtIdentification(name=NxtIdentificationName.DEVICE_DEVICE_NAME, value=v1)]
        errors = [NxtError(message=message1, code=code1)]
        objError = [NxtIndividualObjectError(identification=identification, errors=errors)]
        response = NxtBadRequestResponse(errors=objError)
        assert len(response.errors) == 1
        assert response.status == "error"

    #  status should be 'error' if provided
    def test_bad_status_error(self, value_iter):
        v1 = next(value_iter)
        message1 = next(value_iter)
        code1 = next(value_iter)
        bad_status = next(value_iter)
        identification = [NxtIdentification(name=NxtIdentificationName.DEVICE_DEVICE_NAME, value=v1)]
        errors = [NxtError(message=message1, code=code1)]
        objError = [NxtIndividualObjectError(identification=identification, errors=errors)]
        with pytest.raises(ValidationError):
            # noinspection PyTypeChecker
            NxtBadRequestResponse(status=bad_status, errors=objError)

    #  Instantiate with multiple valid NxtIndividualObjectErrors
    def test_multiple_valid_errors(self, value_iter):
        v1 = next(value_iter)
        message1 = next(value_iter)
        code1 = next(value_iter)
        identification = [NxtIdentification(name=NxtIdentificationName.DEVICE_DEVICE_NAME, value=v1)]
        errors = [NxtError(message=message1, code=code1)]
        objErrors = [NxtIndividualObjectError(identification=identification, errors=errors)] * 5
        response = NxtBadRequestResponse(errors=objErrors)
        assert len(response.errors) == 5
        assert response.status == "error"

    #  Instantiate with an empty list of NxtIndividualObjectErrors
    def test_empty_error_list(self):
        with pytest.raises(ValidationError):
            NxtBadRequestResponse(errors=[])

    #  Instantiate with a list containing non-NxtIndividualObjectError items
    def test_non_individual_object_error_items(self):
        with pytest.raises(ValidationError):
            NxtBadRequestResponse(errors=["not_an_error_object"])
