# type: ignore

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, RootModel, constr


class SelectionMode(Enum):
    cell = "cell"
    row = "row"
    column = "column"
    row_column = "rowColumn"


class Signals(BaseModel):
    type: Literal["filter"]
    dataset_id: str = Field(
        ...,
        alias="datasetId",
        description="The ID of the *other* dataset that should be cross-filtered.",
    )
    field_names: Dict[str, str] = Field(
        ..., alias="fieldNames", description="The field names in a filter."
    )


class Signals1(BaseModel):
    type: Literal["parameter"]
    dataset_id: str = Field(
        ...,
        alias="datasetId",
        description="The ID of the *other* dataset that should be cross-filtered.",
    )
    parameter_keys: Dict[str, str] = Field(
        ...,
        alias="parameterKeys",
        description="The dynamic parameter key names in a SQL dataset",
    )


class CrossFilter(BaseModel):
    enabled: bool
    selection_mode: SelectionMode = Field(..., alias="selectionMode")
    value: Dict[str, Union[float, str]] = Field(
        ..., description="The selected values of the originating cross filter."
    )
    signals: List[Union[Signals, Signals1]]
    type: Literal["heatmapChart"]


class FieldModel(BaseModel):
    name: str = Field(..., description="The name of the field.")
    type: str = Field(..., description="The type of the field.")


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


class Axis(BaseModel):
    field: Optional[FieldModel] = Field(
        ..., description="The field to use for the axis."
    )
    aggregation: Optional[Aggregation] = Field(
        ...,
        description="The aggregation function for the axis. Must be one of: COUNT, SUM, MEAN, MAX, MIN, DEVIATION, VARIANCE, MEDIAN, P05, P25, P50, P75, P95, MODE, UNIQUE, MERGE",
    )
    title: Optional[str] = Field(..., description="The title of the axis.")
    benchmark: Optional[str] = Field(
        None, description="The field value to use as the benchmark for the axis."
    )
    enable_grid_line: Optional[bool] = Field(
        None,
        alias="enableGridLine",
        description="Whether to show grid lines for the axis.",
    )


class ChartDisplay(BaseModel):
    show_total: Optional[bool] = Field(
        None, alias="showTotal", description="Whether to show the total value."
    )
    format: Optional[str] = Field(None, description="The format to use for the value.")


class Metric(BaseModel):
    id: str = Field(..., description="The unique id of the metric.")
    label: str = Field(..., description="The label of the metric.")
    data_id: str = Field(
        ..., alias="dataId", description="The id of the dataset to use for the metric."
    )
    expression: str = Field(..., description="The expression to use for the metric.")
    sanitized_expression: str = Field(
        ...,
        alias="sanitizedExpression",
        description="The sanitized expression to use for the metric.",
    )


class Chart1(BaseModel):
    id: str = Field(..., description="The unique id of the chart.")
    title: str = Field(..., description="The title of the chart.")
    data_id: Optional[str] = Field(
        ..., alias="dataId", description="The id of the dataset to use for the chart."
    )
    apply_filters: Optional[bool] = Field(
        False,
        alias="applyFilters",
        description="Whether to apply filters to the chart.",
    )
    cross_filter: Optional[CrossFilter] = Field(
        None,
        alias="crossFilter",
        description="Whether to have cross filtering defined for the chart.",
    )
    type: Literal["bigNumber"] = Field(
        ...,
        description="The type of the chart. Must be one of: bigNumber, horizontalBar, lineChart, barChart, layerChart, heatmapChart, pivotTable",
    )
    axis: Optional[Axis] = Field(
        None, description="The axis configuration for the chart."
    )
    chart_display: Optional[ChartDisplay] = Field(
        {}, alias="chartDisplay", description="The display configuration for the chart."
    )
    metric: Optional[Metric] = Field(
        None, description="The metric to use for the chart."
    )
    use_metric: Optional[bool] = Field(
        None, alias="useMetric", description="Whether to use a metric for the chart."
    )


class Aggregation1(Enum):
    numeric_bin = "numericBin"
    time_bin = "timeBin"
    unique_bin = "uniqueBin"


class ColorBy(Enum):
    field_ = ""
    y_axis = "Y-Axis"
    group_by = "GroupBy"


class Sort(Enum):
    data_order = "dataOrder"
    ascending = "ascending"
    descending = "descending"
    alpha_asc = "alphaAsc"
    alpha_desc = "alphaDesc"
    manual = "manual"


class Type(Enum):
    sequential = "sequential"
    qualitative = "qualitative"
    diverging = "diverging"
    cyclical = "cyclical"
    custom = "custom"
    ordinal = "ordinal"
    custom_ordinal = "customOrdinal"


class ColorBy1(Enum):
    y_axis = "Y-Axis"
    group_by = "GroupBy"
    field_ = ""


class Tooltip(BaseModel):
    show_percentage_change: Optional[bool] = Field(
        None,
        alias="showPercentageChange",
        description="Whether to show the percentage change in the tooltip.",
    )


class ColorBy2(Enum):
    x_axis = "X-Axis"
    group_by = "GroupBy"
    field_ = ""


class VizMode(Enum):
    chart = "CHART"
    table = "TABLE"


class TableVizModeConfig(BaseModel):
    values_field_display_name: str = Field(
        ...,
        alias="valuesFieldDisplayName",
        description="The display name for the value field in table viz mode, which is used as a table column header",
    )
    group_by_field_id: str = Field(
        ...,
        alias="groupByFieldId",
        description="The id of the sql dataset query parameters field to lookup the value from in table viz mode, which is used as a table column header",
    )
    fallback_x_axis_labels: List[str] = Field(
        ..., alias="fallbackXAxisLabels", description="The fallback x axis labels"
    )


