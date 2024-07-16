"""Unit test file for nexthink_api"""
import pytest
from pydantic import ValidationError

from nexthink_api import NxtField, NxtFieldName


class TestNxtField:
    def test_NxtField1(self):
        f = NxtField(name=NxtFieldName.HYPERVISOR_NAME, value="test1")
        assert f.customValue is None
        assert f.name.value == NxtFieldName.HYPERVISOR_NAME.value
        assert f.value == "test1"

    def test_NxtField2(self):
        f = NxtField(name=NxtFieldName.CUSTOM_DEVICE, customValue="custom_value", value="test2")
        assert f.customValue == "custom_value"
        assert f.name.value == NxtFieldName.CUSTOM_DEVICE.value
        assert f.value == "test2"
        assert f.get_field_name(NxtFieldName.CUSTOM_DEVICE) == NxtFieldName.CUSTOM_DEVICE.value.format("custom_value")

    def test_NxtField3(self):
        with pytest.raises(ValidationError):
            NxtField(name=NxtFieldName.CUSTOM_DEVICE, value="test3")

    def test_NxtField4(self):
        with pytest.raises(ValidationError):
            NxtField(name=NxtFieldName.ENVIRONMENT_NAME, customValue="bad_custom_value", value="test4")

    def test_NxtFieldTypeParams1(self):
        with pytest.raises(ValidationError):
            str_val = NxtFieldName.ENVIRONMENT_NAME.value
            NxtField(name=str_val, value="test5")

    def test_NxtFieldTypeParams2(self):
        f = NxtField(name=NxtFieldName.HYPERVISOR_NAME, value=5)
        assert isinstance(f.value, int)
        assert f.value == 5

    def test_field_with_model_dump(self):
        f = NxtField(name=NxtFieldName.ENVIRONMENT_NAME, value="test6")
        assert f.model_dump() == {"name": NxtFieldName.ENVIRONMENT_NAME.value, "value": "test6"}
