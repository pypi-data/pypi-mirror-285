from enum import Enum
from typing import List, Optional

from pydantic import ConfigDict, BaseModel, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class HTTPExceptionModel(CamelModel):
    detail: str


class Label(CamelModel):
    name: str = Field(description="Assigned label")
    children: List["Label"] = Field(description="Sublabels")


class Location(CamelModel):
    country: Optional[str] = Field(
        None, description="Company address (country)", examples=["Germany"]
    )
    city: Optional[str] = Field(
        None, description="Company address (city)", examples=["Berlin"]
    )
    continent: Optional[str] = Field(
        None, description="Company address (continent)", examples=["Europe"]
    )
    state: Optional[str] = Field(
        None, description="Company address (state/land)", examples=["Berlin"]
    )
    latitude: Optional[float] = Field(None, examples=[52.5167])
    longitude: Optional[float] = Field(None, examples=[13.3833])
    zip_code: Optional[str] = Field(
        None, description="Company address (ZIP code)", examples=["10999"]
    )


class EmployeeCount(CamelModel):
    min: Optional[int] = Field(
        None, description="Bottom range of the employee count interval", examples=[11]
    )
    max: Optional[int] = Field(
        None, description="Top range of the employee count interval", examples=[50]
    )
    exact: Optional[int] = Field(
        None, description="Exact number for employees", examples=[30]
    )
    range: Optional[str] = Field(
        None,
        description="Employee count interval displayed in delphai",
        examples=["11-50"],
    )


class Source(CamelModel):
    name: str = Field(description="Name of the source")
    credibility_score: float = Field(
        description="Credibility score of source in percentage", examples=[0.60]
    )


class RelationType(str, Enum):
    ACQUISITION = "acquisition"
    PARTIAL_ACQUISITION = "partial_acquisition"
    FUNDING = "funding"
    SUBSIDIARY = "subsidiary"
    DIVESTMENT = "divestment"
    ADVISORY = "advisory"
    COMPETITOR = "competitor"
    CLIENT_SUPPLIER = "client_supplier"
    PARTNERSHIP = "partnership"
    LEGAL_CONFLICT = "legal_conflict"


class Ownership(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
