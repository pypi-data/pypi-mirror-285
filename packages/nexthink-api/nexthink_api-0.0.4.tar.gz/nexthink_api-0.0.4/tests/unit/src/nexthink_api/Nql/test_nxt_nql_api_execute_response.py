"""Unit test file for nexthink_api"""
import pytest
from pydantic import ValidationError

from nexthink_api import NxtDateTime, NxtNqlApiExecuteResponse


class TestNxtNqlApiExecuteResponse:

    #  valid input data correctly initializes NxtNqlApiExecuteResponse instance
    def test_valid_input_initializes_instance(self):
        execution_time = NxtDateTime(year=2023, month=10, day=5, hour=12, minute=30, second=45)
        response = NxtNqlApiExecuteResponse(
            queryId="queryId",
            executedQuery="devices | list name",
            rows=10,
            executionDateTime=execution_time,
            headers=["name"],
            data=[["Alice"], ["Bob"]]
        )
        assert response.queryId == "queryId"
        assert response.executedQuery == "devices | list name"
        assert response.rows == 10
        assert response.executionDateTime == execution_time
        assert response.headers == ["name"]
        assert response.data == [["Alice"], ["Bob"]]

    #  headers list containing non-string elements raises validation error
    def test_headers_with_non_string_elements_raises_error(self):
        execution_time = NxtDateTime(year=2023, month=10, day=5, hour=12, minute=30, second=45)
        with pytest.raises(ValueError):
            NxtNqlApiExecuteResponse(
                    queriId="queryId",
                    executedQuery="devices | list name",
                    rows=10,
                    executionDateTime=execution_time,
                    headers=["name", 123],
                    data=[["Alice"], ["Bob"]]
            )

    #  data list containing non-list elements raises validation error
    def test_data_with_non_list_elements_raises_error(self):
        execution_time = NxtDateTime(year=2023, month=10, day=5, hour=12, minute=30, second=45)
        with pytest.raises(ValueError):
            NxtNqlApiExecuteResponse(
                    queryId="queryId",
                    executedQuery="devices | list name",
                    rows=10,
                    executionDateTime=execution_time,
                    headers=["name", 123],
                    data=[[1], [2]]
            )

    #  rows field with negative or non-integer values raises validation error
    def test_rows_with_invalid_values_raises_error(self):
        execution_time = NxtDateTime(year=2023, month=10, day=5, hour=12, minute=30, second=45)
        with pytest.raises(ValidationError):
            r = NxtNqlApiExecuteResponse(
                queryId="queryId",
                executedQuery="devices | list name",
                rows=-1,
                executionDateTime=execution_time,
                headers=["name"],
                data=[["Alice"], ["Bob"]]
            )
            print(r.model_dump_json())
        with pytest.raises(ValidationError):
            NxtNqlApiExecuteResponse(
                queryId="queryId",
                executedQuery="devices | list name",
                rows="ten",
                executionDateTime=execution_time,
                headers=["name"],
                data=[["Alice"], ["Bob"]]
            )

    # test build class from json dict
    def test_serialize_from_json(self, data_loader):
        json_data = data_loader("nql_execute_response_serialize.json")
        response = NxtNqlApiExecuteResponse.model_validate(json_data)
        assert response.queryId == json_data['queryId'], "Bad queryId value"
        assert response.executedQuery == json_data['executedQuery'], "Bad executedQuery value"
        assert response.rows == json_data['rows'], "Bad rows number value"
        assert response.executionDateTime.model_dump() == json_data['executionDateTime'], 'Bad Execution datetime value'
        assert response.data == json_data['data'], "Bad data dict value"
