import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from ..models import CamelModel, Location, RelationType, Source
from ..types import ObjectId


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


class CompanyDescription(CamelModel):
    long: Optional[str] = Field(
        None,
        description="Company's default description",
        examples=[
            (
                "delphai is an AI and big data analytics software platform that informs "
                "business decisions and validates strategies"
            )
        ],
    )
    short: Optional[str] = Field(
        None,
        description="Truncated version of company's default description",
        examples=["delphai is an AI and big data analytics software platform"],
    )


class CompanyRevenue(CamelModel):
    currency: Optional[str] = Field(
        None, description="Currency of revenue number", examples=["EUR"]
    )
    annual: Optional[int] = Field(
        None, description="Annual revenue number for specified year", examples=[5000000]
    )
    source: Source


CompanyIdentifierCategory = str
CompanyIdentifierSubcategory = str
CompanyIdentifier = Dict[CompanyIdentifierSubcategory, str]


class CompanyMinimal(CamelModel):
    id: ObjectId = Field(
        ..., description="Internal company ID", examples=["5ba391e472cc306cb6d9255e"]
    )
    name: Optional[str] = Field(
        None, description="Name of the company", examples=["delphai"]
    )
    url: Optional[str] = Field(
        None, description="Webpage of the company", examples=["delphai.com"]
    )


class Company(CompanyMinimal):
    descriptions: Optional[Dict[str, CompanyDescription]] = None
    founding_year: Optional[int] = Field(
        None, description="Founding year", examples=[2020]
    )
    headquarters: Optional[Location] = Field(None, description="Company address")
    employee_count: Optional[EmployeeCount] = Field(
        None, description="Number of employees"
    )
    additional_urls: Optional[Dict[str, str]] = Field(
        None, examples=[{"linkedin": "https://www.linkedin.com/company/delphai"}]
    )
    revenue: Optional[Dict[str, CompanyRevenue]] = Field(
        None, description="Company revenue with currency"
    )
    products: Optional[List[str]] = Field(
        None, description="List of company products", examples=[["Software"]]
    )
    identifiers: Optional[Dict[CompanyIdentifierCategory, CompanyIdentifier]] = Field(
        None, description="Object of company identifiers"
    )
    custom_attributes: Optional[Dict[str, Any]] = Field(
        None,
        description="Company custom attributes",
        examples=[{"crmId": 84831, "labels": ["Partner", "Supplier"]}],
    )
    industries: Optional[List[str]] = Field(
        None, examples=[["Software & internet services", "Hardware & IT equipment"]]
    )
    emerging_technologies: Optional[List[str]] = Field(
        None,
        description="Company exposure to a preselected set of emerging technologies",
        examples=[["Artificial intelligence", "Natural language processing"]],
    )
    naics_labels: Optional[List[str]] = Field(
        None,
        description="Sector and subsector North American Industry Classification System codes of the company",
        examples=[
            [
                "41 | Wholesale Trade",
                "416 | Building material and supplies merchant wholesalers",
            ]
        ],
    )
    nace_labels: Optional[List[str]] = Field(
        None,
        description="Statistical classification of economic activities in the European Community for the company",
        examples=[["C28 | Manufacture of machinery & equipment n.e.c."]],
    )
    business_model: Optional[List[str]] = Field(
        None,
        description="Business model of the company",
        examples=[["B2B", "B2C"]],
    )
    ownership: Optional[List[str]] = Field(
        None,
        description="Describes if the company is privately owned or publicly traded",
        examples=[["Private", "Other"]],
    )


class CompaniesSearchResult(CamelModel):
    company: Company
    score: float = Field(default=0, description="Search score", examples=["202.35745"])
    snippets: List[str] = Field(
        default=[],
        description="Snippets containing query keywords",
        examples=[
            [
                "delphai is an AI and big data analytics software platform that informs "
                "business decisions and validates strategies"
            ]
        ],
    )


class CompaniesSearchResults(CamelModel):
    results: List[CompaniesSearchResult]
    total: int = Field(..., description="Number of results", examples=[1337])


class CompanyPeer(CamelModel):
    company: Company
    score: float = Field(default=0, description="Search score", examples=["202.35745"])


class CompanyPeers(CamelModel):
    results: List[CompanyPeer]
    total: int = Field(..., description="Number of results", examples=[5])


class CompanyCustomAttribute(CamelModel):
    type: str = Field(description="Attribute type", examples=["singleSelect"])
    choices: Optional[List[Any]] = Field(None, description="Valid values")
    value: Any = Field(description="Attribute value")


class CompanyCustomAttributes(CamelModel):
    custom_attributes: Dict[str, CompanyCustomAttribute] = Field(
        description="Company custom attributes",
        examples=[
            {
                "crmId": {"type": "singleSelect", "value": 84831},
                "labels": {
                    "type": "multipleSelect",
                    "choices": ["Partner", "Peer", "Provider", "Supplier"],
                    "value": ["Partner", "Supplier"],
                },
            }
        ],
    )


class CompanyCustomAttributeUpdate(CamelModel):
    value: Any = Field(description="Attribute value")
    delete: bool = Field(False, description="Unset attribute")


class CompanyCustomAttributesUpdate(CamelModel):
    custom_attributes: Dict[str, CompanyCustomAttributeUpdate] = Field(
        description="Company custom attributes",
        examples=[
            {
                "crmId": {"value": 84831},
                "labels": {"value": ["Partner", "Supplier"]},
                "notes": {"delete": True},
            }
        ],
    )


class CompanyRelationSource(CamelModel):
    url: str = Field(
        ..., description="URL of the source in which the relation is found"
    )
    date: Optional[datetime.date] = Field(
        None,
        description="Date of source URL in which the relation is found",
        examples=["2023-12-31"],
    )


class CompanyRelation(CamelModel):
    company: CompanyMinimal
    relation_type: str = Field(
        ..., description="Relation with the target company", examples=["client"]
    )
    sources: List[CompanyRelationSource]


class CompanyRelations(CamelModel):
    results: List[CompanyRelation]
    total: int


class CompanyRelationRequest(CamelModel):
    source_company_id: ObjectId
    target_company_id: ObjectId
    relation_type: RelationType


class CompanyRelationCreateRequest(CompanyRelationRequest):
    source_date: datetime.date = Field(
        ...,
        description="Date of source URL in which the relation is found",
        examples=["2023-12-31"],
    )
    source_url: str = Field(
        ..., description="URL of the source in which the relation is found"
    )
    text_chunk: Optional[str] = Field(
        None,
        description="A segment or portion of text from which contains the relevant information that supports the extracted relation",
    )
    input_origin: Optional[str] = Field(
        None,
        description="Input channel of which the given relation is found",
        examples=["News pipeline"],
    )
    confidence: Optional[float] = Field(
        None,
        description="Probability/confidence score from the machine learning model which extracted the given relation",
        examples=[0.9988],
    )
    method: Optional[str] = Field(
        None,
        description="The machine learning approach used to extract the given relation",
        examples=["summarizer"],
    )