class LabelFormatMode(Enum):
    value_only = "valueOnly"
    group_by_name_and_value = "groupByNameAndValue"


class ColorBy3(Enum):
    value = "value"
    field_ = ""


class Sort1(BaseModel):
    mode: Literal["manual"]
    manual_order: List[Union[str, float]] = Field(..., alias="manualOrder")


class Mode(Enum):
    data_order = "dataOrder"
    ascending = "ascending"
    descending = "descending"


class Sort2(BaseModel):
    mode: Mode


class PivotRow(BaseModel):
    label: Optional[str] = None
    field_name: str = Field(..., alias="fieldName")
    type: Optional[str] = None
    show_totals: Optional[bool] = Field(None, alias="showTotals")
    sort: Optional[Union[Sort1, Sort2]] = None


class Aggregation2(Enum):
    sum = "sum"
    count = "count"
    average = "average"
    min = "min"
    max = "max"


class PivotValue(BaseModel):
    label: Optional[str] = None
    field_name: str = Field(..., alias="fieldName")
    type: Optional[str] = None
    aggregation: Aggregation2


class PivotFilter(BaseModel):
    field_name: str = Field(..., alias="fieldName")
    values: Optional[List[str]] = None
    label: Optional[str] = None


class Scope(Enum):
    dataset_panel = "datasetPanel"
    pivot_rows = "pivotRows"
    pivot_columns = "pivotColumns"
    pivot_values = "pivotValues"
    pivot_filters = "pivotFilters"


class AdditionalField(BaseModel):
    label: Optional[str] = None
    field_name: str = Field(..., alias="fieldName")
    type: Optional[str] = None
    scopes: Optional[List[Scope]] = ["pivotValues"]


class ChartDisplay5(BaseModel):
    show_in_tooltip: Optional[bool] = Field(
        None,
        alias="showInTooltip",
        description="Whether to show the chart in the tooltip.",
    )
    id_field: Optional[str] = Field(
        None,
        alias="idField",
        description="The id field to filter the chart data by when hovering an element.",
    )
    format: Optional[str] = Field(None, description="The format to use for the chart.")
    interval: Optional[
        constr(
            pattern=r"^([0-9]+)-(year|month|week|day|hour|minute|second|millisecond)$"
        )
    ] = Field(
        None,
        description="Time interval to aggregate by. Should be in the form (number)-(interval), where interval is one of: year, month, week, day, hour, minute, second, millisecond, e.g 1-day, 2-week, 3-month, 4-year",
    )


class SortBy(Enum):
    natural = "NATURAL"
    category = "CATEGORY"
    value = "VALUE"


class ColorBy4(Enum):
    y_axis = "Y-Axis"
    field_ = ""


class ApplyFilters(RootModel[bool]):
    root: bool = Field(..., description="Whether to apply filters to the chart.")


class Aggregation3(Enum):
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


class AggregationModel(RootModel[Optional[Aggregation3]]):
    root: Optional[Aggregation3] = Field(
        ...,
        description="The aggregation function for the axis. Must be one of: COUNT, SUM, MEAN, MAX, MIN, DEVIATION, VARIANCE, MEDIAN, P05, P25, P50, P75, P95, MODE, UNIQUE, MERGE",
    )


class Benchmark(RootModel[Optional[str]]):
    root: Optional[str] = Field(
        ..., description="The field value to use as the benchmark for the axis."
    )


class EnableGridLine(RootModel[bool]):
    root: bool = Field(..., description="Whether to show grid lines for the axis.")


class FieldModel1(RootModel[Optional[FieldModel]]):
    root: Optional[FieldModel] = Field(
        ..., description="The field to use for the axis."
    )


class Field0(BaseModel):
    name: str = Field(..., description="The name of the field.")
    type: str = Field(..., description="The type of the field.")


class Title(RootModel[Optional[str]]):
    root: Optional[str] = Field(..., description="The title of the axis.")


class Signals2(BaseModel):
    type: Literal["filter"]
    dataset_id: str = Field(
        ...,
        alias="datasetId",
        description="The ID of the *other* dataset that should be cross-filtered.",
    )
    field_names: Dict[str, str] = Field(
        ..., alias="fieldNames", description="The field names in a filter."
    )


class Signals3(BaseModel):
    type: Literal["parameter"]
    dataset_id: str = Field(
        ...,
        alias="datasetId",
        description="The ID of the *other* dataset that should be cross-filtered.",
    )
    parameter_keys: Dict[str, str] = Field(
        ...,
        alias="parameterKeys",
        description="The dynamic parameter key names in a SQL dataset",
    )


class CrossFilter1(BaseModel):
    enabled: bool
    selection_mode: SelectionMode = Field(..., alias="selectionMode")
    value: Dict[str, Union[float, str]] = Field(
        ..., description="The selected values of the originating cross filter."
    )
    signals: List[Union[Signals2, Signals3]]
    type: Literal["heatmapChart"]


class CrossFilterModel(RootModel[CrossFilter1]):
    root: CrossFilter1 = Field(
        ..., description="Whether to have cross filtering defined for the chart."
    )


class DataId(RootModel[Optional[str]]):
    root: Optional[str] = Field(
        ..., description="The id of the dataset to use for the chart."
    )


class Id(RootModel[str]):
    root: str = Field(..., description="The unique id of the chart.")


class TitleModel(RootModel[str]):
    root: str = Field(..., description="The title of the chart.")


class Items(RootModel[str]):
    root: str


class SortModel(Enum):
    data_order = "dataOrder"
    ascending = "ascending"
    descending = "descending"
    alpha_asc = "alphaAsc"
    alpha_desc = "alphaDesc"
    manual = "manual"


