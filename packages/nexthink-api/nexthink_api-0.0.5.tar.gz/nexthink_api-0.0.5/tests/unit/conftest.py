""" global fixture definition file for pytest """

import os
from pathlib import Path
import json
import pytest
import yaml

from nexthink_api import (
    NxtApiClient,
)


# Return data path for current test
@pytest.fixture
def data_path(pytestconfig, request) -> Path:
    # noinspection PyUnresolvedReferences
    invocation_dir = pytestconfig.invocation_dir
    module_path = Path(request.module.__file__).parent
    relative_module_path = module_path.relative_to(invocation_dir)
    data_dir = Path(invocation_dir / 'data' / relative_module_path)
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


# Load json data file for current test
@pytest.fixture
def data_loader(pytestconfig, request):
    def _data_loader(filename):
        data_path = os.environ.get('NEXTHINK_API_TESTS_DATA')
        root_dir = pytestconfig.rootpath
        data_dir = Path(root_dir / data_path)

        module_path = Path(request.module.__file__).parent
        relative_module_path = module_path.relative_to(data_dir)
        data_dir = Path(data_dir / 'data' / relative_module_path)
        data_dir.mkdir(parents=True, exist_ok=True)
        file_path = data_dir / filename
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    return _data_loader


@pytest.fixture
def read_yaml_file(pytestconfig):
    """
    A fixture function that reads a YAML file that describe de Nexthink API.
    It loads the YAML file specified by the 'NEXTHINK_API_YAML' environment variable.
    Returns the parsed YAML content.
    """
    def _read_yaml_file(filename):
        root_dir = pytestconfig.rootpath
        yaml_var = os.environ.get('NEXTHINK_API_YAML')
        # load and parse YAML file
        yaml_file = Path(root_dir / yaml_var / filename)
        with open(yaml_file, 'r') as f:
            return yaml.safe_load(f)
    return _read_yaml_file


# Bypass the token authentication
@pytest.fixture
def patch_bearer_token(mocker):
    mocker.patch.object(NxtApiClient, 'get_bearer_token', return_value=True)


@pytest.fixture
def patch_bearer_token_false(mocker):
    mocker.patch.object(NxtApiClient, 'get_bearer_token', return_value=False)
