import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field

from ..models import CamelModel, EmployeeCount, Location, RelationType, Source
from ..types import ObjectId


class CompanyInclude(str, Enum):
    CUSTOM_ATTRIBUTES = "customAttributes"
    CUSTOM_CLASSIFICATION = "customClassification"


class CompanyDescription(CamelModel):
    long: Optional[str] = Field(
        None,
        description="Company's default description",
        examples=[
            (
                "Intelligence Applied, known as Intapp, is a global leader in "
                "cloud-based firm management software, founded in 2000 in Palo Alto, "
                "United States. Specializing in serving partner-led firms across "
                "various sectors like private capital, investment banking, legal, "
                "accounting, and consulting."
            )
        ],
    )
    short: Optional[str] = Field(
        None,
        description="Truncated version of company's default description",
        examples=["Intapp is a global leader in cloud-based firm management software."],
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
        ..., description="Internal company ID", examples=["5ba3b37eb6fa1e372f53d04c"]
    )
    name: Optional[str] = Field(
        None,
        description="Name of the company",
        examples=["Intapp | Intelligence Applied"],
    )
    url: Optional[str] = Field(
        None, description="Webpage of the company", examples=["intapp.com"]
    )


class Company(CompanyMinimal):
    descriptions: Optional[Dict[str, CompanyDescription]] = None
    founding_year: Optional[int] = Field(
        None, description="Founding year", examples=[2000]
    )
    headquarters: Optional[Location] = Field(None, description="Company address")
    employee_count: Optional[EmployeeCount] = Field(
        None, description="Number of employees"
    )
    additional_urls: Optional[Dict[str, str]] = Field(
        None, examples=[{"linkedin": "linkedin.com/company/intapp"}]
    )


class CompanyProfile(Company):
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
        None,
        description="Company exposure to a preselected set of industry labels",
        examples=[["Software & internet services", "Hardware & IT equipment"]],
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
                "51 | Information",
                "513 | Publishing Industries",
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
        examples=[["Public", "Other"]],
    )


class CompanyCreateDescription(CompanyDescription):
    paraphrase: bool = Field(
        default=True,
        description="Boolean flag for paraphrasing of description to ensure copyright-compliance in the case of external descriptions",
    )
    quality_score: Optional[float] = Field(
        default=None, description="Quality score of description returned by the model"
    )


class CompanyCreate(CamelModel):
    id: Optional[ObjectId] = Field(default=None, description="Internal company ID")
    name: Optional[str] = Field(
        None, description="Name of the company", examples=["Intapp"]
    )
    url: Optional[str] = Field(
        default=None, description="Webpage of the company", examples=["intapp.com"]
    )
    founded: Optional[int] = Field(
        None, description="Founding year", examples=[2000], alias="foundingYear"
    )
    headquarters: Optional[Location] = Field(None, description="Company address")
    n_employees: Optional[str] = Field(
        None,
        description="Number of employees",
        examples=["1001-5000"],
        alias="employeeCount",
    )
    descriptions: Optional[Dict[str, CompanyCreateDescription]] = None
    external_description: Optional[str] = Field(
        default="",
        description="An external and therefore non-copyright compliant description that will only be saved in the source tracking table",
    )
    social_media: Optional[Dict[str, str]] = Field(
        None,
        description="Social media links of company",
        examples=[
            {
                "linkedin": "https://www.linkedin.com/company/intapp",
                "facebook": "https://www.facebook.com/intapp",
            }
        ],
    )
    source: Optional[str] = Field(
        default="", description="Source of company data.", examples=["linkedin.com"]
    )
    source_link: Optional[str] = Field(
        default="",
        description="Source URL of company data. This must be the exact page where the information was extracted from",
        examples=["https://www.linkedin.com/company/intapp"],
    )
    added_by: Optional[str] = Field(
        default="",
        description="ID of user adding this information or name of service",
        examples=["ec8ccc64-81dc-4b7b-a72e-daa7172bfae6"],
    )
    overwrite: bool = Field(
        default=False,
        description="Boolean flag if the company information currently present in the company's entry in the companies collection should be forcly overwritten or not",
    )
    enrich: bool = Field(
        default=True,
        description="Send new company to be enriched",
    )


class CompaniesSearchResult(CamelModel):
    company: Company
    score: float = Field(default=0, description="Search score", examples=["202.35745"])
    snippets: List[str] = Field(
        default=[],
        description="Snippets containing query keywords",
        examples=[
            [
                "Intapp is a preferred partner for professional and financial "
                "services firms."
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
    value: Any = Field(..., description="Attribute value")


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
    value: Any = Field(..., description="Attribute value")
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
        ...,
        description="URL of the source in which the relation is found",
        examples=["https://airbridge.nl/sale-of-delphai-to-intapp-nasdaq-inta"],
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
    total: int = Field(..., description="Number of results", examples=[337])


class CompanyRelationRequest(CamelModel):
    source_company_id: ObjectId = Field(
        ..., description="Internal company ID of source company"
    )
    target_company_id: ObjectId = Field(
        ..., description="Internal company ID of company related to source company"
    )
    relation_type: RelationType


class CompanyRelationCreateRequest(CompanyRelationRequest):
    source_date: datetime.date = Field(
        ...,
        description="Date of source URL in which the relation is found",
        examples=["2023-12-31"],
    )
    source_url: str = Field(
        ...,
        description="URL of the source in which the relation is found",
        examples=["https://airbridge.nl/sale-of-delphai-to-intapp-nasdaq-inta"],
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