class Aggregation4(Enum):
    numeric_bin = "numericBin"
    time_bin = "timeBin"
    unique_bin = "uniqueBin"


class AggregationModel1(RootModel[Optional[Aggregation4]]):
    root: Optional[Aggregation4] = Field(
        ...,
        description="The aggregation function for the axis. Must be one of: numericBin, timeBin, uniqueBin",
    )


class BenchmarkModel(RootModel[str]):
    root: str = Field(
        ..., description="The field value to use as the benchmark for the axis."
    )


class FieldModel2(RootModel[Optional[Field0]]):
    root: Optional[Field0] = Field(..., description="The field to use for the axis.")


class Interval(
    RootModel[
        constr(
            pattern=r"^([0-9]+)-(year|month|week|day|hour|minute|second|millisecond)$"
        )
    ]
):
    root: constr(
        pattern=r"^([0-9]+)-(year|month|week|day|hour|minute|second|millisecond)$"
    ) = Field(
        ...,
        description="Time interval for the aggregation in case of a time axis. Should be in the form (number)-(interval), where interval is one of: year, month, week, day, hour, minute, second, millisecond, e.g 1-day, 2-week, 3-month, 4-year",
    )


class TitleModel1(RootModel[Optional[str]]):
    root: Optional[str] = Field(..., description="The title of the axis.")


class Field0Model(BaseModel):
    field: FieldModel1
    aggregation: AggregationModel
    title: Optional[Title] = None
    benchmark: Optional[Benchmark] = None
    enable_grid_line: Optional[EnableGridLine] = Field(None, alias="enableGridLine")


class Sort3(BaseModel):
    mode: Literal["manual"]
    manual_order: List[Union[str, float]] = Field(..., alias="manualOrder")


class Sort4(BaseModel):
    mode: Mode


class ItemsModel(BaseModel):
    label: Optional[str] = None
    field_name: str = Field(..., alias="fieldName")
    type: Optional[str] = None
    show_totals: Optional[bool] = Field(None, alias="showTotals")
    sort: Optional[Union[Sort3, Sort4]] = None


class Sort5(BaseModel):
    mode: Literal["manual"]
    manual_order: List[Union[str, float]] = Field(..., alias="manualOrder")


class Sort6(BaseModel):
    mode: Mode


class SortModel1(RootModel[Union[Sort5, Sort6]]):
    root: Union[Sort5, Sort6]


class Format(RootModel[str]):
    root: str = Field(..., description="The format to use for the chart.")


class IdField(RootModel[str]):
    root: str = Field(
        ...,
        description="The id field to filter the chart data by when hovering an element.",
    )


class ShowInTooltip(RootModel[bool]):
    root: bool = Field(..., description="Whether to show the chart in the tooltip.")


class LayerId(RootModel[str]):
    root: str = Field(
        ..., description="The id of the layer which the charts are shown for."
    )


class TypeModel(RootModel[Literal["layerChart"]]):
    root: Literal["layerChart"] = Field(
        ...,
        description="The type of the chart. Must be one of: bigNumber, horizontalBar, lineChart, barChart, layerChart, heatmapChart, pivotTable",
    )


class ApplyFiltersModel(RootModel[bool]):
    root: bool = Field(..., description="Whether to apply the filters to the chart.")


class ChartDisplayModel(BaseModel):
    show_in_tooltip: Optional[ShowInTooltip] = Field(None, alias="showInTooltip")
    id_field: Optional[IdField] = Field(None, alias="idField")
    format: Optional[Format] = None
    include_internal: Optional[bool] = Field(
        None, alias="includeInternal", description="Whether to include internal flows."
    )
    num_entries: Optional[float] = Field(
        None,
        alias="numEntries",
        description="The number of entries to show in the chart.",
    )


class XAxis(BaseModel):
    field: FieldModel1
    aggregation: AggregationModel
    title: Optional[Title] = None
    benchmark: Optional[Benchmark] = None
    enable_grid_line: Optional[EnableGridLine] = Field(None, alias="enableGridLine")


class YAxis(BaseModel):
    title: Optional[str] = Field(..., description="The title of the axis.")
    field: Optional[Field0] = Field(..., description="The field to use for the axis.")
    aggregation: Optional[Aggregation1] = Field(
        ...,
        description="The aggregation function for the axis. Must be one of: numericBin, timeBin, uniqueBin",
    )
    interval: Optional[
        constr(
            pattern=r"^([0-9]+)-(year|month|week|day|hour|minute|second|millisecond)$"
        )
    ] = Field(
        None,
        description="Time interval for the aggregation in case of a time axis. Should be in the form (number)-(interval), where interval is one of: year, month, week, day, hour, minute, second, millisecond, e.g 1-day, 2-week, 3-month, 4-year",
    )
    benchmark: Optional[str] = Field(
        None, description="The field value to use as the benchmark for the axis."
    )
    enable_grid_line: Optional[bool] = Field(
        None,
        alias="enableGridLine",
        description="Whether to show grid lines for the axis.",
    )


class GroupBy(BaseModel):
    title: Optional[TitleModel1] = None
    field: FieldModel2
    aggregation: AggregationModel1
    interval: Optional[Interval] = None
    benchmark: Optional[BenchmarkModel] = None
    enable_grid_line: Optional[EnableGridLine] = Field(None, alias="enableGridLine")


