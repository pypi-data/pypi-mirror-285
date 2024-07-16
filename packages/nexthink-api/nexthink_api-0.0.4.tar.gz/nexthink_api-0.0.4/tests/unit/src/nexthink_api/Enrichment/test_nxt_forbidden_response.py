"""Unit test file for nexthink_api"""
from typing import Iterator
from pydantic import ValidationError
import pytest

from nexthink_api import (
    NxtForbiddenResponse,
)


class TestNxtForbiddenResponse:

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

    #  Instantiate NxtForbiddenResponse with a valid message string
    def test_instantiate_with_valid_message(self, value_iter):
        v1 = next(value_iter)
        response = NxtForbiddenResponse(message=v1)
        assert response.message == v1

    #  Access the message attribute after instantiation
    def test_access_message_attribute(self, value_iter):
        v1 = next(value_iter)
        v2 = next(value_iter)
        response = NxtForbiddenResponse(message=v1)
        response.message = v2
        assert response.message == v2

    #  Instantiate NxtForbiddenResponse with an empty string as message
    def test_instantiate_with_empty_message(self):
        response = NxtForbiddenResponse(message="")
        assert response.message == ""

    #  Instantiate NxtForbiddenResponse with a very long string as message
    def test_instantiate_with_long_message(self, value_iter):
        long_message = next(value_iter) * 10000  # very long string
        response = NxtForbiddenResponse(message=long_message)
        assert response.message == long_message

    #  Instantiate NxtForbiddenResponse with non-string types as message, expecting type errors
    def test_instantiate_with_non_string_types(self):
        with pytest.raises(ValidationError):
            NxtForbiddenResponse(message=123)
