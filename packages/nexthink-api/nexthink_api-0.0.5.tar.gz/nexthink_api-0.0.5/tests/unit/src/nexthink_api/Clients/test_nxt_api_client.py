"""Unit test file for nexthink_api"""
from typing import Iterator
import base64
import requests
import pytest

from nexthink_api import (
    NxtApiClient,
    NxtRegionName,
    NxtEndpoint,
    NxtSuccessResponse,
    NxtPartialSuccessResponse,
    NxtBadRequestResponse,
    NxtForbiddenResponse,
    NxtInvalidTokenRequest

)


class TestNxtApiClientTest:

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

    # pylint: disable=too-many-arguments
    # Mock response helper
    def _mock_response(
            self,
            mocker,
            status=200,
            content="CONTENT",
            json_data=None,
            endpoint=None,
            raise_for_status=None):
        """
        This will return a mock response with the provided status, content and json data
        """
        mock_resp = mocker.Mock()
        # mock raise_for_status call w/optional error
        mock_resp.raise_for_status = mocker.Mock()
        if raise_for_status:
            mock_resp.raise_for_status.side_effect = raise_for_status
        # set status code and content
        mock_resp.status_code = status
        mock_resp.content = content
        # add json data if provided
        if json_data:
            mock_resp.json = mocker.Mock(
                    return_value=json_data
            )
        if endpoint:
            mock_resp.url = endpoint.value
        return mock_resp

    # valid instance without token
    def test_ValidInstanceWithoutToken(self, mocker, value_iter):
        # Arrange
        instance = next(value_iter)
        region = NxtRegionName.eu
        client_id = next(value_iter)
        client_secret = next(value_iter)

        # Mock
        mocker.patch.object(NxtApiClient, 'init_token', return_value=None)

        # Act
        nxtClient = NxtApiClient(instance, region, client_id=client_id, client_secret=client_secret)

        # Assert
        assert nxtClient.token is None, "Token should not initialize yet"
        assert nxtClient.settings.instance == instance, "Instance is not the one expected"
        assert nxtClient.settings.region == region, "Instance is not the one expected"
        assert isinstance(nxtClient.settings.region, NxtRegionName), "Instance of region should be NxtRegionName"

    # Valid instance with call to create_autorisation
    def test_ValidInstance(self, mocker, value_iter):
        # Arrange
        instance = next(value_iter)
        region = NxtRegionName.eu
        client_id = next(value_iter)
        client_secret = next(value_iter)
        expected_cred = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

        # Mock to bypass the get_bearer_token() function
        get_bearer_token = mocker.patch.object(NxtApiClient, 'get_bearer_token', return_value=False)

        # Act
        nxtClient = NxtApiClient(instance, region, client_id=client_id, client_secret=client_secret)

        # Assert
        assert nxtClient.headers['Authorization'] == f"Basic {expected_cred}", "Credential is not the one expected"
        assert get_bearer_token.call_once(), "get_bearer_token has not been call"
        assert nxtClient.token is None, "Token should not initialize yet"
        assert nxtClient.settings.instance == instance, "Instance is not the one expected"
        assert nxtClient.settings.region == region, "Instance is not the one expected"
        assert isinstance(nxtClient.settings.region, NxtRegionName), "Instance of region should be NxtRegionName"

    def test_get_bearer_token(self, mocker, value_iter):
        # arrange
        instance = next(value_iter)
        region = NxtRegionName.eu
        client_id = next(value_iter)
        client_secret = next(value_iter)
        mock_post_response = mocker.Mock()
        mock_post_response.json.return_value = {"access_token": "test_access_token"}
        mock_post_response.url = NxtEndpoint.Token.value
        mock_post_response.status_code = 200
        mock_post_response.text = 'test'

        # mock
        # get_bearer_token = mocker.patch.object(NxtApiClient, 'post', return_value=mock_response)
        mock_post = mocker.patch('requests.post')
        mock_post.return_value = mock_post_response

        # act
        nxtClient = NxtApiClient(instance, region, client_id=client_id, client_secret=client_secret)

        # assert
        assert nxtClient.token == "test_access_token", "Token is not the one expected"
        assert mock_post.call_once(), "get_bearer_token has not been call"
        assert nxtClient.headers == {
            "Authorization": "Bearer test_access_token",
            "Content-Type" : "application/json",
            "Accept"       : "application/json, text/csv",
        }, "Headers are not set correctly"

    # Check if header is correct when the token has been got
    def test_update_header(self, mocker, value_iter):
        # Arrange
        instance = next(value_iter)
        region = NxtRegionName.eu
        client_id = next(value_iter)
        client_secret = next(value_iter)

        # Mock
        get_bearer_token = mocker.patch.object(NxtApiClient, 'get_bearer_token', return_value=True)

        # Act
        nxtClient = NxtApiClient(instance, region, client_id=client_id, client_secret=client_secret)

        # Assert
        assert nxtClient.token is None, "Token is not the one expected"
        assert get_bearer_token.call_once(), "get_bearer_token has not been call"
        assert nxtClient.headers == {
            "Authorization": "Bearer None",
            "Content-Type" : "application/json",
            "Accept"       : "application/json, text/csv",
        }, "Headers are not set correctly"

    #  successfully retrieves data from a valid endpoint with default parameters
    def test_get_valid_endpoint_default_params(self, mocker, value_iter):
        # Arrange
        instance = next(value_iter)
        region = NxtRegionName.eu
        client_id = next(value_iter)
        client_secret = next(value_iter)
        mock_get_response = {"key": "value"}

        # Mock
        # Build response for token and get test
        mock_get_response = self._mock_response(mocker, json_data=mock_get_response)
        mock_get = mocker.patch.object(NxtApiClient, 'get', return_value=mock_get_response)
        mock_client_instance = mocker.Mock(sepc=NxtApiClient)
        mocker.patch.object(NxtApiClient, 'init_token', return_value=mock_client_instance)
        mocker.patch.object(NxtApiClient, 'get_bearer_token', return_value=True)

        # Act
        nxtClient = NxtApiClient(instance, region, client_id=client_id, client_secret=client_secret)

        # Assert
        assert mock_client_instance.init_client.call_once(), "should have been call once"
        assert mock_client_instance.get_bearer_token.call_once(), "should have been call once"
        assert mock_client_instance.update.call_once(), "should have been call once"

        # act 2
        response = nxtClient.get(NxtEndpoint.Enrichment)

        # Assert 2
        assert response == mock_get_response, "Response is not the one expected"
        assert mock_get.call_once_with(NxtEndpoint.Enrichment), "get should have been call once"

    #  handles successful response with status code 200
    def test_get_successful_response_200(self, mocker):
        # Mock to bypass token
        mocker.patch.object(NxtApiClient, 'get_bearer_token', return_value=True)

        # Arrange
        mock_response = self._mock_response(mocker, endpoint=NxtEndpoint.Enrichment)

        # Mock
        mocker.patch("requests.get", return_value=mock_response)

        # Act
        client = NxtApiClient(instance="test_instance", region=NxtRegionName.us, client_id="test_id",
                              client_secret="test_secret")
        response = client.get(NxtEndpoint.Enrichment)

        # Assert
        assert isinstance(response, NxtSuccessResponse)

    #  handles 207 Enrichment return code
    def test_get_207_status_code(self, mocker, data_loader, patch_bearer_token):
        # Arrange
        data = data_loader('Enrichment207.json')
        mock_response = self._mock_response(mocker,
                                            endpoint=NxtEndpoint.Enrichment,
                                            status=207,
                                            json_data=data)

        # Mock
        mocker.patch("requests.get", return_value=mock_response)

        # Act
        client = NxtApiClient(instance="test_instance", region=NxtRegionName.us, client_id="test_id",
                              client_secret="test_secret")
        response = client.get(NxtEndpoint.Enrichment)

        # Assert
        assert isinstance(response, NxtPartialSuccessResponse)
        assert response.model_dump() == data

    #  handles 400 Enrichment return code
    def test_get_400_status_code(self, mocker, data_loader, patch_bearer_token):
        # Arrange
        data = data_loader('Enrichment400.json')
        mock_response = self._mock_response(mocker,
                                            endpoint=NxtEndpoint.Enrichment,
                                            status=400,
                                            json_data=data)

        # Mock
        mocker.patch("requests.get", return_value=mock_response)

        # Act
        client = NxtApiClient(instance="test_instance", region=NxtRegionName.us, client_id="test_id",
                              client_secret="test_secret")
        response = client.get(NxtEndpoint.Enrichment)

        # Assert
        assert isinstance(response, NxtBadRequestResponse)
        assert response.model_dump() == data

    def test_get_401_status_code(self, mocker, patch_bearer_token):
        # Arrange
        mock_response = self._mock_response(mocker,
                                            endpoint=NxtEndpoint.Enrichment,
                                            status=401)

        # Mock
        mocker.patch("requests.get", return_value=mock_response)

        # Act
        client = NxtApiClient(instance="test_instance", region=NxtRegionName.us, client_id="test_id",
                              client_secret="test_secret")
        response = client.get(NxtEndpoint.Enrichment)

        # Assert
        assert isinstance(response, NxtInvalidTokenRequest)

    def test_get_403_status_code(self, mocker, patch_bearer_token):
        # Arrange
        mock_response = self._mock_response(mocker,
                                            endpoint=NxtEndpoint.Enrichment,
                                            status=403)
        mock_response.reason = "Forbidden"

        # Mock
        mocker.patch("requests.get", return_value=mock_response)

        # Act
        client = NxtApiClient(instance="test_instance", region=NxtRegionName.us, client_id="test_id",
                              client_secret="test_secret")
        response = client.get(NxtEndpoint.Enrichment)

        # Assert
        assert isinstance(response, NxtForbiddenResponse)

    #  handles network issues such as timeouts or connection errors
    def test_get_network_issues(self, mocker):
        # Mock
        mocker.patch("requests.get", side_effect=requests.exceptions.ConnectionError("Connection error"))

        # Act
        with pytest.raises(requests.exceptions.ConnectionError):
            NxtApiClient(instance="test_instance", region=NxtRegionName.us, client_id="test_id",
                         client_secret="test_secret")

    #  handles invalid endpoint values gracefully
    def test_get_invalid_endpoint(self):
        with pytest.raises(AttributeError):
            # noinspection PyUnresolvedReferences
            # pylint: disable=no-member
            NxtApiClient(instance="test_instance", region=NxtRegionName.dom, client_id="test_id",
                         client_secret="test_secret")
