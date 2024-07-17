"""Unit test file for nexthink_api"""
from nexthink_api import NxtErrorResponse


class TestNxtErrorResponse:

    #  successfully create an instance with valid message, code, and source
    def test_create_instance_with_valid_data(self):
        response = NxtErrorResponse(message="Error occurred", code=400, source="Server")
        assert response.message == "Error occurred"
        assert response.code == 400
        assert response.source == "Server"

    #  handle empty string for source
    def test_empty_string_for_message(self):
        response = NxtErrorResponse(message="Error occurred", code=200, source="")
        assert response.source == ""

    #  handle negative integer for code
    def test_negative_integer_for_code(self):
        response = NxtErrorResponse(message="Negative code", code=-1, source="Server")
        assert response.code == -1

    # test no value source provided
    def test_no_source_value_provided(self):
        response = NxtErrorResponse(message="message", code=403)
        assert response.message == "message", "Not the expected value"
        assert response.code == 403, "Not the expected value"
        assert response.source is None, "Not the expected value"
