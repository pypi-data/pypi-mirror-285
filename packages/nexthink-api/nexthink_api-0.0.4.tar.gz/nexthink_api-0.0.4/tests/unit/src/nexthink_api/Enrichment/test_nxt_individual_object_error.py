"""Unit test file for nexthink_api"""
from typing import Iterator
from pydantic import ValidationError
import pytest

from nexthink_api import (
    NxtIndividualObjectError,
    NxtIdentification,
    NxtIdentificationName,
    NxtError,
)


class TestNxtIndividualObjectError:

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

    #  Validate successful creation with exactly one identification and multiple errors
    def test_good_creation(self, value_iter):
        v1 = next(value_iter)
        message1 = next(value_iter)
        code1 = next(value_iter)
        message2 = next(value_iter)
        code2 = next(value_iter)
        identification = [NxtIdentification(name=NxtIdentificationName.DEVICE_DEVICE_NAME, value=v1)]
        errors = [NxtError(message=message1, code=code1), NxtError(message=message2, code=code2)]
        obj = NxtIndividualObjectError(identification=identification, errors=errors)
        assert len(obj.identification) == 1
        assert len(obj.errors) == 2
        assert obj.errors[0].message == message1  # pylint: disable=unsubscriptable-object
        assert obj.errors[0].code == code1  # pylint: disable=unsubscriptable-object
        assert obj.errors[1].message == message2  # pylint: disable=unsubscriptable-object
        assert obj.errors[1].code == code2  # pylint: disable=unsubscriptable-object
        # pylint: disable=unsubscriptable-object
        assert obj.identification[0].name == NxtIdentificationName.DEVICE_DEVICE_NAME
        assert obj.identification[0].value == v1  # pylint: disable=unsubscriptable-object

    #  Validate successful creation with exactly one identification and one error
    def test_successful_creation_one_identification_one_error(self, value_iter):
        v1 = next(value_iter)
        message1 = next(value_iter)
        code1 = next(value_iter)
        identification = [NxtIdentification(name=NxtIdentificationName.DEVICE_DEVICE_NAME, value=v1)]
        errors = [NxtError(message=message1, code=code1)]
        obj = NxtIndividualObjectError(identification=identification, errors=errors)

        assert len(obj.identification) == 1
        assert len(obj.errors) == 1

    #  Attempt to create an instance with zero identifications
    def test_zero_identifications(self, value_iter):
        message1 = next(value_iter)
        code1 = next(value_iter)
        with pytest.raises(ValidationError):
            NxtIndividualObjectError(identification=[], errors=[NxtError(message=message1, code=code1)])

    #  Attempt to create an instance with more than one identification
    def test_more_than_one_identification(self, value_iter):
        v1 = next(value_iter)
        v2 = next(value_iter)
        message1 = next(value_iter)
        code1 = next(value_iter)
        identifications = [NxtIdentification(name=NxtIdentificationName.DEVICE_DEVICE_NAME, value=v1),
                           NxtIdentification(name=NxtIdentificationName.USER_USER_SID, value=v2)]
        errors = [NxtError(message=message1, code=code1)]

        with pytest.raises(ValidationError):
            NxtIndividualObjectError(identification=identifications, errors=errors)

    #  Attempt to create an instance with zero errors
    def test_zero_errors(self, value_iter):
        v1 = next(value_iter)
        identification = [NxtIdentification(name=NxtIdentificationName.DEVICE_DEVICE_NAME, value=v1)]

        with pytest.raises(ValidationError):
            NxtIndividualObjectError(identification=identification, errors=[])