class ColorRange(BaseModel):
    name: Optional[str] = Field("Unnamed", description="The name of the color range.")
    type: Optional[Type] = Field(
        "sequential",
        description="The type of the color range. Must be one of: sequential, qualitative, diverging, cyclical, custom, ordinal, customOrdinal",
    )
    category: Optional[str] = "Unnamed"
    colors: List[str]
    reversed: Optional[bool] = None
    color_map: Optional[
        List[List[Union[Optional[Union[str, float, List[str]]], Items]]]
    ] = Field(None, alias="colorMap")
    color_legends: Optional[Dict[str, str]] = Field(None, alias="colorLegends")


class ChartDisplay1(BaseModel):
    sort: Optional[Sort] = Field(None, description="The sort type for the chart.")
    sort_group_by: Optional[SortModel] = Field(
        None, alias="sortGroupBy", description="The sort type for the group by axis."
    )
    number_shown: Optional[float] = Field(
        None,
        alias="numberShown",
        description="The number of bars to show in the chart.",
    )
    display_vertical: Optional[bool] = Field(
        None,
        alias="displayVertical",
        description="Whether to display the chart vertically.",
    )
    color_range: Optional[ColorRange] = Field(
        default_factory=lambda: ColorRange.model_validate(
            {
                "name": "Uber Viz Qualitative",
                "type": "qualitative",
                "category": "Uber",
                "colors": [
                    "#12939A",
                    "#DDB27C",
                    "#88572C",
                    "#FF991F",
                    "#F15C17",
                    "#223F9A",
                    "#DA70BF",
                    "#125C77",
                    "#4DC19C",
                    "#776E57",
                ],
            }
        ),
        alias="colorRange",
        description="The color range for the chart.",
    )
    format: Optional[str] = Field(None, description="The format to use for the value.")
    show_legend: Optional[bool] = Field(
        None, alias="showLegend", description="Whether to show the legend."
    )
    enable_legend_checkbox_mode: Optional[bool] = Field(
        True,
        alias="enableLegendCheckboxMode",
        description="Whether the legend should allow toggling the visibility of each data series.",
    )
    hint: Optional[str] = Field(None, description="Add a hint for the chart.")


class Chart2(BaseModel):
    id: Id
    title: TitleModel
    data_id: Optional[DataId] = Field(..., alias="dataId")
    apply_filters: Optional[ApplyFilters] = Field(None, alias="applyFilters")
    cross_filter: Optional[CrossFilterModel] = Field(None, alias="crossFilter")
    type: Literal["horizontalBar"] = Field(
        ...,
        description="The type of the chart. Must be one of: bigNumber, horizontalBar, lineChart, barChart, layerChart, heatmapChart, pivotTable",
    )
    x_axis: XAxis = Field(
        ..., alias="xAxis", description="The x axis configuration for the chart."
    )
    y_axis: YAxis = Field(
        ..., alias="yAxis", description="The y axis configuration for the chart."
    )
    group_by: Optional[GroupBy] = Field(
        None,
        alias="groupBy",
        description="The group by axis configuration for the chart.",
    )
    color_by: Optional[ColorBy] = Field(
        "Y-Axis", alias="colorBy", description="The color by option for the chart."
    )
    num_groups: Optional[Union[float, str]] = Field(
        10,
        alias="numGroups",
        description="The number of groups to show in the chart. Use ALL to show all groups.",
    )
    chart_display: Optional[ChartDisplay1] = Field({}, alias="chartDisplay")


class XAxis1(BaseModel):
    title: Optional[TitleModel1] = None
    field: FieldModel2
    aggregation: AggregationModel1
    interval: Optional[Interval] = None
    benchmark: Optional[BenchmarkModel] = None
    enable_grid_line: Optional[EnableGridLine] = Field(None, alias="enableGridLine")


class YAxis1(BaseModel):
    field: FieldModel1
    aggregation: AggregationModel
    title: Optional[Title] = None
    benchmark: Optional[Benchmark] = None
    enable_grid_line: Optional[EnableGridLine] = Field(None, alias="enableGridLine")
    y_anchor: Optional[Union[Any, float]] = Field(
        None,
        alias="yAnchor",
        description="The y-axis number value at which to show a horizontal anchor line.",
    )


class YAxis2(Field0Model):
    y_anchor: Optional[Union[Any, float]] = Field(
        None,
        alias="yAnchor",
        description="The y-axis number value at which to show a horizontal anchor line.",
    )


class YAxis3(BaseModel):
    title: Optional[TitleModel1] = None
    field: FieldModel2
    aggregation: AggregationModel1
    interval: Optional[Interval] = None
    benchmark: Optional[BenchmarkModel] = None
    enable_grid_line: Optional[EnableGridLine] = Field(None, alias="enableGridLine")


class Value(BaseModel):
    field: FieldModel1
    aggregation: AggregationModel
    title: Optional[Title] = None
    benchmark: Optional[Benchmark] = None
    enable_grid_line: Optional[EnableGridLine] = Field(None, alias="enableGridLine")


class DefaultFieldSortingItem(BaseModel):
    field_name: str = Field(..., alias="fieldName")


class Chart6(BaseModel):
    id: Id
    title: TitleModel
    data_id: Optional[DataId] = Field(..., alias="dataId")
    apply_filters: Optional[ApplyFilters] = Field(None, alias="applyFilters")
    cross_filter: Optional[CrossFilterModel] = Field(None, alias="crossFilter")
    type: Literal["pivotTable"] = Field(
        ...,
        description="The type of the chart. Must be one of: bigNumber, horizontalBar, lineChart, barChart, layerChart, heatmapChart, pivotTable",
    )
    pivot_rows: List[PivotRow] = Field(..., alias="pivotRows")
    pivot_columns: List[ItemsModel] = Field(..., alias="pivotColumns")
    pivot_values: List[PivotValue] = Field(..., alias="pivotValues")
    pivot_filters: Optional[List[PivotFilter]] = Field(None, alias="pivotFilters")
    additional_fields: Optional[List[AdditionalField]] = Field(
        None, alias="additionalFields"
    )
    default_field_sorting: Optional[List[DefaultFieldSortingItem]] = Field(
        None, alias="defaultFieldSorting"
    )


