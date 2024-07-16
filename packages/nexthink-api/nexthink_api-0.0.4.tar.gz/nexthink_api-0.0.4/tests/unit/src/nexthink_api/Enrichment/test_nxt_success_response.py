"""Unit test file for nexthink_api"""
from typing import Iterator
from pydantic import ValidationError
import pytest

from nexthink_api import (
    NxtSuccessResponse,
)


class TestNxtSuccessResponse:

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

    #  Verify that the default status is 'success'
    def test_default_status_success(self):
        response = NxtSuccessResponse()
        assert response.status == "success"

    #  instantiate with an valid status value
    def test_valid_status_value(self):
        response = NxtSuccessResponse(status="success")
        assert response.status == "success"

    #  Attempt to set the status field to a value other than 'success' and expect a validation error
    def test_invalid_status_value(self):
        with pytest.raises(ValueError):
            NxtSuccessResponse(status="failure")

    #  Evaluate model's response to null input values
    def test_null_input_values(self):
        with pytest.raises(ValidationError):
            NxtSuccessResponse(status=None)
