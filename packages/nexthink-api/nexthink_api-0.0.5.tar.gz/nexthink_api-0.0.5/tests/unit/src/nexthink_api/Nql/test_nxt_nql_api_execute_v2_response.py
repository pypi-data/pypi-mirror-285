"""Unit test file for nexthink_api"""
import pytest
from pydantic import ValidationError

from nexthink_api import NxtNqlApiExecuteV2Response


class TestNxtNqlApiExecuteV2Response:

    #  valid queryId, executedQuery, rows, executionDateTime, and data are correctly parsed
    def test_valid_input_parsing(self):
        response = NxtNqlApiExecuteV2Response(
            queryId="123",
            executedQuery="devices | list name",
            rows=10,
            executionDateTime="2023-10-01T12:00:00",
            data=[{"key1": "value1", "key2": "value2"}]
        )
        assert response.queryId == "123"
        assert response.executedQuery == "devices | list name"
        assert response.rows == 10
        assert response.executionDateTime == "2023-10-01T12:00:00"
        assert response.data == [{"key1": "value1", "key2": "value2"}]

    #  executionDateTime is not in ISO format
    def test_execution_iso_datetime_parsing(self):
        with pytest.raises(ValidationError):
            NxtNqlApiExecuteV2Response(
                queryId="123",
                executedQuery="devices | list name",
                rows=10,
                executionDateTime="2023-10-01T12:00:70",
                data=[{"key1": "value1", "key2": "value2"}]
            )

    #  data dictionary contains expected key-value pairs
    def test_data_dictionary_contents(self):
        response = NxtNqlApiExecuteV2Response(
            queryId="123",
            executedQuery="devices | list name",
            rows=10,
            executionDateTime="2023-10-01T12:00:00",
            data=[{"key1": "value1", "key2": "value2"}]
        )
        assert response.data == [{"key1": "value1", "key2": "value2"}]

    # data is not a list
    def test_data_is_not_list(self):
        with pytest.raises(ValidationError):
            # noinspection PyTypeChecker
            NxtNqlApiExecuteV2Response(
                    queryId="123",
                    executedQuery="devices | list name",
                    rows=10,
                    executionDateTime="2023-10-01T12:00:00",
                    data={"key1": "value1", "key2": "value2"}
            )

    #  rows is non-integer value
    def test_invalid_rows_value(self):
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            NxtNqlApiExecuteV2Response(
                queryId="123",
                executedQuery="devices | list name",
                rows="ten",
                executionDateTime="2023-10-01T12:00:00",
                data=[{"key1": "value1", "key2": "value2"}]
            )

    #  data contains non-string values
    def test_invalid_data_dictionary(self):
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            NxtNqlApiExecuteV2Response(
                queryId="123",
                executedQuery="devices | list name",
                rows=10,
                executionDateTime="2023-10-01T12:00:00",
                data=[{"key1": 100}]
            )

    # object from json dict
    def test_serialize_from_json(self, data_loader):
        json_data = data_loader("nql_execute_v2_response_serialize.json")
        response = NxtNqlApiExecuteV2Response.model_validate(json_data)
        assert response.queryId == json_data['queryId'], "Bad queryId value"
        assert response.executedQuery == json_data['executedQuery'], "Bad executedQuery value"
        assert response.rows == json_data['rows'], "Bad rows number value"
        assert response.executionDateTime == json_data['executionDateTime'], 'Bad Execution datetime value'
        assert response.data == json_data['data'], "Bad data dict value"