class YAxis4(BaseModel):
    field: FieldModel1
    aggregation: AggregationModel
    title: Optional[Title] = None
    benchmark: Optional[Benchmark] = None
    enable_grid_line: Optional[EnableGridLine] = Field(None, alias="enableGridLine")


class Chart7(BaseModel):
    id: Id
    title: TitleModel
    type: Literal["layerChart"] = Field(
        ...,
        description="The type of the chart. Must be one of: bigNumber, horizontalBar, lineChart, barChart, layerChart, heatmapChart, pivotTable",
    )
    layer_chart_type: Literal["TIME_SERIES"] = Field(
        ...,
        alias="layerChartType",
        description="The tooltip chart type. Must be one of TIME_SERIES, HEXTILE_TIME_SERIES, BREAKDOWN_BY_CATEGORY, FLOW_TOP_ORIGINS, FLOW_TOP_DESTS",
    )
    layer_id: str = Field(
        ...,
        alias="layerId",
        description="The id of the layer which the charts are shown for.",
    )
    chart_display: Optional[ChartDisplay5] = Field(
        {}, alias="chartDisplay", description="The display configuration for the chart."
    )
    apply_filters: Optional[bool] = Field(
        None,
        alias="applyFilters",
        description="Whether to apply the filters to the chart.",
    )
    x_axis: XAxis1 = Field(
        ..., alias="xAxis", description="The x axis configuration for the chart."
    )
    y_axis: YAxis4 = Field(
        ..., alias="yAxis", description="The y axis configuration for the chart."
    )


class ChartDisplay6(BaseModel):
    show_in_tooltip: Optional[ShowInTooltip] = Field(None, alias="showInTooltip")
    id_field: Optional[IdField] = Field(None, alias="idField")
    format: Optional[Format] = None


class Chart8(BaseModel):
    id: Id
    title: TitleModel
    type: TypeModel
    layer_chart_type: Literal["HEXTILE_TIME_SERIES"] = Field(
        ...,
        alias="layerChartType",
        description="The tooltip chart type. Must be one of TIME_SERIES, HEXTILE_TIME_SERIES, BREAKDOWN_BY_CATEGORY, FLOW_TOP_ORIGINS, FLOW_TOP_DESTS",
    )
    layer_id: LayerId = Field(..., alias="layerId")
    chart_display: ChartDisplay6 = Field(
        ...,
        alias="chartDisplay",
        description="The display configuration for the chart.",
    )
    apply_filters: Optional[bool] = Field(
        None,
        alias="applyFilters",
        description="Whether to apply the filters to the chart.",
    )
    y_axis: YAxis4 = Field(
        ..., alias="yAxis", description="The y axis configuration for the chart."
    )


class Axis1(BaseModel):
    field: FieldModel1
    aggregation: AggregationModel
    title: Optional[Title] = None
    benchmark: Optional[Benchmark] = None
    enable_grid_line: Optional[EnableGridLine] = Field(None, alias="enableGridLine")


class ChartDisplay8(BaseModel):
    show_in_tooltip: Optional[ShowInTooltip] = Field(None, alias="showInTooltip")
    id_field: Optional[IdField] = Field(None, alias="idField")
    format: Optional[Format] = None
    include_internal: Optional[bool] = Field(
        None, alias="includeInternal", description="Whether to include internal flows."
    )
    num_entries: Optional[float] = Field(
        None,
        alias="numEntries",
        description="The number of entries to show in the chart.",
    )


class Chart10(BaseModel):
    id: Id
    title: TitleModel
    type: TypeModel
    layer_chart_type: Literal["FLOW_TOP_DESTS"] = Field(
        ...,
        alias="layerChartType",
        description="The tooltip chart type. Must be one of TIME_SERIES, HEXTILE_TIME_SERIES, BREAKDOWN_BY_CATEGORY, FLOW_TOP_ORIGINS, FLOW_TOP_DESTS",
    )
    layer_id: LayerId = Field(..., alias="layerId")
    chart_display: Optional[ChartDisplay8] = Field(
        {}, alias="chartDisplay", description="The display configuration for the chart."
    )
    apply_filters: Optional[ApplyFiltersModel] = Field(None, alias="applyFilters")


class Chart11(BaseModel):
    id: Id
    title: TitleModel
    type: TypeModel
    layer_chart_type: Literal["FLOW_TOP_ORIGINS"] = Field(
        ...,
        alias="layerChartType",
        description="The tooltip chart type. Must be one of TIME_SERIES, HEXTILE_TIME_SERIES, BREAKDOWN_BY_CATEGORY, FLOW_TOP_ORIGINS, FLOW_TOP_DESTS",
    )
    layer_id: LayerId = Field(..., alias="layerId")
    chart_display: Optional[ChartDisplayModel] = Field(None, alias="chartDisplay")
    apply_filters: Optional[ApplyFiltersModel] = Field(None, alias="applyFilters")


class ColorRangeModel(BaseModel):
    name: Optional[str] = Field("Unnamed", description="The name of the color range.")
    type: Optional[Type] = Field(
        "sequential",
        description="The type of the color range. Must be one of: sequential, qualitative, diverging, cyclical, custom, ordinal, customOrdinal",
    )
    category: Optional[str] = "Unnamed"
    colors: List[str]
    reversed: Optional[bool] = None
    color_map: Optional[
        List[List[Union[Optional[Union[str, float, List[str]]], Items]]]
    ] = Field(None, alias="colorMap")
    color_legends: Optional[Dict[str, str]] = Field(None, alias="colorLegends")


