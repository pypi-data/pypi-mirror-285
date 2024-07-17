"""Unit test file for nexthink_api"""
import pytest
from pydantic import HttpUrl

from nexthink_api import NxtNqlApiStatusResponse, NxtNqlStatus


class TestNxtNqlApiStatusResponse:

    #  valid status SUBMITTED is correctly assigned
    def test_valid_status_submitted(self):
        response = NxtNqlApiStatusResponse(status=NxtNqlStatus.SUBMITTED)
        assert response.status == NxtNqlStatus.SUBMITTED, "Status is not correctly affected"

    #  invalid status string raises validation error
    def test_invalid_status_string(self):
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            NxtNqlApiStatusResponse(status="INVALID_STATUS")

    # Test good URL for resultFileUrl
    def test_correct_url_format(self):
        url_value = "https://www.test.com/token/123456"
        response = NxtNqlApiStatusResponse(status=NxtNqlStatus.COMPLETED, resultsFileUrl=url_value)
        assert response.status == NxtNqlStatus.COMPLETED, "status is not correctly affected"
        assert str(response.resultsFileUrl) == url_value, "resultsFileUrl is not correctly affected"

    #  invalid URL format for resultsFileUrl raises validation error
    def test_invalid_url_format(self):
        with pytest.raises(ValueError):
            NxtNqlApiStatusResponse(status=NxtNqlStatus.COMPLETED, resultsFileUrl="invalid_url")

    #  both resultsFileUrl and errorDescription are None
    def test_both_resultsfileurl_and_errordescription_none(self):
        response = NxtNqlApiStatusResponse(status=NxtNqlStatus.SUBMITTED)
        assert response.resultsFileUrl is None, "default value should be None"
        assert response.errorDescription is None, "default value should be None"

    #  status is None raises validation error
    def test_status_none_raises_validation_error(self):
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            NxtNqlApiStatusResponse(status=None)

    # valie errorDescription affectation
    def test_error_description_affectation(self):
        value = "test1"
        response = NxtNqlApiStatusResponse(status=NxtNqlStatus.COMPLETED, errorDescription=value)
        assert response.status == NxtNqlStatus.COMPLETED, "status is not correctly affected"
        assert response.errorDescription == value, "value is not correctly affected"

    # invalid type for errorDescription
    def test_invalid_type_error_description(self):
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            NxtNqlApiStatusResponse(status=NxtNqlStatus.COMPLETED, errorDescription=1)

    # object from json dict
    def test_serialize_from_json(self, data_loader):
        json_data = data_loader("nql_status_response_serialize.json")
        response = NxtNqlApiStatusResponse.model_validate(json_data)
        assert response.status == NxtNqlStatus(json_data['status']), "status is not correctly affected"
        assert str(response.resultsFileUrl) == json_data['resultsFileUrl'], "url is not correctly affected"
        # pylint: disable=no-member
        assert isinstance(response.resultsFileUrl, HttpUrl.__origin__), "resultsFileUrl should be HttpUrl instance type"
        assert response.errorDescription == json_data['errorDescription'], \
            "error description is not correctly affected"

    # object serialisation to json
    def test_serialize_to_json(self, data_loader):
        json_data = data_loader("nql_status_response_serialize.json")
        response = NxtNqlApiStatusResponse.model_validate(json_data)
        to_json = response.model_dump(mode='json')
        to_json_str = response.model_dump_json()
        assert json_data == to_json, "serialize to json value is not the one expected"
        assert isinstance(to_json_str, str)
