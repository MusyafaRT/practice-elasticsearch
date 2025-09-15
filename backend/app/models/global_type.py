from typing import Generic, Optional, TypeVar
from pydantic.generics import GenericModel

T = TypeVar("T")

class ResponseWrapper(GenericModel, Generic[T]):
    status: str
    message: str
    data: Optional[T] = None


class PaginationMetaData(GenericModel):
    current_page: int
    page_size: int
    total_pages: int
    total_items: int