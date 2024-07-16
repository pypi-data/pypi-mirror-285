""" Parse Nexthink YAML description API """

from pathlib import Path
from typing import List, Dict, Optional
import sys
import re
import pickle
from pydantic import BaseModel, Field
import yaml


class Server(BaseModel):
    url: str
    description: Optional[str]
    version: str


class Parameter(BaseModel):
    name: str
    in_: str
    required: bool
    type: dict
    description: Optional[str]


class Endpoint(BaseModel):
    summary: str = Field(exclude=True)
    operationId: str
    description: Optional[str]
    parameters: List[Parameter]


class Response(BaseModel):
    code: str
    description: str


class Method(BaseModel):
    method: str
    responses: List[Response]


class APISpec(BaseModel):
    title: str
    servers: List[Server]
    endpoints: Dict[str, Endpoint]
    methods: Dict[str, Dict[str, list[Response]]]


class API_config(BaseModel):
    APIs: dict[str, APISpec] = Field(default={})


class API(BaseModel):
    version: str
    endpoints: dict
    methods: dict


class YamlParser:
    api_config = None
    yaml_dir = None
    pkl_file = None

    @classmethod
    def get_package_root(cls):
        # Module name
        module_name = cls.__module__
        module = sys.modules[module_name]
        # module file path
        module_file_path = module.__file__
        # Convert to Path object
        module_path = Path(module_file_path)
        package_name = module_name.split('.', 1)[0]
        # search for top level __init__.py
        package_root = module_path.parent
        while package_root.name != package_name:
            package_root = package_root.parent

        return package_root

    @classmethod
    def get_class_file_path(cls):
        # Module name
        module_name = cls.__module__
        module = sys.modules[module_name]
        # module file path
        module_file_path = module.__file__
        # Convert to Path object
        return Path(module_file_path)

    def __init__(self):
        self.yaml_dir = self.get_package_root() / 'yaml'
        self.pkl_file = self.get_package_root() / 'Pkl/api_config.pkl'

        if self.pkl_file.exists():
            # reload api_config from PKL
            self.load_pk_file()
        else:
            # Parser les fichiers YAML et sauvegarder le résultat
            yaml_files = list(self.yaml_dir.glob('*.yaml'))
            self.api_config = self.parse_yaml_files(yaml_files)
            # save api_config to pkl_file)
            self.save_pk_file()

    def load_yaml_file(self, yaml_file) -> dict:
        with yaml_file.open('r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def load_pk_file(self) -> None:
        with (open(self.pkl_file, 'rb')) as f:
            self.api_config = pickle.load(f)

    def save_pk_file(self) -> None:
        with (open(self.pkl_file, 'wb')) as f:
            pickle.dump(self.api_config, f)

    def parse_yaml_files(self, yaml_files: List[Path]) -> API_config:  # pylint: disable=too-many-locals
        api_specs = {}
        for yaml_file in yaml_files:
            data = self.load_yaml_file(yaml_file)
            title = data.get('info', {}).get('title', 'No Title')
            description = data.get('info', {}).get('description', '')
            version = data.get('info', {}).get('version', '')
            servers = [Server(url=server['url'], description=description, version=version) for server in
                       data.get('servers', [])]
            endpoints = {}
            methods = {}

            for path, methods_info in data.get('paths', {}).items():
                for method, method_info in methods_info.items():
                    if method in ['get', 'post', 'put', 'delete', 'patch']:  # standard HTTP methods
                        endpoint = Endpoint(
                                summary=method_info.get('summary', ''),
                                operationId=method_info.get('operationId', ''),
                                description=method_info.get('description', ''),
                                parameters=self.parse_parameters(method_info.get('parameters', []))
                        )
                        if path not in endpoints:
                            endpoints[path] = endpoint

                        response_list = []
                        for code, response_info in method_info.get('responses', {}).items():
                            response_list.append(Response(code=code, description=response_info.get('description', '')))

                        if path not in methods:
                            methods[path] = {}
                        methods[path][method] = response_list

            api_specs[yaml_file.stem] = APISpec(title=title, servers=servers, endpoints=endpoints, methods=methods)
        return API_config(APIs=api_specs)

    def parse_parameters(self, params: list) -> List[Parameter]:
        parameters = []
        for param in params:
            parameter = Parameter(
                    name=param.get('name', ''),
                    in_=param.get('in', ''),
                    required=param.get('required', False),
                    type=param.get('type', {}),
                    description=param.get('description', '')
            )
            parameters.append(parameter)
        return parameters


class NxtAPISpecParser:
    # APIs Version:  {api : version}
    versions = {}
    # API list:  {index: api_name, }
    APIs = []
    # Endpoints by API {api1: [endpoint1, endpoint2],  api2: [endpoint3, endpoint4]}
    endpoints = {}
    # Methods by endpoints and by APIs: {api1: {endpoint1: [method1, method2, ...]}, api2}
    methods = []
    # API Global definition
    api_definitions = {}

    def __init__(self, APISpecs: API_config):
        self.APISpecs = APISpecs
        self.parseSpecs()

    def parseSpecs(self):
        self.versions = self.get_versions()
        self.APIs = self.get_apis()
        self.endpoints = self.get_endpoints()
        self.methods = self.get_methods_for_endpoint()
        self.api_definitions = self.get_api_definition()

    def get_versions(self) -> dict[str:str]:
        return {api: apispec.servers[0].version for api, apispec in self.APISpecs.APIs.items()}

    def get_apis(self) -> list[str]:
        return list(self.APISpecs.APIs.keys())

    def get_api_for_endpoint(self, endpoint: str) -> str:
        endpoints = self.get_endpoints()
        return next((api for api, values in endpoints.items()
                     if any(re.match(rf"(/)?{re.escape(endpoint)}", value)
                            for value in values)), None)

    def get_endpoints(self) -> dict[str, list[str]]:
        return {api: self.get_endpoints_for_api(api) for api in self.APIs}

    def get_endpoints_for_api(self, api: str) -> list[str]:
        return list(self.APISpecs.APIs[api].endpoints.keys())

    def get_methods_for_endpoint(self) -> dict[str, list[str]]:
        return {
            endpoint: list(methods.keys())
            for api in self.APISpecs.APIs.keys()
            for endpoint, methods in self.APISpecs.APIs[api].methods.items()
        }

    def get_methods_for_api(self, api: str) -> dict[str, list[str]]:
        return {
            endpoint: [method.upper() for method in responses.keys()]
            for endpoint, responses in self.APISpecs.APIs[api].methods.items()
        }

    def get_api_definition(self):
        return {
            api: {
                endpoint: {
                    method: {
                        response.code: response.description
                        for response in self.APISpecs.APIs[api].methods[endpoint][method]
                    }
                    for method in self.methods[endpoint]
                }
                for endpoint in self.endpoints[api]
            }
            for api in self.APIs
        }


class NxtYamlParser:
    api_parser: YamlParser = None
    nxt_api_spec_parser: NxtAPISpecParser = None
    api_config: API_config = None

    def __init__(self):
        self.api_parser = YamlParser()
        self.api_config = self.api_parser.api_config
        self.nxt_api_spec_parser = NxtAPISpecParser(self.api_config)
