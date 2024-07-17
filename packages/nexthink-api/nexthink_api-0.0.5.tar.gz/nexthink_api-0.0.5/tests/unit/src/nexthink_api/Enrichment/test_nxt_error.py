"""Unit test file for nexthink_api"""
from typing import Iterator
import pytest

from nexthink_api import (
    NxtError,
)


class TestNxtError:

    # test value generator
    @staticmethod
    def value_generator() -> Iterator[str]:
        counter = 1
        while True:
            for suffix in ['a', 'b', 'c', 'd', 'e', 'f']:
                yield f"test{counter}-{suffix}"
            counter += 1

    # Fixture to use to generate test values
    @pytest.fixture
    def value_iter(self) -> Iterator[str]:
        return self.value_generator()

    #  Create an instance with valid message and code
    def test_create_instance_with_valid_data(self, value_iter):
        message = next(value_iter)
        code = next(value_iter)
        error = NxtError(message=message, code=code)
        assert error.message == message
        assert error.code == code

    #  Attempt to create an instance with an empty message string
    def test_empty_message_string(self, value_iter):
        code = next(value_iter)
        with pytest.raises(ValueError):
            NxtError(message="", code=code)

    #  Attempt to create an instance with an empty code string
    def test_empty_code_string(self, value_iter):
        message = next(value_iter)
        with pytest.raises(ValueError):
            NxtError(message=message, code="")

    #  Attempt to create an instance with a code as int
    def test_int_code(self, value_iter):
        message = next(value_iter)
        with pytest.raises(ValueError):
            NxtError(message=message, code=5)
