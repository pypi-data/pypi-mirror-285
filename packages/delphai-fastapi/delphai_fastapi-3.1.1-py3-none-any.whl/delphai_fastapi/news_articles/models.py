from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import Field

from ..models import CamelModel, Label
from ..types import ObjectId


class NewsArticleType(str, Enum):
    NEWS = "news"
    PRESS_RELEASE = "press release"


class NewsArticle(CamelModel):
    company_id: ObjectId = Field(..., description="Internal company ID")
    url: str = Field(
        ...,
        description="Article URL",
        examples=["https://airbridge.nl/sale-of-delphai-to-intapp-nasdaq-inta"],
    )
    type: NewsArticleType = Field(..., description="Type of article")
    published: datetime = Field(..., description="When the article was published")
    snippet: str = Field(
        ..., description="Snippet of the article mentioning the company"
    )
    language: Optional[str] = Field(
        None,
        description="Original language of the article in ISO 639 code",
        examples=["en"],
    )
    labels: Optional[List[Label]] = None
    title: str = Field(
        ..., description="Article title", examples=["Sale of delphai to Intapp"]
    )
    added: datetime = Field(..., description="When the article was added to delphai")


class NewsArticles(CamelModel):
    results: List[NewsArticle]
    total: int = Field(..., description="Number of results")