class ChartDisplay2(BaseModel):
    color_range: Optional[ColorRangeModel] = Field(
        default_factory=lambda: ColorRangeModel.model_validate(
            {
                "name": "Uber Viz Qualitative",
                "type": "qualitative",
                "category": "Uber",
                "colors": [
                    "#12939A",
                    "#DDB27C",
                    "#88572C",
                    "#FF991F",
                    "#F15C17",
                    "#223F9A",
                    "#DA70BF",
                    "#125C77",
                    "#4DC19C",
                    "#776E57",
                ],
            }
        ),
        alias="colorRange",
        description="The color range for the chart.",
    )
    sort: Optional[SortModel] = Field(None, description="The sort type for the chart.")
    format_tooltip: Optional[str] = Field(
        None, alias="formatTooltip", description="The format to use for the tooltip."
    )
    format_x_axis: Optional[str] = Field(
        None, alias="formatXAxis", description="The format to use for the x axis."
    )
    format_y_axis: Optional[str] = Field(
        None, alias="formatYAxis", description="The format to use for the y axis."
    )
    show_axis_line: Optional[bool] = Field(
        None, alias="showAxisLine", description="Whether to show the axis line."
    )
    show_legend: Optional[bool] = Field(
        None, alias="showLegend", description="Whether to show the legend."
    )
    enable_legend_checkbox_mode: Optional[bool] = Field(
        True,
        alias="enableLegendCheckboxMode",
        description="Whether the legend should allow toggling the visibility of each data series.",
    )
    hint: Optional[str] = Field(None, description="Add a hint for the chart.")
    dynamic_tick_rotate: Optional[Union[Any, bool]] = Field(
        None,
        alias="dynamicTickRotate",
        description="Whether to dynamically rotate ticks.",
    )


class Chart3(BaseModel):
    id: Id
    title: TitleModel
    data_id: Optional[DataId] = Field(..., alias="dataId")
    apply_filters: Optional[ApplyFilters] = Field(None, alias="applyFilters")
    cross_filter: Optional[CrossFilterModel] = Field(None, alias="crossFilter")
    type: Literal["lineChart"] = Field(
        ...,
        description="The type of the chart. Must be one of: bigNumber, horizontalBar, lineChart, barChart, layerChart, heatmapChart, pivotTable",
    )
    x_axis: XAxis1 = Field(
        ..., alias="xAxis", description="The x axis configuration for the chart."
    )
    y_axis: YAxis1 = Field(
        ..., alias="yAxis", description="The y axis configuration for the chart."
    )
    group_by: GroupBy = Field(
        ...,
        alias="groupBy",
        description="The group by axis configuration for the chart.",
    )
    num_groups: Optional[Union[float, str]] = Field(
        20,
        alias="numGroups",
        description="The number of groups to show in the chart. Use ALL to show all groups.",
    )
    group_others: Optional[bool] = Field(
        None,
        alias="groupOthers",
        description="Whether to group the other values into a single line.",
    )
    enable_area: Optional[bool] = Field(
        None,
        alias="enableArea",
        description="Whether to fill the area below the line chart.",
    )
    color_by: Optional[ColorBy1] = Field(
        None, alias="colorBy", description="The color by option for the chart."
    )
    chart_display: Optional[ChartDisplay2] = Field({}, alias="chartDisplay")
    tooltip: Optional[Tooltip] = Field(
        None, description="The tooltip configuration for the chart."
    )


