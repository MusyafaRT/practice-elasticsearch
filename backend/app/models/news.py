from pydantic import BaseModel
from typing import List


class CategoryDistribution(BaseModel):
    category: str
    count: int

class SourceDistribution(BaseModel):
    source: str
    count: int

class TimelinePoint(BaseModel):
    date: str
    count: int

class RegionDistribution(BaseModel):
    region: str
    count: int

class KeywordDistribution(BaseModel):
    keyword: str
    count: int


class AnalyticsOverviewResponse(BaseModel):
    category_distribution: List[CategoryDistribution]
    source_distribution: List[SourceDistribution]
    timeline: List[TimelinePoint]
    region_distribution: List[RegionDistribution]
    top_keywords: List[KeywordDistribution]