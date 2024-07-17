"""Unit test file for nexthink_api"""
from nexthink_api import NxtEndpoint


class TestNxtEndpoint:

    #  get_api_name returns correct enum name for valid path
    def test_get_api_name_valid_path(self):
        assert NxtEndpoint.get_api_name('/api/v1/enrichment/data/fields') == 'Enrichment'
        assert NxtEndpoint.get_api_name('/api/v1/act/execute') == 'Act'
        assert NxtEndpoint.get_api_name('/api/v1/euf/campaign/trigger') == 'Engage'
        assert NxtEndpoint.get_api_name('/api/v1/workflow/execute') == 'Workflow'
        assert NxtEndpoint.get_api_name('/api/v1/nql/execute') == 'Nql'
        assert NxtEndpoint.get_api_name('/api/v2/nql/execute') == 'NqlV2'
        assert NxtEndpoint.get_api_name('/api/v1/nql/export') == 'NqlExport'
        assert NxtEndpoint.get_api_name('/api/v1/nql/status') == 'NqlStatus'
        assert NxtEndpoint.get_api_name('/api/v1/token') == 'Token'

    #  all enum values are correctly assigned to their respective paths
    def test_enum_values_assigned_correctly(self):
        assert NxtEndpoint.Enrichment == '/api/v1/enrichment/data/fields'
        assert NxtEndpoint.Act == '/api/v1/act/execute'
        assert NxtEndpoint.Engage == '/api/v1/euf/campaign/trigger'
        assert NxtEndpoint.Workflow == '/api/v1/workflow/execute'
        assert NxtEndpoint.Nql == '/api/v1/nql/execute'
        assert NxtEndpoint.NqlV2 == '/api/v2/nql/execute'
        assert NxtEndpoint.NqlExport == '/api/v1/nql/export'
        assert NxtEndpoint.NqlStatus == '/api/v1/nql/status'
        assert NxtEndpoint.Token == '/api/v1/token'

    def test_number_of_endpoints(self):
        expected = 9
        assert len(NxtEndpoint) == expected, f"Number of endpoints should be {expected}"

    #  get_api_name returns None for invalid path
    def test_get_api_name_invalid_path(self):
        assert NxtEndpoint.get_api_name('/invalid/path') is None

    #  get_api_name with empty string as path
    def test_get_api_name_empty_string(self):
        assert NxtEndpoint.get_api_name('') is None

    #  get_api_name with path not starting with '/'
    def test_get_api_name_no_leading_slash(self):
        assert NxtEndpoint.get_api_name('api/v1/enrichment/data/fields') is None

    #  get_api_name with path containing special characters
    def test_get_api_name_special_characters(self):
        assert NxtEndpoint.get_api_name('/api/v1/enrichment/data/fields/!@#') == 'Enrichment'

    #  get_api_name with path having trailing slashes
    def test_get_api_name_trailing_slashes(self):
        assert NxtEndpoint.get_api_name('/api/v1/enrichment/data/fields/') == 'Enrichment'