class ChartDisplay3(BaseModel):
    color_range: Optional[ColorRangeModel] = Field(
        default_factory=lambda: ColorRangeModel.model_validate(
            {
                "name": "Uber Viz Qualitative",
                "type": "qualitative",
                "category": "Uber",
                "colors": [
                    "#12939A",
                    "#DDB27C",
                    "#88572C",
                    "#FF991F",
                    "#F15C17",
                    "#223F9A",
                    "#DA70BF",
                    "#125C77",
                    "#4DC19C",
                    "#776E57",
                ],
            }
        ),
        alias="colorRange",
        description="The color range configuration for the chart.",
    )
    sort: Optional[SortModel] = Field(None, description="The sort type for the chart.")
    format_tooltip: Optional[str] = Field(
        None, alias="formatTooltip", description="The format to use for the tooltip."
    )
    format_x_axis: Optional[str] = Field(
        None, alias="formatXAxis", description="The format to use for the x axis."
    )
    format_y_axis: Optional[str] = Field(
        None, alias="formatYAxis", description="The format to use for the y axis."
    )
    show_x_axis: Optional[bool] = Field(
        None, alias="showXAxis", description="Whether to show the x axis."
    )
    show_y_axis: Optional[bool] = Field(
        None, alias="showYAxis", description="Whether to show the y axis."
    )
    show_values: Optional[bool] = Field(
        None, alias="showValues", description="Whether to show the values in the chart."
    )
    label_format_mode: Optional[LabelFormatMode] = Field(
        None, alias="labelFormatMode", description="The value label format mode."
    )
    label_skip_width: Optional[float] = Field(
        None,
        alias="labelSkipWidth",
        description="Threshold at which to hide value labels if bar width is lower than the provided value, ignored if 0 (in px).",
    )
    label_skip_height: Optional[float] = Field(
        None,
        alias="labelSkipHeight",
        description="Threshold at which to hide value labels if bar height is lower than the provided value, ignored if 0 (in px).",
    )
    log_scale_values: Optional[bool] = Field(
        None,
        alias="logScaleValues",
        description="Whether to use a log scale for the values.",
    )
    dynamic_tick_rotate: Optional[Union[Any, bool]] = Field(
        None,
        alias="dynamicTickRotate",
        description="Whether to dynamically rotate ticks.",
    )
    rotate_x_ticks: Optional[Union[Any, bool]] = Field(
        None, alias="rotateXTicks", description="Whether to rotate the x ticks."
    )
    rotate_y_ticks: Optional[Union[Any, bool]] = Field(
        None, alias="rotateYTicks", description="Whether to rotate the y ticks."
    )
    less_x_ticks: Optional[bool] = Field(
        None, alias="lessXTicks", description="Whether to show less x ticks."
    )
    less_y_ticks: Optional[bool] = Field(
        None, alias="lessYTicks", description="Whether to show less y ticks."
    )
    more_space_x_axis: Optional[float] = Field(
        None,
        alias="moreSpaceXAxis",
        description="The amount of space to add to the x axis.",
    )
    more_space_y_axis: Optional[float] = Field(
        None,
        alias="moreSpaceYAxis",
        description="The amount of space to add to the y axis.",
    )
    sort_group_by: Optional[SortModel] = Field(
        None, alias="sortGroupBy", description="The sort type for the group by axis."
    )
    is_horizontal: Optional[bool] = Field(
        None,
        alias="isHorizontal",
        description="Whether to display the chart horizontally.",
    )
    inner_padding: Optional[float] = Field(
        None, alias="innerPadding", description="The inner padding for the chart."
    )
    padding: Optional[float] = Field(None, description="The padding for the chart.")
    show_axis_line: Optional[bool] = Field(
        None, alias="showAxisLine", description="Whether to show the axis line."
    )
    show_legend: Optional[bool] = Field(
        None, alias="showLegend", description="Whether to show the legend."
    )
    enable_legend_checkbox_mode: Optional[bool] = Field(
        True,
        alias="enableLegendCheckboxMode",
        description="Whether the legend should allow toggling the visibility of each data series.",
    )
    x_axis_labels: Optional[List[Union[str, float]]] = Field(
        None,
        alias="xAxisLabels",
        description="Ordering of the labels to use for the x axis",
    )
    group_by_labels: Optional[List[str]] = Field(
        None,
        alias="groupByLabels",
        description='Ordering of the labels to use for "group by".',
    )
    hint: Optional[str] = Field(None, description="Add a hint for the chart.")


class Chart4(BaseModel):
    id: Id
    title: TitleModel
    data_id: Optional[DataId] = Field(..., alias="dataId")
    apply_filters: Optional[ApplyFilters] = Field(None, alias="applyFilters")
    cross_filter: Optional[CrossFilterModel] = Field(None, alias="crossFilter")
    type: Literal["barChart"] = Field(
        ...,
        description="The type of the chart. Must be one of: bigNumber, horizontalBar, lineChart, barChart, layerChart, heatmapChart, pivotTable",
    )
    x_axis: XAxis1 = Field(
        ..., alias="xAxis", description="The x axis configuration for the chart."
    )
    y_axis: YAxis2 = Field(
        ..., alias="yAxis", description="The y axis configuration for the chart."
    )
    group_by: Optional[GroupBy] = Field(
        None,
        alias="groupBy",
        description="The group by axis configuration for the chart.",
    )
    num_bins: float = Field(
        ..., alias="numBins", description="The number of bins to show in the chart."
    )
    bin_others: bool = Field(
        ...,
        alias="binOthers",
        description="Whether to bin the other values into a single bar.",
    )
    num_groups: Optional[Union[float, str]] = Field(
        10,
        alias="numGroups",
        description="The number of groups to show in the chart. Use ALL to show all groups.",
    )
    group_others: Optional[bool] = Field(
        None,
        alias="groupOthers",
        description="Whether to group the other values into a single bar.",
    )
    group_mode: str = Field(
        ...,
        alias="groupMode",
        description="The grouping mode for the chart. Must be one of: stacked, grouped",
    )
    color_by: Optional[ColorBy2] = Field(
        None,
        alias="colorBy",
        description="The color by option for the chart. Must be one of: X-Axis,GroupBy,",
    )
    enable_viz_mode: Optional[bool] = Field(
        False, alias="enableVizMode", description="Whether to show the viz mode toggle."
    )
    viz_mode: Optional[VizMode] = Field(
        "CHART", alias="vizMode", description="The viz mode for the chart."
    )
    table_viz_mode_config: Optional[TableVizModeConfig] = Field(
        None, alias="tableVizModeConfig", description="Configuration for table viz mode"
    )
    chart_display: Optional[ChartDisplay3] = Field(
        {}, alias="chartDisplay", description="The display configuration for the chart."
    )


