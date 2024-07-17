"""Unit test file for nexthink_api"""
import pytest

from nexthink_api import (
    NxtNqlStatus,
)


class TestNxtNqlStatus:  # pylint: disable=too-few-public-methods
    @pytest.mark.yaml
    def test_yaml_compliance_nql_status_response_value(self, read_yaml_file):
        # Get Field name from yaml file
        data = read_yaml_file('nql.yaml')
        yaml_fields = set(data['components']['schemas']['NqlApiStatusResponse']['properties']['status']['enum'])
        # remove example for custom field name and deduplicate
        fields_from_yaml = set(yaml_fields)
        valuesListFromEnum = set(list(map(lambda member: member.value, NxtNqlStatus)))
        assert valuesListFromEnum == fields_from_yaml, "Values from yaml file not equals to enum class"
