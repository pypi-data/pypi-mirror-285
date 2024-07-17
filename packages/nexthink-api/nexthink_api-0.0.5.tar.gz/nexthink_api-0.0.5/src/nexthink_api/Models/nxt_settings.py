""" Nexthink Tenant Configuration Class """

from typing import Final, Self, Optional, Dict, Union
from urllib.parse import urljoin
import os
from pydantic import BaseModel, HttpUrl, Field, model_validator

from .nxt_region_name import NxtRegionName
from .nxt_endpoint import NxtEndpoint


class NxtSettings(BaseModel):
    base_url: Final = 'https://{instance}.api.{region}.nexthink.cloud'
    instance: str = Field(min_length=1)
    region: NxtRegionName
    infinity_base_uri: HttpUrl = Field(init=False, default=None)
    token_url: HttpUrl = Field(init=False, default=None)
    proxies: Optional[Union[Dict[str, str], bool]] = None

    @model_validator(mode='before')
    @classmethod
    def set_infinity_base_uri(cls, values):
        instance = values.get("instance")
        region = values.get("region")

        assert (instance is not None and region is not None), "Instance and Region are required"
        values['infinity_base_uri'] = cls.base_url.format(instance=instance, region=region.value)
        return values

    @model_validator(mode='after')
    def set_settings_init(self) -> Self:
        self.token_url = urljoin(str(self.infinity_base_uri), NxtEndpoint.Token.value)
        # Proxy has not been provided, try to detect proxies
        if self.proxies is None:
            # Attempt to detect proxies from environment variables (optional)
            self.proxies = {
                'http': os.getenv("http_proxy") or os.getenv("HTTP_PROXY"),
                'https': os.getenv("https_proxy") or os.getenv("HTTPS_PROXY")
            } or {}
        # False is used to disable proxy
        elif self.proxies is False:
            self.proxies = {}

        return self
