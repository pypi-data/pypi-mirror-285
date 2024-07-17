"""
From the YAML file, keep only Identification enum values
Remove the <> at the end of customIdentificationName
Returns a list of Identification names to avoid duplicates
"""
import pytest

from nexthink_api import NxtIdentificationName


class TestNxtIdentificationName:  # pylint: disable=too-few-public-methods
    """
     Test the correspondence between the values obtained from an enum and a YAML file list.
     get_identification_name_from_yaml: A fixture that returns a list of field names from a YAML file.
     """
    @pytest.mark.yaml
    def test_yaml_compliance_nxt_identification_name(self, read_yaml_file):
        enrichment_data = read_yaml_file('enrichment.yaml')
        yaml_ids = list(enrichment_data['components']['schemas']['Identification']['properties']['name']['enum'])
        identification_from_yaml = {item.split('#', 1)[0] + '#{}'
                                    if '#' in item
                                    else item
                                    for item in yaml_ids}

        valuesListFromEnum = set(list(map(lambda member: member.value, NxtIdentificationName)))
        assert valuesListFromEnum == identification_from_yaml, \
            "Identification name from yaml file not equals to enum class"
