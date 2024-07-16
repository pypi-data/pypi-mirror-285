"""Unit test file for nexthink_api"""
import pytest

from nexthink_api import NxtFieldName


class TestNxtFieldName:  # pylint: disable=too-few-public-methods
    """
     Test the correspondence between the values obtained from an enum and a YAML file list.
     :param get_nxt_field_name_list: A fixture that returns a list of field names from a YAML file.
     """
    @pytest.mark.yaml
    def test_yaml_compliance_nxt_field_name(self, read_yaml_file):
        # Get Field name from yaml file
        enrichment_data = read_yaml_file('enrichment.yaml')
        yaml_fields = list(enrichment_data['components']['schemas']['Field']['properties']['name']['enum'])
        # remove example for custom field name and deduplicate
        fields_from_yaml = {item.split('#', 1)[0] + '#{}'
                            if '#' in item
                            else item
                            for item in yaml_fields}
        valuesListFromEnum = set(list(map(lambda member: member.value, NxtFieldName)))
        assert valuesListFromEnum == fields_from_yaml, "Field name from yaml file not equals to enum class"
