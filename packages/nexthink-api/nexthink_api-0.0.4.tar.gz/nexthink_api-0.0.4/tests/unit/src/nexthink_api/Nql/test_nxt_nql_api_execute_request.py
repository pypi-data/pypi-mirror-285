"""Unit test file for nexthink_api"""
import pytest

from nexthink_api import NxtNqlApiExecuteRequest


class TestNxtNqlApiExecuteRequest:

    #  valid queryId with minimum length
    def test_valid_queryId_min_length(self):
        request = NxtNqlApiExecuteRequest(queryId="#a", parameters={})
        assert request.queryId == "#a"

    #  valid queryId with maximum length
    def test_valid_queryId_max_length(self):
        max_length_queryId = "#" + "a" * 254
        request = NxtNqlApiExecuteRequest(queryId=max_length_queryId, parameters={})
        assert request.queryId == max_length_queryId

    #  valid queryId with mixed alphanumeric characters
    def test_valid_queryId_mixed_alphanumeric(self):
        request = NxtNqlApiExecuteRequest(queryId="#a1b2c3", parameters={})
        assert request.queryId == "#a1b2c3"

    #  queryId with less than 2 characters
    def test_queryId_less_than_2_characters(self):
        with pytest.raises(ValueError):
            NxtNqlApiExecuteRequest(queryId="#", parameters={})

    #  queryId without a leading '#'
    def test_queryId_without_leading_hash(self):
        with pytest.raises(ValueError):
            NxtNqlApiExecuteRequest(queryId="a1b2c3", parameters={})

    #  queryId with special characters not allowed by regex
    def test_queryId_with_special_characters(self):
        with pytest.raises(ValueError):
            NxtNqlApiExecuteRequest(queryId="#a1b2c3!", parameters={})

    #  dictionary with one parameter
    def test_one_parameter_dictionary(self):
        request = NxtNqlApiExecuteRequest(queryId="#validqueryid", parameters={"name": "value"})
        assert request.parameters == {"name": "value"}
        assert request.queryId == "#validqueryid"

    #  dictionary with 2 parameters
    def test_two_parameters_dictionary(self):
        request = NxtNqlApiExecuteRequest(queryId="#validqueryid", parameters={"name": "value", "name2": "value2"})
        assert request.parameters == {"name": "value", "name2": "value2"}
        assert request.queryId == "#validqueryid"

    def test_no_parameters(self):
        requests = NxtNqlApiExecuteRequest(queryId="#validqueryid")
        assert requests.queryId == "#validqueryid", "Not the expected value"
        # pylint: disable=use-implicit-booleaness-not-comparison
        assert requests.parameters == {}, "parameters should be empty by default"
