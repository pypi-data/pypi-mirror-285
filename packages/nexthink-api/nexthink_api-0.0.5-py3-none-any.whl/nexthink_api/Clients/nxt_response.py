""" Nexthink API Response Management Class """

from typing import Union, TypeAlias
from urllib.parse import urlparse
from pydantic import BaseModel, Field, ConfigDict
from requests.models import Response


from ..Enrichment.nxt_success_response import NxtSuccessResponse
from ..Enrichment.nxt_partial_success_response import NxtPartialSuccessResponse
from ..Enrichment.nxt_bad_request_response import NxtBadRequestResponse
from ..Enrichment.nxt_forbidden_response import NxtForbiddenResponse
from ..Enrichment.nxt_individual_object_error import NxtIndividualObjectError
from ..Utils.nxt_yaml_parser import NxtYamlParser, NxtAPISpecParser
from ..Models.nxt_endpoint import NxtEndpoint
from ..Models.nxt_invalid_token_request import NxtInvalidTokenRequest
from ..Models.nxt_token_response import NxtTokenResponse
from ..Exceptions.nxt_api_exception import NxtApiException
from ..Nql.nxt_nql_api_execute_response import NxtNqlApiExecuteResponse
from ..Nql.nxt_nql_api_execute_v2_response import NxtNqlApiExecuteV2Response
from ..Nql.nxt_nql_api_export_response import NxtNqlApiExportResponse
from ..Nql.nxt_nql_api_status_response import NxtNqlApiStatusResponse
from ..Nql.nxt_error_response import NxtErrorResponse


# using an alias to make the code more readable
ResponseType: TypeAlias = Union[
    NxtSuccessResponse,
    NxtPartialSuccessResponse,
    NxtBadRequestResponse,
    NxtForbiddenResponse,
    NxtIndividualObjectError,
    NxtTokenResponse
]

EnrichmentResponseType: TypeAlias = Union[
    NxtSuccessResponse,
    NxtPartialSuccessResponse,
    NxtBadRequestResponse,
    NxtInvalidTokenRequest,
    NxtForbiddenResponse
]


class NxtResponse(BaseModel):
    response: ResponseType = Field(alias='value', default=None)
    nxt_yaml_parser: NxtAPISpecParser = Field(default=None)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

    @property
    def value(self):
        return self.response

    def build_nxt_response(self, response: Response):
        nxt_yaml_parser = NxtYamlParser()
        self.nxt_yaml_parser = nxt_yaml_parser.nxt_api_spec_parser
        endpoint = urlparse(response.url).path
        api = NxtEndpoint.get_api_name(endpoint)
        if api == NxtEndpoint.Enrichment.name:
            return self.build_nxt_enrichment_response(response)
        if api == NxtEndpoint.Act.name:
            return self.build_nxt_act_response(response)
        if api == NxtEndpoint.Engage.name:
            return self.build_nxt_engage_response(response)
        if api == NxtEndpoint.Workflow.name:
            return self.build_nxt_workflow_response(response)
        if api in ['Nql', 'NqlV2', 'NqlExport', 'NqlStatus']:
            return self.build_nxt_nql_response(response)
        if api == NxtEndpoint.Token.name:
            return self.build_nxt_token_response(response)
        raise NxtApiException(f"Can't create response for the API: '{api}'")

    # noinspection PyMethodMayBeStatic
    def build_nxt_enrichment_response(self, response: Response) -> EnrichmentResponseType:
        """
        Create Enrichment response the POST/GET response.

        Args:
            response (Response): The response object to build the response from.

        Returns:
            EnrichmentResponseType: The response object based on the status code of the given response.

        Raises:
            HTTPError: If the status code is not one of the expected values.

        """
        status_code = response.status_code
        if status_code == 200:
            return NxtSuccessResponse()
        if status_code == 207:
            data = response.json()
            return NxtPartialSuccessResponse.model_validate(data)
        if status_code == 400:
            data = response.json()
            return NxtBadRequestResponse(errors=data['errors'])
        if status_code == 401:
            return NxtInvalidTokenRequest()
        if status_code == 403:
            return NxtForbiddenResponse(message=response.reason)
        raise NxtApiException(f"Unknown status response code: {status_code}")

    def build_nxt_act_response(self, response: Response):
        pass

    def build_nxt_workflow_response(self, response: Response):
        pass

    def build_nxt_engage_response(self, response: Response):
        pass

    # noinspection PyMethodMayBeStatic
    def build_nxt_nql_response(self, response: Response):
        status_code = response.status_code
        if status_code == 200:
            url = urlparse(response.url)
            api = NxtEndpoint.get_api_name(url.path)
            data = response.json()
            if api == NxtEndpoint.Nql.name:
                return NxtNqlApiExecuteResponse.model_validate(data)
            if api == NxtEndpoint.NqlV2.name:
                return NxtNqlApiExecuteV2Response.model_validate(data)
            if api == NxtEndpoint.NqlExport.name:
                return NxtNqlApiExportResponse.model_validate(data)
            if api == NxtEndpoint.NqlStatus.name:
                return NxtNqlApiStatusResponse.model_validate(data)
            return NxtErrorResponse(message=f"Can't find API for {url.path}", code=418)
        if status_code in [401, 403, 404, 406, 500, 503]:
            return NxtErrorResponse(message=response.reason, code=status_code)
        raise NxtApiException(f"Unknown status response code: {status_code}")

    # noinspection PyMethodMayBeStatic
    def build_nxt_token_response(self, response: Response):
        return NxtTokenResponse(code=response.status_code, description=response.text)

    def from_response(self, response: Response):
        return self.build_nxt_response(response)
