""" Request handling class for the Nexthink API """

import base64
from typing import Union, Optional
from urllib.parse import urljoin
import time
import requests

from ..Models.nxt_settings import NxtSettings
from ..Models.nxt_endpoint import NxtEndpoint
from ..Models.nxt_region_name import NxtRegionName
from ..Models.nxt_token_request import NxtTokenRequest
from ..Exceptions.nxt_token_exception import NxtTokenException
from ..Exceptions.nxt_status_exception import NxtStatusException
from ..Exceptions.nxt_timeout_exception import NxtStatusTimeoutException
from ..Enrichment.nxt_enrichment_request import NxtEnrichmentRequest
from ..Clients.nxt_response import NxtResponse
from ..Nql.nxt_nql_api_execute_request import NxtNqlApiExecuteRequest
from ..Nql.nxt_nql_api_status_response import NxtNqlApiStatusResponse
from ..Nql.nxt_nql_api_export_response import NxtNqlApiExportResponse
from ..Nql.nxt_error_response import NxtErrorResponse
from ..Nql.nxt_nql_status import NxtNqlStatus
from ..Utils.nxt_yaml_parser import NxtYamlParser


__all__ = ["NxtApiClient"]


class NxtApiClient:
    # pylint: disable=too-many-arguments
    def __init__(self, instance: str, region: NxtRegionName, client_id: str, client_secret: str, proxies=None):
        self.settings = NxtSettings(instance=instance, region=region, proxies=proxies)
        self.endpoint: NxtEndpoint
        self.token = None
        self.headers = {}
        self.init_token(client_id, client_secret)

    def init_token(self, client_id: str, client_secret: str) -> None:
        self.create_autorisation(client_id, client_secret)
        if self.get_bearer_token():
            self.update_header()

    def update_header(self, endpoint: NxtEndpoint = None) -> None:
        # Update header for subsequent requests
        if endpoint in [ None, NxtEndpoint.NqlExport, NxtEndpoint.NqlStatus]:
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type" : "application/json",
                "Accept"       : "application/json, text/csv",
            }
        else:
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

    def create_autorisation(self, client_id: str, client_secret: str) -> None:
        if self.token is None:
            credentials: str = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
            self.headers['Authorization'] = f'Basic {credentials}'

    def get_bearer_token(self) -> bool:
        try:
            return_value = False
            # Prepare to request token
            data = NxtTokenRequest().model_dump()
            # Endpoint for token request
            url = urljoin(str(self.settings.infinity_base_uri), NxtEndpoint.Token.value)
            # Request the token
            response = requests.post(url, headers=self.headers, json=data, proxies=self.settings.proxies, timeout=300)
            nxt_response = NxtResponse()
            nxt_result = nxt_response.from_response(response=response)
            if nxt_result.code == 200:
                self.token = response.json()["access_token"]
                return_value = True
            return return_value

        # In case of raise_for_status has generated an Exception
        except requests.exceptions.HTTPError as e:
            # Something went wrong
            raise NxtTokenException(f"Error during token retrieval: {e}") from e

    def run_enrichment(self, endpoint: NxtEndpoint, data: NxtEnrichmentRequest) -> NxtResponse:
        self.update_header(endpoint)
        return self.post(endpoint, data)

    def run_nql(self, endpoint: NxtEndpoint, data: NxtNqlApiExecuteRequest, method: Optional[str] = None):
        method = method or 'POST'
        if not self.check_method(endpoint, method):
            raise ValueError('Unsupported HTTP method')
        self.update_header(endpoint)
        if method == 'POST':
            return self.post(endpoint, data)
        return self.get(endpoint, data)

    def wait_status(
            self,
            value: NxtNqlApiExportResponse,
            timeout: int = 300
    ) -> Union[NxtNqlApiStatusResponse, NxtErrorResponse]:
        start = time.time()
        status = NxtNqlApiStatusResponse(status=NxtNqlStatus.SUBMITTED)
        while status.status in [NxtNqlStatus.SUBMITTED, NxtNqlStatus.IN_PROGRESS]:
            status = self.get_status_export(value)
            if isinstance(status, NxtErrorResponse):
                return status
            if time.time() - start > timeout:
                raise NxtStatusTimeoutException("Status not completed before timeout")
            time.sleep(1)
        return status

    def get_status_export(self, value: NxtNqlApiExportResponse) -> NxtNqlStatus:
        export_status_url = urljoin(str(self.settings.infinity_base_uri), NxtEndpoint.NqlStatus.value + '/')
        export_status_url = urljoin(export_status_url, value.exportId)
        response = requests.get(export_status_url, headers=self.headers, proxies=self.settings.proxies, timeout=300)
        nxt_response = NxtResponse()
        response_status = nxt_response.from_response(response=response)
        return response_status

    def download_export(self, value: NxtNqlApiStatusResponse, timeout: int = 300):
        if value.status != NxtNqlStatus.COMPLETED:
            raise NxtStatusException("Try do download an export not completed")
        res = requests.get(value.resultsFileUrl, proxies=self.settings.proxies, timeout=timeout)
        return res

    # noinspection PyMethodMayBeStatic
    def check_method(self, endpoint: NxtEndpoint, method: str) -> bool:
        nxt_yaml_parser = NxtYamlParser()
        api = nxt_yaml_parser.nxt_api_spec_parser.get_api_for_endpoint(endpoint)
        methods = nxt_yaml_parser.nxt_api_spec_parser.get_methods_for_api(api)
        return method in methods.get(endpoint.value, [])

    def get(self, endpoint: NxtEndpoint, params=None):
        url = urljoin(str(self.settings.infinity_base_uri), endpoint.value)
        response = requests.get(url, headers=self.headers, params=params, proxies=self.settings.proxies, timeout=300)
        nxt_response = NxtResponse()
        response_status = nxt_response.from_response(response=response)
        return response_status

    def post(self, endpoint: NxtEndpoint, data: Union[NxtTokenRequest, NxtEnrichmentRequest, NxtNqlApiExecuteRequest]):
        url = urljoin(str(self.settings.infinity_base_uri), endpoint.value)
        response = requests.post(url,
                                 headers=self.headers,
                                 json=data.model_dump(),
                                 proxies=self.settings.proxies,
                                 timeout=300)
        nxt_response = NxtResponse()
        response_status = nxt_response.from_response(response=response)
        return response_status
