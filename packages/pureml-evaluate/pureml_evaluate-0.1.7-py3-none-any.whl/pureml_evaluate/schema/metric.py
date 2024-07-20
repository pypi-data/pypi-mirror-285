import typing
from enum import Enum

from pydantic import BaseModel


class MetricDictEnum(Enum):
    all = "__all__"
    subsets = "__subsets__"


class ColumnTemplate(BaseModel):
    name: str
    value: str


class MetricTemplate(BaseModel):
    name: str
    category: str
    value: typing.Any = None
    status: bool = None
    columns_sensitive: typing.List[ColumnTemplate] = None


column_all = ColumnTemplate(
    name=MetricDictEnum.all.value, value=MetricDictEnum.all.value
)


class MetricResult(BaseModel):
    column: typing.List[ColumnTemplate] = None  # [column_all.dict()]
    metric: typing.List[MetricTemplate] = None


class MetricAllResult(BaseModel):
    __all__: MetricResult = None
    __subsets__: MetricResult = None
