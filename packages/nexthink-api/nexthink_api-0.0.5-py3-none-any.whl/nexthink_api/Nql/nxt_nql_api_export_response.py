"""
Export identifier to be used in the "status" operation to know the state
of the export and to retrieve the URL of the file with the results.
"""

from typing import Annotated
from pydantic import BaseModel, Field

__all__ = ["NxtNqlApiExportResponse"]


class NxtNqlApiExportResponse(BaseModel):
    exportId: Annotated[
        str,
        Field(
            min_length=1
        )
    ]
