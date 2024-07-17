"""Unit test file for nexthink_api"""
import pytest
from pydantic import ValidationError

from nexthink_api import NxtNqlApiExportResponse


class TestNxtNqlApiExportResponse:

    #  valid exportId is correctly assigned
    def test_valid_export_id_assigned(self):
        response = NxtNqlApiExportResponse(exportId="validExportId123")
        assert response.exportId == "validExportId123"

    #  exportId is a non-empty string
    def test_export_id_non_empty_string(self):
        with pytest.raises(ValidationError):
            NxtNqlApiExportResponse(exportId="")

    #  exportId is None
    def test_export_id_none(self):
        with pytest.raises(ValidationError):
            NxtNqlApiExportResponse(exportId=None)

    #  exportId contains special characters
    def test_export_id_special_characters(self):
        response = NxtNqlApiExportResponse(exportId="exp!@#123")
        assert response.exportId == "exp!@#123"

    #  exportId is a very long string
    def test_export_id_very_long_string(self):
        long_string = "a" * 1000
        response = NxtNqlApiExportResponse(exportId=long_string)
        assert response.exportId == long_string

    #  exportId is invalid type
    def test_export_id_invalid_type(self):
        with pytest.raises(ValidationError):
            NxtNqlApiExportResponse(exportId=123)
