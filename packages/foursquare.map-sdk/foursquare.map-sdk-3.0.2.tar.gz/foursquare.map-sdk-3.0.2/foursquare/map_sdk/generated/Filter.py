# type: ignore

from __future__ import annotations

from enum import Enum
from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, Field, RootModel, constr


class Filter1(BaseModel):
    id: str = Field(..., description="Unique id for this filter")
    name: List[str] = Field(
        ...,
        description="Names of the fields that this filter applies to (respectively to dataIds)",
    )
    type: Literal["range"] = Field(
        ...,
        description="Range filter specifies sets min and max values for a numeric field",
    )
    data_id: List[str] = Field(
        ..., alias="dataId", description="Dataset ids that this filter applies to"
    )
    view: Literal["side"] = Field(
        "side",
        description="Where the filter should be displayed: has to be side for non-timeRange filters",
    )
    value: Optional[List[float]] = Field(..., description="Range of the filter")


class View(Enum):
    side = "side"
    enlarged = "enlarged"
    minified = "minified"


class AnimationWindow(Enum):
    free = "free"
    incremental = "incremental"
    point = "point"
    interval = "interval"


class Type(Enum):
    integer = "integer"
    real = "real"
    string = "string"
    boolean = "boolean"
    date = "date"


class YAxis(BaseModel):
    name: str = Field(..., description="Name of the field")
    type: Type = Field(..., description="Type of the field")


class SyncTimelineMode(Enum):
    number_0 = 0
    number_1 = 1


class Type1(Enum):
    histogram = "histogram"
    line_chart = "lineChart"


class Aggregation(Enum):
    count = "COUNT"
    sum = "SUM"
    mean = "MEAN"
    max = "MAX"
    min = "MIN"
    deviation = "DEVIATION"
    variance = "VARIANCE"
    median = "MEDIAN"
    p05 = "P05"
    p25 = "P25"
    p50 = "P50"
    p75 = "P75"
    p95 = "P95"
    mode = "MODE"
    unique = "UNIQUE"
    merge = "MERGE"


class PlotType(BaseModel):
    type: Optional[Type1] = "histogram"
    interval: Optional[
        constr(
            pattern=r"^([0-9]+)-(year|month|week|day|hour|minute|second|millisecond)$"
        )
    ] = Field(
        None,
        description="Time interval for the time axis aggregation. Should be in the form (number)-(interval), where interval is one of: year, month, week, day, hour, minute, second, millisecond, e.g 1-day, 2-week, 3-month, 4-year",
    )
    aggregation: Optional[Aggregation] = Field(
        "SUM", description="Aggregation function for the time axis"
    )
    default_time_format: Optional[str] = Field(
        None,
        alias="defaultTimeFormat",
        description="Default time format for the time axis. For the syntax check these docs: https://momentjs.com/docs/#/displaying/format/",
    )


class Geometry(BaseModel):
    type: Literal["Polygon"]
    coordinates: List[List[List[float]]]


class Geometry1(BaseModel):
    type: Literal["MultiPolygon"]
    coordinates: List[List[List[List[float]]]]


class Value(BaseModel):
    type: Literal["Feature"]
    properties: Optional[Any] = None
    geometry: Union[Geometry, Geometry1]
    id: Optional[str] = Field(None, description="Unique id of the polygon")


class DataId(RootModel[List[str]]):
    root: List[str] = Field(..., description="Dataset ids that this filter applies to")


class Id(RootModel[str]):
    root: str = Field(..., description="Unique id for this filter")


class Name(RootModel[List[str]]):
    root: List[str] = Field(
        ...,
        description="Names of the fields that this filter applies to (respectively to dataIds)",
    )


class ViewModel(RootModel[Literal["side"]]):
    root: Literal["side"] = Field(
        ...,
        description="Where the filter should be displayed: has to be side for non-timeRange filters",
    )


class Filter2(BaseModel):
    id: Id
    name: Name
    type: Literal["timeRange"] = Field(
        ..., description="Time range filter specifies sets min and max values"
    )
    data_id: DataId = Field(..., alias="dataId")
    view: Optional[View] = Field(
        "side",
        description="Where the filter should be displayed: side, enlarged or minified",
    )
    value: Optional[List[float]] = Field(..., description="Range of the filter")
    animation_window: Optional[AnimationWindow] = Field(
        "free", alias="animationWindow", description="Animation window type"
    )
    y_axis: Optional[Union[Any, YAxis]] = Field(
        None, alias="yAxis", description="Dimension field for the y axis"
    )
    speed: Optional[float] = Field(1, description="Speed of the animation")
    synced_with_layer_timeline: Optional[bool] = Field(
        None,
        alias="syncedWithLayerTimeline",
        description="Whether the filter should be synced with the layer timeline",
    )
    sync_timeline_mode: Optional[SyncTimelineMode] = Field(
        None,
        alias="syncTimelineMode",
        description="Sync timeline mode: 0 (sync with range start) or 1 (sync with range end)",
    )
    invert_trend_color: Optional[bool] = Field(
        None,
        alias="invertTrendColor",
        description="Whether the trend color should be inverted",
    )
    timezone: Optional[str] = Field(
        None,
        description="Timezone (TZ identifier) for displaying time, e.g. America/New_York",
    )
    plot_type: Optional[PlotType] = Field(
        default_factory=lambda: PlotType.model_validate({"type": "histogram"}),
        alias="plotType",
        description="Type of plot to show in the enlarged panel",
    )


class Filter3(BaseModel):
    id: Id
    name: Name
    type: Literal["select"] = Field(
        ..., description="Select filter with a single boolean value"
    )
    data_id: DataId = Field(..., alias="dataId")
    view: Optional[ViewModel] = None
    value: Optional[bool] = Field(..., description="Selected or not")


class Filter4(BaseModel):
    id: Id
    name: Name
    type: Literal["multiSelect"] = Field(
        ..., description="Multi select filter with a list of values"
    )
    data_id: DataId = Field(..., alias="dataId")
    view: Optional[ViewModel] = None
    value: Optional[List[str]] = Field(..., description="List of selected values")


class Filter5(BaseModel):
    id: Id
    name: Name
    type: Literal["polygon"] = Field(..., description="Polygon selection on the map")
    data_id: DataId = Field(..., alias="dataId")
    view: Optional[ViewModel] = None
    value: Optional[Value] = Field(
        ..., description="Polygon selection on a map (GeoJSON format)"
    )
    layer_id: Optional[List[str]] = Field(
        None, alias="layerId", description="Layer ids that this filter applies to"
    )


class Filter(RootModel[Union[Filter1, Filter2, Filter3, Filter4, Filter5]]):
    root: Union[Filter1, Filter2, Filter3, Filter4, Filter5] = Field(
        ..., title="Filter"
    )
