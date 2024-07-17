"""Unit test file for nexthink_api"""
from pydantic import ValidationError
import pytest

from nexthink_api import NxtIdentification, NxtIdentificationName


class TestNxtIdentification:
    """
        Test the correspondence between the values obtained from an enum and a YAML file list.
        :param get_identification_name_from_yaml: A fixture that returns a list of Identification names from YAML file.
        """

    # Instance with valid parameters
    def test_NxtIdentification1(self):
        f = NxtIdentification(name=NxtIdentificationName.DEVICE_DEVICE_NAME, value="test1")
        assert f.name.value == NxtIdentificationName.DEVICE_DEVICE_NAME.value
        assert f.value == "test1"

    # Instance with invalid parameters for name (not in Enum
    def test_NxtIdentificationNameUnknownString(self):
        with pytest.raises(ValidationError):
            NxtIdentification(name="unknownString", value="test2")

    # Instance with value not a string
    def test_NxtIdentificationValueNotString(self):
        with pytest.raises(ValidationError):
            NxtIdentification(name=NxtIdentificationName.BINARY_BINARY_UID, value=5)

    # Instance with empty value
    def test_NxtIdentificationValueEmptyString(self):
        with pytest.raises(ValidationError):
            NxtIdentification(name=NxtIdentificationName.BINARY_BINARY_UID, value="")

    # Instance with empty value
    def test_NxtIdentificationValueSpaceString(self):
        with pytest.raises(ValidationError):
            NxtIdentification(name=NxtIdentificationName.BINARY_BINARY_UID, value="   ")

        # Check if model_dump() method  works correctly with Enum
    def test_NxtIdentificationWithModelDump(self):
        f = NxtIdentification(name=NxtIdentificationName.BINARY_BINARY_UID, value="test6")
        assert (f.model_dump() == {"name": NxtIdentificationName.BINARY_BINARY_UID.value, "value": "test6"})
