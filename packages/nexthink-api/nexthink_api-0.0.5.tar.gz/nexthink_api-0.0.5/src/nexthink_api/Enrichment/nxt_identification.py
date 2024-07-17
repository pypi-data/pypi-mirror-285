"""
Identification information for the given object, composed of the name of the field and the value used to identify
"""

from pydantic import BaseModel, field_serializer, field_validator, InstanceOf

from .nxt_identification_name import NxtIdentificationName

__all__ = ["NxtIdentification", "NxtIdentificationName"]


class NxtIdentification(BaseModel):
    name: InstanceOf[NxtIdentificationName]
    value: str

    @field_serializer('name', when_used='json')
    def name(self, value: NxtIdentificationName):
        return value.value

    @field_validator('name', mode='before')
    @classmethod
    def validate_name(cls, value):
        if isinstance(value, str):
            return NxtIdentificationName(value)
        return value

    @field_validator('value')
    @classmethod
    def check_non_empty(cls, v):
        if not v or v.strip() == '':
            raise ValueError('value must be a non-empty string')
        return v
