"""Contains a model for a unit"""

from typing import Optional

from pydantic import Field

from aind_slims_api.models.base import SlimsBaseModel


class SlimsUnit(SlimsBaseModel):
    """Model for unit information in SLIMS"""

    name: str = Field(..., alias="unit_name")
    abbreviation: Optional[str] = Field("", alias="unit_abbreviation")
    pk: int = Field(..., alias="unit_pk")

    _slims_table = "Unit"
