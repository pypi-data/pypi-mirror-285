from typing import Literal, Required, TypedDict


class Filter(TypedDict, total=False):
    attribute: Required[str]
    values: list[str]


class Interval(TypedDict):
    end: str
    start: str


class Preset(TypedDict):
    value: Literal[
        "PreviousQuarter",
        "ThisWeek",
        "PreviousWeek",
        "Yesterday",
        "Today",
        "ThisMonth",
        "PreviousMonth",
        "ThisQuarter",
        "ThisYear",
    ]


class FilterValue(TypedDict, total=False):
    label: str
    value: Required[str]


type Measure = Literal["Min", "Max", "Sum", "Percentage", "StdDev", "Average", "Count"]

type DoubleMeasure = Literal["Min", "Max", "Sum", "Percentage", "StdDev", "Average"]

type LongMeasure = Literal["Count"]


class LongAggregateValue(TypedDict, total=False):
    measure: LongMeasure
    value: int


class DoubleAggregateValue(TypedDict, total=False):
    measure: DoubleMeasure
    value: float


class MetricData(TypedDict, total=False):
    aggregates: Required[list[DoubleAggregateValue | LongAggregateValue]]
    id: str


class BooleanField(TypedDict):
    value: bool


class DoubleField(TypedDict):
    value: float


class InstantField(TypedDict):
    value: str


class IntField(TypedDict):
    value: int


class LongField(TypedDict):
    value: int


class StringField(TypedDict):
    value: str


class TimestampField(TypedDict):
    value: str


class UUIDField(TypedDict):
    value: str


class ListField(TypedDict):
    value: list[
        BooleanField
        | DoubleField
        | InstantField
        | IntField
        | LongField
        | StringField
        | TimestampField
        | UUIDField
    ]


type MetricRecordValue = (
    BooleanField
    | DoubleField
    | InstantField
    | IntField
    | ListField
    | LongField
    | StringField
    | TimestampField
    | UUIDField
)


class Field(TypedDict, total=False):
    field: MetricRecordValue
    name: Required[str]


class MetricRecord(TypedDict, total=False):
    fields: list[Field]
    primaryTimestampField: TimestampField
    value: MetricRecordValue


class AggregateMetadata(TypedDict, total=False):
    description: str
    measure: Required[Measure]


class FilterMetadata(TypedDict, total=False):
    description: str
    filterAttribute: Required[str]


class MetricMetadata(TypedDict, total=False):
    aggregations: list[AggregateMetadata]
    description: str
    filters: list[FilterMetadata]
    id: Required[str]
    relatedREcordIds: list[str]


class FieldMetadata(TypedDict):
    description: str
    name: str
    nullable: bool


class MetricRecordMetadata(TypedDict, total=False):
    description: Required[str]
    fieldsMetadata: list[FieldMetadata]
    filters: list[FilterMetadata]
    id: Required[str]
    relatedMetricIds: list[str]