class ChartDisplay4(BaseModel):
    color_range: Optional[ColorRangeModel] = Field(
        default_factory=lambda: ColorRangeModel.model_validate(
            {
                "name": "Uber Viz Qualitative",
                "type": "qualitative",
                "category": "Uber",
                "colors": [
                    "#12939A",
                    "#DDB27C",
                    "#88572C",
                    "#FF991F",
                    "#F15C17",
                    "#223F9A",
                    "#DA70BF",
                    "#125C77",
                    "#4DC19C",
                    "#776E57",
                ],
            }
        ),
        alias="colorRange",
        description="The color range configuration for the chart.",
    )
    show_values: Optional[bool] = Field(
        None, alias="showValues", description="Whether to show the values in the chart."
    )
    show_legend: Optional[bool] = Field(
        None, alias="showLegend", description="Whether to show the legend."
    )
    format: Optional[str] = Field(None, description="The format to use for the chart.")
    border_width: Optional[float] = Field(
        None, alias="borderWidth", description="The border width for the chart."
    )
    force_square: Optional[bool] = Field(
        None,
        alias="forceSquare",
        description="Whether to force the chart to be square.",
    )
    x_outer_padding: Optional[float] = Field(
        None, alias="xOuterPadding", description="The outer padding for the x axis."
    )
    x_inner_padding: Optional[float] = Field(
        None, alias="xInnerPadding", description="The inner padding for the x axis."
    )
    y_outer_padding: Optional[float] = Field(
        None, alias="yOuterPadding", description="The outer padding for the y axis."
    )
    y_inner_padding: Optional[float] = Field(
        None, alias="yInnerPadding", description="The inner padding for the y axis."
    )
    sort_x: Optional[SortModel] = Field(
        "alphaAsc", alias="sortX", description="The sort type for the x axis."
    )
    sort_y: Optional[SortModel] = Field(
        "alphaAsc", alias="sortY", description="The sort type for the y axis."
    )
    rotate_x_ticks: Optional[bool] = Field(
        None, alias="rotateXTicks", description="Whether to rotate ticks on x axis."
    )
    rotate_y_ticks: Optional[bool] = Field(
        None, alias="rotateYTicks", description="Whether to rotate ticks on y axis."
    )
    dynamic_tick_rotate: Optional[Union[Any, bool]] = Field(
        None,
        alias="dynamicTickRotate",
        description="Whether to dynamically rotate ticks.",
    )
    domain_zero_to_hundred: Optional[bool] = Field(
        None,
        alias="domainZeroToHundred",
        description="Whether to set legend domain from 0 to 100.",
    )
    hint: Optional[str] = Field(None, description="Add a hint for the chart.")


class Chart5(BaseModel):
    id: Id
    title: TitleModel
    data_id: Optional[DataId] = Field(..., alias="dataId")
    apply_filters: Optional[ApplyFilters] = Field(None, alias="applyFilters")
    cross_filter: Optional[CrossFilterModel] = Field(None, alias="crossFilter")
    type: Literal["heatmapChart"] = Field(
        ...,
        description="The type of the chart. Must be one of: bigNumber, horizontalBar, lineChart, barChart, layerChart, heatmapChart, pivotTable",
    )
    x_axis: XAxis1 = Field(
        ..., alias="xAxis", description="The x axis configuration for the chart."
    )
    y_axis: YAxis3 = Field(
        ..., alias="yAxis", description="The y axis configuration for the chart."
    )
    value: Value = Field(..., description="The value axis configuration for the chart.")
    color_by: Optional[ColorBy3] = Field(
        None, alias="colorBy", description="The color by option for the chart."
    )
    num_of_col: Optional[float] = Field(
        None,
        alias="numOfCol",
        description="The maximum number of columns to show in the chart.",
    )
    num_of_row: Optional[float] = Field(
        None,
        alias="numOfRow",
        description="The maximum number of rows to show in the chart.",
    )
    chart_display: Optional[ChartDisplay4] = Field({}, alias="chartDisplay")


class ChartDisplay7(BaseModel):
    show_in_tooltip: Optional[ShowInTooltip] = Field(None, alias="showInTooltip")
    id_field: Optional[IdField] = Field(None, alias="idField")
    format: Optional[Format] = None
    color_range: Optional[ColorRangeModel] = Field(
        default_factory=lambda: ColorRangeModel.model_validate(
            {
                "name": "Uber Viz Qualitative",
                "type": "qualitative",
                "category": "Uber",
                "colors": [
                    "#12939A",
                    "#DDB27C",
                    "#88572C",
                    "#FF991F",
                    "#F15C17",
                    "#223F9A",
                    "#DA70BF",
                    "#125C77",
                    "#4DC19C",
                    "#776E57",
                ],
            }
        ),
        alias="colorRange",
        description="The color range configuration for the chart.",
    )
    num_entries: Optional[Union[float, str]] = Field(
        None,
        alias="numEntries",
        description="The number of entries to show in the chart.",
    )
    sort_by: Optional[SortBy] = Field(
        None, alias="sortBy", description="The sort by configuration for the chart."
    )
    sort_order_reverse: Optional[bool] = Field(
        None, alias="sortOrderReverse", description="Whether to reverse the sort order."
    )


class Chart9(BaseModel):
    id: Id
    title: TitleModel
    type: TypeModel
    layer_chart_type: Literal["BREAKDOWN_BY_CATEGORY"] = Field(
        ...,
        alias="layerChartType",
        description="The tooltip chart type. Must be one of TIME_SERIES, HEXTILE_TIME_SERIES, BREAKDOWN_BY_CATEGORY, FLOW_TOP_ORIGINS, FLOW_TOP_DESTS",
    )
    layer_id: LayerId = Field(..., alias="layerId")
    chart_display: Optional[ChartDisplay7] = Field(
        {}, alias="chartDisplay", description="The display configuration for the chart."
    )
    apply_filters: Optional[ApplyFiltersModel] = Field(None, alias="applyFilters")
    axis: Optional[Axis1] = Field(
        None, description="The axis configuration for the chart."
    )
    color_by: Optional[ColorBy4] = Field(None, alias="colorBy")


class Chart(
    RootModel[
        Union[
            Union[Chart1, Chart2, Chart3, Chart4, Chart5, Chart6],
            Union[Chart7, Chart8, Chart9, Chart10, Chart11],
        ]
    ]
):
    root: Union[
        Union[Chart1, Chart2, Chart3, Chart4, Chart5, Chart6],
        Union[Chart7, Chart8, Chart9, Chart10, Chart11],
    ] = Field(..., title="Chart")
