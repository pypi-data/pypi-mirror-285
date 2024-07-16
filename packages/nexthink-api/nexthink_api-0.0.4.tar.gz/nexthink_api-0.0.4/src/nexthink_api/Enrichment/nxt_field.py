""" Enrichment information for the given object, composed of the name of field to be enriched and the desired value """

from typing import Union
from typing_extensions import Self
from pydantic import BaseModel, Field, field_serializer, model_validator, InstanceOf

from .nxt_field_name import NxtFieldName

__all__ = ["NxtField"]


# TODO: add date string format support for the value property
# Will use the enum value with serialize
class NxtField(BaseModel):
    name: InstanceOf[NxtFieldName]
    value: Union[str, int]
    customValue: str = Field(default=None, exclude=True, repr=False)

    # Add constraints to name
    # If name doesn't contain #, then customValue must be None
    # If name contains #, then customValue must be specified
    @model_validator(mode='after')
    def check_name(self) -> Self:
        if '#' in self.name.value and self.customValue is None:
            raise ValueError("You cannot use a FieldName of type Custom without specifying a customValue.")
        if '#' not in self.name.value and self.customValue is not None:
            raise ValueError("You cannot use a customValue without specifying a FieldName of type Custom.")
        return self

    # return the value of enum when convert to dict
    @field_serializer('name')
    def name(self, value: NxtFieldName):
        return self.get_field_name(value)

    def get_field_name(self, name: NxtFieldName) -> str:
        if self.customValue is not None and '#' in name.value:
            updated_value = name.value.format(self.customValue)
            if len(updated_value) > 64:
                raise ValueError(f"Resulting string exceeds 64 characters: {updated_value}")
            return updated_value
        if '#' in name.value:
            raise ValueError(f"Missing 'customValue' parameter for custom field: {name}")
        return name.value
