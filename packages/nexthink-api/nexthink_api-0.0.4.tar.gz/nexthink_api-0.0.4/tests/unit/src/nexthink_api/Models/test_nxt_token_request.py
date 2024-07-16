"""Unit test file for nexthink_api"""
from pydantic import ValidationError
import pytest

from nexthink_api import NxtTokenRequest


class TestNxtTokenRequest():

    def testValidHeaderWIthModelDump(self):
        v1: NxtTokenRequest = NxtTokenRequest()
        d: dict = v1.model_dump()
        assert d == {'grant_type': 'client_credentials'}

    def testModifyHeader(self):
        with pytest.raises(ValidationError):
            v1: NxtTokenRequest = NxtTokenRequest()
            v1.data = {'test': 'toto'}
