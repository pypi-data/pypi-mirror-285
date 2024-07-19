# type: ignore

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, RootModel, confloat


class ColorItem(RootModel[confloat(ge=0.0, le=255.0)]):
    root: confloat(ge=0.0, le=255.0)


class Legend(BaseModel):
    is_included: bool = Field(
        ..., alias="isIncluded", description="Display the layer in the legend."
    )


class Type(Enum):
    sequential = "sequential"
    qualitative = "qualitative"
    diverging = "diverging"
    cyclical = "cyclical"
    custom = "custom"
    ordinal = "ordinal"
    custom_ordinal = "customOrdinal"


class FieldModel(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None


class FieldItem(BaseModel):
    field: Optional[Union[Any, FieldModel]] = None
    format: Optional[Union[Any, str]] = None


class Anchor(Enum):
    start = "start"
    middle = "middle"
    end = "end"


class Alignment(Enum):
    top = "top"
    center = "center"
    bottom = "bottom"


class Columns(BaseModel):
    geojson: str


class Columns1(BaseModel):
    lat: str
    lng: str
    altitude: Optional[str] = None
    neighbors: Optional[str] = None


class Type1(Enum):
    string = "string"
    real = "real"
    timestamp = "timestamp"
    integer = "integer"
    boolean = "boolean"
    date = "date"


class ColorField(BaseModel):
    type: Optional[Type1] = Field(None, description="Column type")
    name: Optional[str] = Field(None, description="Column name")


class ColorScale(Enum):
    ordinal = "ordinal"
    quantize = "quantize"
    quantile = "quantile"
    jenks = "jenks"
    custom = "custom"
    custom_ordinal = "customOrdinal"


class SizeScale(Enum):
    point = "point"
    sqrt = "sqrt"
    linear = "linear"


class Columns2(BaseModel):
    lat0: str
    lng0: str
    lat1: str
    lng1: str
    alt0: Optional[Union[Any, str]] = None
    alt1: Optional[Union[Any, str]] = None


class Columns3(BaseModel):
    neighbors: str
    lat: str
    lng: str
    alt: Optional[str] = None


class SizeScale1(Enum):
    point = "point"
    linear = "linear"
    sqrt = "sqrt"
    log = "log"


class Columns4(BaseModel):
    lat0: str
    lng0: str
    lat1: str
    lng1: str


class Columns5(BaseModel):
    lat: str
    lng: str
    neighbors: str


class Columns6(BaseModel):
    lat: str
    lng: str


class WeightScale(Enum):
    point = "point"
    linear = "linear"
    sqrt = "sqrt"
    log = "log"


class ColorAggregation(Enum):
    count = "count"
    average = "average"
    maximum = "maximum"
    minimum = "minimum"
    median = "median"
    stdev = "stdev"
    sum = "sum"
    variance = "variance"
    mode = "mode"
    count_unique = "countUnique"


class SizeScale3(Enum):
    linear = "linear"
    sqrt = "sqrt"
    log = "log"


class Type2(Enum):
    real = "real"
    integer = "integer"


class SizeField(BaseModel):
    type: Optional[Type2] = Field(None, description="Column type")
    name: Optional[str] = Field(None, description="Column name")


class Columns9(BaseModel):
    hex_id: str


class SizeScale5(Enum):
    point = "point"
    linear = "linear"
    sqrt = "sqrt"
    log = "log"


class CoverageScale(Enum):
    point = "point"
    sqrt = "sqrt"
    linear = "linear"


class RadiusByZoom(BaseModel):
    enabled: Optional[bool] = None
    stops: Optional[List[List[float]]] = None


class HeightScale(Enum):
    point = "point"
    linear = "linear"
    sqrt = "sqrt"
    log = "log"


class Columns10(BaseModel):
    token: str


class Columns11(BaseModel):
    lat: str
    lng: str


class Columns12(BaseModel):
    lat: str
    lng: str
    icon: str
    altitude: Optional[str] = None


class SizeScale7(Enum):
    point = "point"
    sqrt = "sqrt"
    linear = "linear"


class Columns13(BaseModel):
    geojson: str


class Columns14(BaseModel):
    id: str
    lat: str
    lng: str
    altitude: Optional[Union[Any, str]] = None
    sort_by: Optional[str] = Field(None, alias="sortBy")


class SizeScale8(Enum):
    point = "point"
    linear = "linear"
    sqrt = "sqrt"
    log = "log"


class RadiusScale(Enum):
    point = "point"
    sqrt = "sqrt"
    linear = "linear"


class Columns15(BaseModel):
    geojson: str


class Columns16(BaseModel):
    id: str
    lat: str
    lng: str
    timestamp: str
    altitude: Optional[Union[Any, str]] = None


class Type3(Enum):
    real = "real"
    timestamp = "timestamp"
    integer = "integer"


class RollField(BaseModel):
    type: Optional[Type3] = Field(None, description="Column type")
    name: Optional[str] = Field(None, description="Column name")


class PitchField(BaseModel):
    type: Optional[Type3] = Field(None, description="Column type")
    name: Optional[str] = Field(None, description="Column name")


class YawField(BaseModel):
    type: Optional[Type3] = Field(None, description="Column type")
    name: Optional[str] = Field(None, description="Column name")


class Preset(Enum):
    true_color = "trueColor"
    infrared = "infrared"
    agriculture = "agriculture"
    forest_burn = "forestBurn"
    ndvi = "ndvi"
    savi = "savi"
    msavi = "msavi"
    ndmi = "ndmi"
    nbr = "nbr"
    nbr2 = "nbr2"
    single_band = "singleBand"


class StacSearchProvider(Enum):
    earth_search = "earth-search"
    microsoft = "microsoft"


class ColormapId(Enum):
    cfastie = "cfastie"
    rplumbo = "rplumbo"
    schwarzwald = "schwarzwald"
    viridis = "viridis"
    plasma = "plasma"
    inferno = "inferno"
    magma = "magma"
    cividis = "cividis"
    greys = "greys"
    purples = "purples"
    blues = "blues"
    greens = "greens"
    oranges = "oranges"
    reds = "reds"
    ylorbr = "ylorbr"
    ylorrd = "ylorrd"
    orrd = "orrd"
    purd = "purd"
    rdpu = "rdpu"
    bupu = "bupu"
    gnbu = "gnbu"
    pubu = "pubu"
    ylgnbu = "ylgnbu"
    pubugn = "pubugn"
    bugn = "bugn"
    ylgn = "ylgn"
    binary = "binary"
    gray = "gray"
    bone = "bone"
    pink = "pink"
    spring = "spring"
    summer = "summer"
    autumn = "autumn"
    winter = "winter"
    cool = "cool"
    wistia = "wistia"
    hot = "hot"
    afmhot = "afmhot"
    gist_heat = "gist_heat"
    copper = "copper"
    piyg = "piyg"
    prgn = "prgn"
    brbg = "brbg"
    puor = "puor"
    rdgy = "rdgy"
    rdbu = "rdbu"
    rdylbu = "rdylbu"
    rdylgn = "rdylgn"
    spectral = "spectral"
    coolwarm = "coolwarm"
    bwr = "bwr"
    seismic = "seismic"
    twilight = "twilight"
    twilight_shifted = "twilight_shifted"
    hsv = "hsv"
    flag = "flag"
    prism = "prism"
    ocean = "ocean"
    gist_earth = "gist_earth"
    terrain = "terrain"
    gist_stern = "gist_stern"
    gnuplot = "gnuplot"
    gnuplot2 = "gnuplot2"
    cmrmap = "cmrmap"
    cubehelix = "cubehelix"
    brg = "brg"
    gist_rainbow = "gist_rainbow"
    rainbow = "rainbow"
    jet = "jet"
    nipy_spectral = "nipy_spectral"
    gist_ncar = "gist_ncar"


class Columns17(BaseModel):
    lat: str
    lng: str
    altitude: Optional[str] = None


class Columns18(BaseModel):
    lat0: str
    lng0: str
    lat1: str
    lng1: str
    count: Optional[str] = None
    source_name: Optional[str] = Field(None, alias="sourceName")
    target_name: Optional[str] = Field(None, alias="targetName")


class Columns19(BaseModel):
    source_h3: str = Field(..., alias="sourceH3")
    target_h3: str = Field(..., alias="targetH3")
    count: Optional[str] = None
    source_name: Optional[str] = Field(None, alias="sourceName")
    target_name: Optional[str] = Field(None, alias="targetName")


class Field0Item(RootModel[confloat(ge=0.0, le=255.0)]):
    root: confloat(ge=0.0, le=255.0)


class Field0(RootModel[confloat(ge=0.0, le=255.0)]):
    root: confloat(ge=0.0, le=255.0)


class Field1(RootModel[List[Field0]]):
    root: List[Field0] = Field(..., max_length=4, min_length=4)


class DataId(RootModel[str]):
    root: str = Field(
        ..., description="The id of the dataset from which this layer was created"
    )


class Hidden(RootModel[bool]):
    root: bool = Field(
        ...,
        description="Hide layer from the layer panel. This will prevent user from editing the layer.",
    )


class IsVisible(RootModel[bool]):
    root: bool = Field(..., description="Layer visibility on the map.")


class Label(RootModel[str]):
    root: str = Field(..., description="The displayed layer label")


class FieldItem1(BaseModel):
    field: Optional[Union[Any, FieldModel]] = None
    format: Optional[Union[Any, str]] = None


class FieldItem2(BaseModel):
    field: Optional[Union[Any, FieldModel]] = None
    format: Optional[Union[Any, str]] = None


class Type6(Enum):
    sequential = "sequential"
    qualitative = "qualitative"
    diverging = "diverging"
    cyclical = "cyclical"
    custom = "custom"
    ordinal = "ordinal"
    custom_ordinal = "customOrdinal"


class Items(RootModel[str]):
    root: str


class Opacity(RootModel[confloat(ge=0.0, le=1.0)]):
    root: confloat(ge=0.0, le=1.0)


class Id(RootModel[str]):
    root: str = Field(..., description="Layer id, use a string without space")


class Type8(Enum):
    string = "string"
    real = "real"
    timestamp = "timestamp"
    integer = "integer"
    boolean = "boolean"
    date = "date"


class Field0Model(BaseModel):
    type: Optional[Type8] = Field(None, description="Column type")
    name: Optional[str] = Field(None, description="Column name")


class Field0Model1(Enum):
    ordinal = "ordinal"
    quantize = "quantize"
    quantile = "quantile"
    jenks = "jenks"
    custom = "custom"
    custom_ordinal = "customOrdinal"


class ElevationPercentile(RootModel[List[confloat(ge=0.0, le=100.0)]]):
    root: List[confloat(ge=0.0, le=100.0)]


class Percentile(RootModel[List[confloat(ge=0.0, le=100.0)]]):
    root: List[confloat(ge=0.0, le=100.0)]


class Field1Model(BaseModel):
    enabled: Optional[bool] = None
    stops: Optional[List[List[float]]] = None


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


class VisualChannels(BaseModel):
    color_field: Optional[ColorField] = Field(None, alias="colorField")
    color_scale: Optional[ColorScale] = Field(
        None, alias="colorScale", description="Scale is based on colorField type."
    )
    stroke_color_field: Optional[Field0Model] = Field(None, alias="strokeColorField")
    stroke_color_scale: Optional[Union[Any, Field0Model1]] = Field(
        None,
        alias="strokeColorScale",
        description="Scale is based on strokeColorField type.",
    )
    size_field: Optional[Field0Model] = Field(None, alias="sizeField")
    size_scale: Optional[SizeScale] = Field(
        None, alias="sizeScale", description="Scale is based on sizeField type. "
    )


class VisualChannels1(BaseModel):
    color_field: Optional[Union[Any, Field0Model]] = Field(None, alias="colorField")
    color_scale: Optional[Field0Model1] = Field(
        None, alias="colorScale", description="Scale is based on colorField type."
    )
    size_field: Optional[Field0Model] = Field(None, alias="sizeField")
    size_scale: Optional[SizeScale1] = Field(
        None, alias="sizeScale", description="Scale is based on sizeField type."
    )


class VisualChannels2(BaseModel):
    color_field: Optional[Union[Any, Field0Model]] = Field(None, alias="colorField")
    color_scale: Optional[Field0Model1] = Field(
        None, alias="colorScale", description="Scale is based on colorField type."
    )
    size_field: Optional[Union[Any, Field0Model]] = Field(None, alias="sizeField")
    size_scale: Optional[SizeScale1] = Field(
        None, alias="sizeScale", description="Scale is based on sizeField type."
    )


class VisualChannels3(BaseModel):
    weight_field: Optional[Field0Model] = Field(None, alias="weightField")
    weight_scale: Optional[WeightScale] = Field(
        None,
        alias="weightScale",
        description="Calculate weight based on the selected field.",
    )


class VisualChannels4(BaseModel):
    color_field: Optional[Union[Any, Field0Model]] = Field(None, alias="colorField")
    color_scale: Optional[Field0Model1] = Field(
        None, alias="colorScale", description="Scale is based on colorField type."
    )
    size_field: Optional[Union[Any, Field0Model]] = Field(None, alias="sizeField")
    size_scale: Optional[SizeScale3] = Field(
        None,
        alias="sizeScale",
        description="Scale is based on sizeField type and undefined type.",
    )


class VisualChannels5(BaseModel):
    color_field: Optional[Union[Any, Field0Model]] = Field(None, alias="colorField")
    color_scale: Optional[Field0Model1] = Field(
        None, alias="colorScale", description="Scale is based on colorField type."
    )
    size_field: Optional[SizeField] = Field(None, alias="sizeField")
    size_scale: Optional[SizeScale3] = Field(
        None,
        alias="sizeScale",
        description="Scale is based on sizeField type and undefined type.",
    )


class VisualChannels6(BaseModel):
    color_field: Optional[Union[Any, Field0Model]] = Field(None, alias="colorField")
    color_scale: Optional[Field0Model1] = Field(
        None, alias="colorScale", description="Scale is based on colorField type."
    )
    stroke_color_field: Optional[Union[Any, Field0Model]] = Field(
        None, alias="strokeColorField"
    )
    stroke_color_scale: Optional[Field0Model1] = Field(
        None, alias="strokeColorScale", description="Scale is based on colorField type."
    )
    size_field: Optional[Union[Any, Field0Model]] = Field(None, alias="sizeField")
    size_scale: Optional[SizeScale5] = Field(
        None, alias="sizeScale", description="Scale is based on sizeField type."
    )
    coverage_field: Optional[Union[Any, Field0Model]] = Field(
        None, alias="coverageField"
    )
    coverage_scale: Optional[CoverageScale] = Field(
        None, alias="coverageScale", description="Scale is based on coverageField type."
    )


class VisualChannels7(BaseModel):
    color_field: Optional[Union[Any, Field0Model]] = Field(None, alias="colorField")
    color_scale: Optional[ColorScale] = Field(
        None, alias="colorScale", description="Scale is based on colorField type."
    )
    height_field: Optional[Union[Any, Field0Model]] = Field(None, alias="heightField")
    height_scale: Optional[HeightScale] = Field(
        None, alias="heightScale", description="Scale is based on heightField type."
    )


class VisualChannels8(BaseModel):
    color_field: Optional[Union[Any, Field0Model]] = Field(None, alias="colorField")
    color_scale: Optional[ColorScale] = Field(
        None, alias="colorScale", description="Scale is based on colorField type."
    )
    size_field: Optional[Field0Model] = Field(None, alias="sizeField")
    size_scale: Optional[SizeScale5] = Field(
        None, alias="sizeScale", description="Scale is based on sizeField type."
    )
    stroke_color_field: Optional[Field0Model] = Field(None, alias="strokeColorField")
    stroke_color_scale: Optional[Union[Any, Field0Model1]] = Field(
        None,
        alias="strokeColorScale",
        description="Scale is based on strokeColorField type.",
    )
    height_field: Optional[Union[Any, Field0Model]] = Field(None, alias="heightField")
    height_scale: Optional[HeightScale] = Field(
        None, alias="heightScale", description="Scale is based on heightField type."
    )


class VisualChannels9(BaseModel):
    color_field: Optional[Union[Any, Field0Model]] = Field(None, alias="colorField")
    color_scale: Optional[Field0Model1] = Field(
        None, alias="colorScale", description="Scale is based on colorField type."
    )


class VisualChannels10(BaseModel):
    color_field: Optional[Union[Any, Field0Model]] = Field(None, alias="colorField")
    color_scale: Optional[Field0Model1] = Field(
        None, alias="colorScale", description="Scale is based on colorField type."
    )
    size_field: Optional[Union[Any, Field0Model]] = Field(None, alias="sizeField")
    size_scale: Optional[SizeScale7] = Field(
        None, alias="sizeScale", description="Scale is based on sizeField type."
    )


class VisualChannels11(BaseModel):
    color_field: Optional[Union[Any, Field0Model]] = Field(None, alias="colorField")
    color_scale: Optional[Field0Model1] = Field(
        None, alias="colorScale", description="Scale is based on colorField type."
    )
    stroke_color_field: Optional[Union[Any, Field0Model]] = Field(
        None, alias="strokeColorField"
    )
    stroke_color_scale: Optional[Field0Model1] = Field(
        None,
        alias="strokeColorScale",
        description="Scale is based on strokeColorField type.",
    )
    size_field: Optional[Field0Model] = Field(None, alias="sizeField")
    size_scale: Optional[SizeScale8] = Field(
        None, alias="sizeScale", description="Scale is based on sizeField type."
    )
    height_field: Optional[Union[Any, Field0Model]] = Field(None, alias="heightField")
    height_scale: Optional[HeightScale] = Field(
        None, alias="heightScale", description="Scale is based on heightField type."
    )
    radius_field: Optional[Union[Any, Field0Model]] = Field(None, alias="radiusField")
    radius_scale: Optional[RadiusScale] = Field(
        None, alias="radiusScale", description="Scale is based on radiusField type."
    )


class VisualChannels12(BaseModel):
    color_field: Optional[Union[Any, Field0Model]] = Field(None, alias="colorField")
    color_scale: Optional[Field0Model1] = Field(None, alias="colorScale")
    size_field: Optional[Union[Any, Field0Model]] = Field(None, alias="sizeField")
    size_scale: Optional[SizeScale8] = Field(
        None, alias="sizeScale", description="Scale is based on sizeField type."
    )
    roll_field: Optional[RollField] = Field(None, alias="rollField")
    roll_scale: Literal["linear"] = Field(
        "linear", alias="rollScale", description="Scale is based on rollField type."
    )
    pitch_field: Optional[PitchField] = Field(None, alias="pitchField")
    pitch_scale: Literal["linear"] = Field(
        "linear", alias="pitchScale", description="Scale is based on pitchField type."
    )
    yaw_field: Optional[YawField] = Field(None, alias="yawField")
    yaw_scale: Literal["linear"] = Field(
        "linear", alias="yawScale", description="Scale is based on yawField type."
    )


class VisualChannels13(BaseModel):
    color_field: Optional[Union[Any, Field0Model]] = Field(None, alias="colorField")
    color_scale: Optional[ColorScale] = Field(
        None, alias="colorScale", description="Scale is based on colorField type."
    )
    stroke_color_field: Optional[Union[Any, Field0Model]] = Field(
        None, alias="strokeColorField"
    )
    stroke_color_scale: Optional[Field0Model1] = Field(
        None,
        alias="strokeColorScale",
        description="Scale is based on strokeColorField type.",
    )
    height_field: Optional[Union[Any, Field0Model]] = Field(None, alias="heightField")
    height_scale: Optional[HeightScale] = Field(
        None, alias="heightScale", description="Scale is based on heightField type."
    )


class VisualChannels14(BaseModel):
    color_field: Optional[Union[Any, Field0Model]] = Field(None, alias="colorField")
    color_scale: Optional[Field0Model1] = Field(
        None, alias="colorScale", description="Scale is based on colorField type."
    )
    size_field: Optional[Union[Any, Field0Model]] = Field(None, alias="sizeField")
    size_scale: Optional[SizeScale8] = Field(
        None, alias="sizeScale", description="Scale is based on sizeField type."
    )


class VisConfig17(BaseModel):
    opacity: Optional[Opacity] = None
    service_layers: Optional[Union[Any, Union[str, float, List[str]]]] = Field(
        None, alias="serviceLayers"
    )


class VisConfig18(BaseModel):
    opacity: Optional[Opacity] = None


class Color(RootModel[Union[List[Union[ColorItem, Field0]], List[Field0]]]):
    root: Union[List[Union[ColorItem, Field0]], List[Field0]] = Field(
        ..., description="Layer color as RGB. e.g. `[255, 0, 0]`."
    )


class Field0Model2(RootModel[List[Union[Field0Item, Field0]]]):
    root: List[Union[Field0Item, Field0]] = Field(..., max_length=3, min_length=3)


class ColorRange1(BaseModel):
    name: Optional[str] = Field("Unnamed", description="The name of the color range.")
    type: Optional[Type6] = Field(
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


class Field1Model1(BaseModel):
    name: Optional[str] = Field("Unnamed", description="The name of the color range.")
    type: Optional[Type6] = Field(
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


class Field1Model2(RootModel[Union[Field0Model2, Field1]]):
    root: Union[Field0Model2, Field1]


class VisConfig(BaseModel):
    opacity: Optional[Opacity] = None
    thickness: Optional[confloat(ge=0.0, le=100.0)] = 2
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    size_range: Optional[List[confloat(ge=0.0, le=200.0)]] = Field(
        [0, 10], alias="sizeRange"
    )
    target_color: Optional[List[float]] = Field(None, alias="targetColor")
    elevation_scale: Optional[confloat(ge=0.0, le=1000.0)] = Field(
        1, alias="elevationScale"
    )


class HighlightColor(RootModel[Optional[Union[Any, Field1Model2]]]):
    root: Optional[Union[Any, Field1Model2]] = Field(..., description="Highlight color")


class VisConfigModel(BaseModel):
    opacity: Optional[Opacity] = None
    stroke_opacity: Optional[confloat(ge=0.0, le=1.0)] = Field(
        0.8, alias="strokeOpacity"
    )
    thickness: Optional[confloat(ge=0.0, le=100.0)] = 0.5
    stroke_color: Optional[Union[Any, Field1Model2]] = Field(
        None, alias="strokeColor", description="Stroke color"
    )
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    stroke_color_range: Optional[Union[Any, Field1Model1]] = Field(
        None, alias="strokeColorRange"
    )
    radius: Optional[confloat(ge=0.0, le=100.0)] = 10
    size_range: Optional[List[confloat(ge=0.0, le=200.0)]] = Field(
        [0, 10], alias="sizeRange"
    )
    radius_range: Optional[List[confloat(ge=0.0, le=500.0)]] = Field(
        [0, 50], alias="radiusRange"
    )
    height_range: Optional[List[confloat(ge=0.0, le=1000.0)]] = Field(
        [0, 500], alias="heightRange"
    )
    elevation_scale: Optional[confloat(ge=0.0, le=1000.0)] = Field(
        5, alias="elevationScale"
    )
    stroked: Optional[bool] = True
    filled: Optional[bool] = False
    enable3d: Optional[bool] = False
    wireframe: Optional[bool] = False
    fixed_height: Optional[bool] = Field(False, alias="fixedHeight")


class VisConfigModel1(BaseModel):
    opacity: Optional[Opacity] = None
    thickness: Optional[confloat(ge=0.0, le=100.0)] = 0.5
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    trail_length: Optional[confloat(ge=1.0, le=1000.0)] = Field(
        180, alias="trailLength"
    )
    fade_trail: Optional[bool] = Field(True, alias="fadeTrail")
    billboard: Optional[bool] = False
    size_range: Optional[List[confloat(ge=0.0, le=200.0)]] = Field(
        [0, 10], alias="sizeRange"
    )
    size_scale: Optional[confloat(ge=-10.0, le=10.0)] = Field(1, alias="sizeScale")
    scenegraph: Optional[str] = None
    scenegraph_enabled: Optional[bool] = Field(False, alias="scenegraphEnabled")
    scenegraph_color_enabled: Optional[bool] = Field(
        False, alias="scenegraphColorEnabled"
    )
    scenegraph_use_trail_color: Optional[bool] = Field(
        False, alias="scenegraphUseTrailColor"
    )
    scenegraph_color: Optional[Union[Any, List[float]]] = Field(
        None, alias="scenegraphColor"
    )
    scenegraph_custom_model_url: Optional[str] = Field(
        "", alias="scenegraphCustomModelUrl"
    )
    adjust_roll: Optional[confloat(ge=-180.0, le=180.0)] = Field(0, alias="adjustRoll")
    adjust_pitch: Optional[confloat(ge=-180.0, le=180.0)] = Field(
        0, alias="adjustPitch"
    )
    adjust_yaw: Optional[confloat(ge=-180.0, le=180.0)] = Field(0, alias="adjustYaw")
    invert_roll: Optional[bool] = Field(False, alias="invertRoll")
    invert_pitch: Optional[bool] = Field(False, alias="invertPitch")
    invert_yaw: Optional[bool] = Field(False, alias="invertYaw")
    fixed_roll: Optional[bool] = Field(True, alias="fixedRoll")
    fixed_pitch: Optional[bool] = Field(True, alias="fixedPitch")
    fixed_yaw: Optional[bool] = Field(True, alias="fixedYaw")


class VisConfigModel2(BaseModel):
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    opacity: Optional[confloat(ge=0.0, le=1.0)] = 1
    flow_animation_enabled: Optional[bool] = Field(False, alias="flowAnimationEnabled")
    flow_adaptive_scales_enabled: Optional[bool] = Field(
        True, alias="flowAdaptiveScalesEnabled"
    )
    flow_fade_enabled: Optional[bool] = Field(True, alias="flowFadeEnabled")
    flow_fade_amount: Optional[confloat(ge=0.0, le=100.0)] = Field(
        50, alias="flowFadeAmount"
    )
    max_top_flows_display_num: Optional[confloat(ge=0.0, le=10000.0)] = Field(
        5000, alias="maxTopFlowsDisplayNum"
    )
    flow_location_totals_enabled: Optional[bool] = Field(
        True, alias="flowLocationTotalsEnabled"
    )
    flow_clustering_enabled: Optional[bool] = Field(True, alias="flowClusteringEnabled")
    dark_base_map_enabled: Optional[bool] = Field(True, alias="darkBaseMapEnabled")


class VisConfigModel3(BaseModel):
    opacity: Optional[Opacity] = None
    thickness: Optional[confloat(ge=0.0, le=100.0)] = 2
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    size_range: Optional[List[confloat(ge=0.0, le=200.0)]] = Field(
        [0, 10], alias="sizeRange"
    )
    target_color: Optional[List[float]] = Field(None, alias="targetColor")


class VisConfigModel4(BaseModel):
    radius: Optional[confloat(ge=0.0, le=100.0)] = 10
    fixed_radius: Optional[bool] = Field(False, alias="fixedRadius")
    opacity: Optional[confloat(ge=0.0, le=1.0)] = 0.8
    outline: Optional[bool] = False
    thickness: Optional[confloat(ge=0.0, le=100.0)] = 2
    stroke_color: Optional[Union[Any, Union[Field0Model2, Field1]]] = Field(
        None, alias="strokeColor", description="Stroke color"
    )
    color_range: Optional[Union[Any, ColorRange]] = Field(
        None, alias="colorRange", description="Color range"
    )
    stroke_color_range: Optional[Union[Any, Field1Model1]] = Field(
        None, alias="strokeColorRange", description="Stroke color range"
    )
    radius_range: Optional[List[confloat(ge=0.0, le=500.0)]] = Field(
        [0, 50], alias="radiusRange"
    )
    filled: Optional[bool] = True
    billboard: Optional[bool] = False
    allow_hover: Optional[bool] = Field(True, alias="allowHover")
    show_neighbor_on_hover: Optional[bool] = Field(False, alias="showNeighborOnHover")
    show_highlight_color: Optional[bool] = Field(True, alias="showHighlightColor")


class TextLabelItem(BaseModel):
    size: Optional[confloat(ge=1.0, le=100.0)] = 18
    color: Field1Model2
    field: Optional[List[FieldItem]] = None
    offset: Optional[List[float]] = Field([0, 0], max_length=2, min_length=2)
    anchor: Optional[Anchor] = "start"
    alignment: Optional[Alignment] = "center"
    background: Optional[bool] = Field(
        None, description="Show background for text label"
    )
    background_color: Optional[Union[Any, Field1Model2]] = Field(
        None, alias="backgroundColor", description="Background color for text label"
    )
    outline_color: Optional[Field1Model2] = Field(
        None, alias="outlineColor", description="Outline color for text label"
    )
    outline_width: Optional[confloat(ge=0.0, le=1.0)] = Field(
        None, alias="outlineWidth", description="Outline width for text label"
    )


class Config(BaseModel):
    data_id: str = Field(
        ...,
        alias="dataId",
        description="The id of the dataset from which this layer was created",
    )
    label: Optional[str] = Field(None, description="The displayed layer label")
    color: Optional[Union[List[Union[ColorItem, Field0]], List[Field0]]] = Field(
        None, description="Layer color as RGB. e.g. `[255, 0, 0]`."
    )
    is_visible: Optional[bool] = Field(
        None, alias="isVisible", description="Layer visibility on the map."
    )
    hidden: Optional[bool] = Field(
        None,
        description="Hide layer from the layer panel. This will prevent user from editing the layer.",
    )
    legend: Optional[Legend] = None
    vis_config: VisConfigModel4 = Field(..., alias="visConfig")
    text_label: Optional[List[TextLabelItem]] = Field(None, alias="textLabel")
    highlight_color: Optional[Union[Any, Field1Model2]] = Field(
        None, alias="highlightColor", description="Highlight color"
    )
    column_mode: Literal["geojson"] = Field(
        ..., alias="columnMode", description="Column mode"
    )
    columns: Columns


class VisConfig1(BaseModel):
    opacity: Optional[Opacity] = None
    thickness: Optional[confloat(ge=0.0, le=100.0)] = 2
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    size_range: Optional[List[confloat(ge=0.0, le=200.0)]] = Field(
        [0, 10], alias="sizeRange"
    )
    target_color: Optional[List[float]] = Field(None, alias="targetColor")
    elevation_scale: Optional[confloat(ge=0.0, le=1000.0)] = Field(
        1, alias="elevationScale"
    )


class Config2(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: Optional[VisConfig1] = Field(None, alias="visConfig")
    column_mode: Literal["points"] = Field(
        "points", alias="columnMode", description="Column mode"
    )
    columns: Columns2


class Config3(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: Optional[VisConfig] = Field(None, alias="visConfig")
    column_mode: Literal["neighbors"] = Field(
        ..., alias="columnMode", description="Column mode"
    )
    columns: Columns3


class Layer2(BaseModel):
    id: Id
    type: Literal["line"]
    config: Union[Config2, Config3]
    visual_channels: Optional[VisualChannels1] = Field(None, alias="visualChannels")


class VisConfig2(BaseModel):
    opacity: Optional[Opacity] = None
    thickness: Optional[confloat(ge=0.0, le=100.0)] = 2
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    size_range: Optional[List[confloat(ge=0.0, le=200.0)]] = Field(
        [0, 10], alias="sizeRange"
    )
    target_color: Optional[List[float]] = Field(None, alias="targetColor")


class Config4(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: Optional[VisConfig2] = Field(None, alias="visConfig")
    highlight_color: Optional[Union[Any, Field1Model2]] = Field(
        None, alias="highlightColor", description="Highlight color"
    )
    column_mode: Literal["points"] = Field(
        "points", alias="columnMode", description="Column mode"
    )
    columns: Columns4


class Config5(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: Optional[VisConfigModel3] = Field(None, alias="visConfig")
    highlight_color: Optional[HighlightColor] = Field(None, alias="highlightColor")
    column_mode: Literal["neighbors"] = Field(
        ..., alias="columnMode", description="Column mode"
    )
    columns: Columns5


class Layer3(BaseModel):
    id: Id
    type: Literal["arc"]
    config: Union[Config4, Config5]
    visual_channels: VisualChannels2 = Field(..., alias="visualChannels")


class VisConfig3(BaseModel):
    opacity: Optional[Opacity] = None
    intensity: Optional[confloat(ge=0.01, le=20.0)] = Field(
        1,
        description="Value that is multiplied with the total weight at a pixel to obtain the final weight. A value larger than 1 biases the output color towards the higher end of the spectrum, and a value less than 1 biases the output color towards the lower end of the spectrum.",
    )
    threshold: Optional[confloat(ge=0.01, le=1.0)] = Field(
        0.18,
        description="A larger threshold smoothens the boundaries of color blobs, while making pixels with low weight harder to spot.",
    )
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    radius: Optional[confloat(ge=0.0, le=100.0)] = 20


class Config6(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    columns: Columns6
    vis_config: Optional[VisConfig3] = Field(None, alias="visConfig")


class Layer4(BaseModel):
    id: Id
    type: Literal["heatmap"]
    config: Config6
    visual_channels: VisualChannels3 = Field(..., alias="visualChannels")


class VisConfig4(BaseModel):
    opacity: Optional[Opacity] = None
    world_unit_size: Optional[confloat(ge=0.0, le=500.0)] = Field(
        1, alias="worldUnitSize"
    )
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    coverage: Optional[confloat(ge=0.0, le=1.0)] = 1
    size_range: Optional[List[confloat(ge=0.0, le=1000.0)]] = Field(
        [0, 500], alias="sizeRange"
    )
    percentile: Optional[List[confloat(ge=0.0, le=100.0)]] = [0, 100]
    elevation_percentile: Optional[List[confloat(ge=0.0, le=100.0)]] = Field(
        [0, 100], alias="elevationPercentile"
    )
    elevation_scale: Optional[confloat(ge=0.0, le=1000.0)] = Field(
        5, alias="elevationScale"
    )
    enable_elevation_zoom_factor: Optional[bool] = Field(
        True, alias="enableElevationZoomFactor"
    )
    fixed_height: Optional[bool] = Field(False, alias="fixedHeight")
    color_aggregation: Optional[ColorAggregation] = Field(
        None, alias="colorAggregation"
    )
    size_aggregation: Optional[ColorAggregation] = Field(None, alias="sizeAggregation")
    enable3d: Optional[bool] = False


class Config7(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    columns: Columns6
    vis_config: Optional[VisConfig4] = Field(None, alias="visConfig")


class Layer5(BaseModel):
    id: Id
    type: Literal["grid"]
    config: Config7
    visual_channels: VisualChannels4 = Field(..., alias="visualChannels")


class VisConfig5(BaseModel):
    opacity: Optional[Opacity] = None
    world_unit_size: Optional[confloat(ge=0.0, le=500.0)] = Field(
        1, alias="worldUnitSize"
    )
    resolution: Optional[confloat(ge=0.0, le=13.0)] = 8
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    coverage: Optional[confloat(ge=0.0, le=1.0)] = 1
    size_range: Optional[List[confloat(ge=0.0, le=1000.0)]] = Field(
        [0, 500], alias="sizeRange"
    )
    percentile: Optional[Percentile] = None
    elevation_percentile: Optional[ElevationPercentile] = Field(
        None, alias="elevationPercentile"
    )
    elevation_scale: Optional[confloat(ge=0.0, le=1000.0)] = Field(
        5, alias="elevationScale"
    )
    enable_elevation_zoom_factor: Optional[bool] = Field(
        True, alias="enableElevationZoomFactor"
    )
    fixed_height: Optional[bool] = Field(False, alias="fixedHeight")
    color_aggregation: Optional[ColorAggregation] = Field(
        None, alias="colorAggregation"
    )
    size_aggregation: Optional[ColorAggregation] = Field(None, alias="sizeAggregation")
    enable3d: Optional[bool] = False


class Config8(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    columns: Columns6
    vis_config: Optional[VisConfig5] = Field(None, alias="visConfig")


class Layer6(BaseModel):
    id: Id
    type: Literal["hexagon"]
    config: Config8
    visual_channels: VisualChannels5 = Field(..., alias="visualChannels")


class VisConfig6(BaseModel):
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    filled: Optional[bool] = True
    opacity: Optional[Opacity] = None
    outline: Optional[bool] = False
    stroke_color: Optional[Union[Any, Field1Model2]] = Field(
        None, alias="strokeColor", description="Stroke color"
    )
    stroke_color_range: Optional[Union[Any, Field1Model1]] = Field(
        None, alias="strokeColorRange", description="Stroke color range"
    )
    stroke_opacity: Optional[Opacity] = Field(None, alias="strokeOpacity")
    thickness: Optional[confloat(ge=0.0, le=100.0)] = 2
    coverage: Optional[confloat(ge=0.0, le=1.0)] = 1
    enable3d: Optional[bool] = False
    size_range: Optional[List[confloat(ge=0.0, le=1000.0)]] = Field(
        [0, 500], alias="sizeRange"
    )
    coverage_range: Optional[List[confloat(ge=0.0, le=1.0)]] = Field(
        [0, 1], alias="coverageRange"
    )
    elevation_scale: Optional[confloat(ge=0.0, le=1000.0)] = Field(
        5, alias="elevationScale"
    )
    enable_elevation_zoom_factor: Optional[bool] = Field(
        True, alias="enableElevationZoomFactor"
    )
    fixed_height: Optional[bool] = Field(False, alias="fixedHeight")


class VisConfig7(BaseModel):
    tile_url: Optional[str] = Field(None, alias="tileUrl")
    stroke_color: Optional[Union[Any, Field1Model2]] = Field(
        None, alias="strokeColor", description="Stroke color"
    )
    stroke_opacity: Optional[Opacity] = Field(None, alias="strokeOpacity")
    radius: Optional[confloat(ge=0.0, le=1000.0)] = 50
    enable3d: Optional[bool] = False
    transition: Optional[bool] = False
    height_range: Optional[List[confloat(ge=0.0, le=1000.0)]] = Field(
        [0, 500], alias="heightRange"
    )
    elevation_scale: Optional[confloat(ge=0.0, le=1000.0)] = Field(
        5, alias="elevationScale"
    )
    opacity: Optional[Opacity] = None
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    radius_by_zoom: Optional[Union[Any, RadiusByZoom]] = Field(
        None, alias="radiusByZoom"
    )
    tile_query: Optional[str] = Field(None, alias="tileQuery")
    show_outlines: Optional[bool] = Field(False, alias="showOutlines")
    show_points: Optional[bool] = Field(False, alias="showPoints")
    dynamic_color: Optional[bool] = Field(False, alias="dynamicColor")
    cell_per_tile_threshold: Optional[confloat(ge=0.0, le=5.0)] = Field(
        2, alias="cellPerTileThreshold"
    )
    use_percentile_range: Optional[bool] = Field(False, alias="usePercentileRange")
    percentile_range: Optional[List[confloat(ge=0.0, le=100.0)]] = Field(
        [0, 99], alias="percentileRange"
    )


class Config10(BaseModel):
    data_id: Optional[str] = Field(
        ...,
        alias="dataId",
        description="The id of the dataset from which this layer was created",
    )
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: Optional[VisConfig7] = Field(None, alias="visConfig")


class Layer8(BaseModel):
    id: Id
    type: Literal["hexTile"]
    config: Config10
    visual_channels: VisualChannels7 = Field(..., alias="visualChannels")


class VisConfig8(BaseModel):
    opacity: Optional[Opacity] = None
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    filled: Optional[bool] = True
    thickness: Optional[confloat(ge=0.0, le=100.0)] = 0.5
    stroke_color: Optional[Union[Any, Field1Model2]] = Field(
        None, alias="strokeColor", description="Stroke color"
    )
    stroke_color_range: Optional[Union[Any, Field1Model1]] = Field(
        None, alias="strokeColorRange", description="Stroke color range"
    )
    size_range: Optional[List[confloat(ge=0.0, le=200.0)]] = Field(
        [0, 10], alias="sizeRange"
    )
    stroked: Optional[bool] = True
    enable3d: Optional[bool] = False
    elevation_scale: Optional[confloat(ge=0.0, le=1000.0)] = Field(
        5, alias="elevationScale"
    )
    enable_elevation_zoom_factor: Optional[bool] = Field(
        True, alias="enableElevationZoomFactor"
    )
    fixed_height: Optional[bool] = Field(False, alias="fixedHeight")
    height_range: Optional[List[confloat(ge=0.0, le=1000.0)]] = Field(
        [0, 500], alias="heightRange"
    )
    wireframe: Optional[bool] = False


class Config11(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    columns: Columns10
    vis_config: Optional[VisConfig8] = Field(None, alias="visConfig")


class Layer9(BaseModel):
    id: Id
    type: Literal["s2"]
    config: Config11
    visual_channels: VisualChannels8 = Field(..., alias="visualChannels")


class VisConfig9(BaseModel):
    opacity: Optional[Opacity] = None
    cluster_radius: Optional[confloat(ge=1.0, le=500.0)] = Field(
        40, alias="clusterRadius"
    )
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    radius_range: Optional[List[confloat(ge=0.0, le=150.0)]] = Field(
        [1, 40], alias="radiusRange"
    )
    color_aggregation: Optional[ColorAggregation] = Field(
        None, alias="colorAggregation"
    )


class Config12(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    columns: Columns11
    vis_config: Optional[VisConfig9] = Field(None, alias="visConfig")


class Layer10(BaseModel):
    id: Id
    type: Literal["cluster"]
    config: Config12
    visual_channels: VisualChannels9 = Field(..., alias="visualChannels")


class VisConfig10(BaseModel):
    radius: Optional[confloat(ge=0.0, le=100.0)] = 10
    fixed_radius: Optional[bool] = Field(False, alias="fixedRadius")
    opacity: Optional[Opacity] = None
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    radius_range: Optional[List[confloat(ge=0.0, le=500.0)]] = Field(
        [0, 50], alias="radiusRange"
    )
    billboard: Optional[bool] = False


class Config13(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    columns: Columns12
    vis_config: Optional[VisConfig10] = Field(None, alias="visConfig")
    highlight_color: Optional[Union[Any, Field1Model2]] = Field(
        None, alias="highlightColor", description="Highlight color"
    )


class Layer11(BaseModel):
    id: Id
    type: Literal["icon"]
    config: Config13
    visual_channels: VisualChannels10 = Field(..., alias="visualChannels")


class VisConfig11(BaseModel):
    opacity: Optional[Opacity] = None
    stroke_opacity: Optional[confloat(ge=0.0, le=1.0)] = Field(
        0.8, alias="strokeOpacity"
    )
    thickness: Optional[confloat(ge=0.0, le=100.0)] = 0.5
    stroke_color: Optional[Union[Any, Field1Model2]] = Field(
        None, alias="strokeColor", description="Stroke color"
    )
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    stroke_color_range: Optional[Union[Any, Field1Model1]] = Field(
        None, alias="strokeColorRange"
    )
    radius: Optional[confloat(ge=0.0, le=100.0)] = 10
    size_range: Optional[List[confloat(ge=0.0, le=200.0)]] = Field(
        [0, 10], alias="sizeRange"
    )
    radius_range: Optional[List[confloat(ge=0.0, le=500.0)]] = Field(
        [0, 50], alias="radiusRange"
    )
    height_range: Optional[List[confloat(ge=0.0, le=1000.0)]] = Field(
        [0, 500], alias="heightRange"
    )
    elevation_scale: Optional[confloat(ge=0.0, le=1000.0)] = Field(
        5, alias="elevationScale"
    )
    stroked: Optional[bool] = True
    filled: Optional[bool] = False
    enable3d: Optional[bool] = False
    wireframe: Optional[bool] = False
    fixed_height: Optional[bool] = Field(False, alias="fixedHeight")


class VisConfig12(BaseModel):
    opacity: Optional[Opacity] = None
    thickness: Optional[confloat(ge=0.0, le=100.0)] = 0.5
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    trail_length: Optional[confloat(ge=1.0, le=1000.0)] = Field(
        180, alias="trailLength"
    )
    fade_trail: Optional[bool] = Field(True, alias="fadeTrail")
    billboard: Optional[bool] = False
    size_range: Optional[List[confloat(ge=0.0, le=200.0)]] = Field(
        [0, 10], alias="sizeRange"
    )
    size_scale: Optional[confloat(ge=-10.0, le=10.0)] = Field(1, alias="sizeScale")
    scenegraph: Optional[str] = None
    scenegraph_enabled: Optional[bool] = Field(False, alias="scenegraphEnabled")
    scenegraph_color_enabled: Optional[bool] = Field(
        False, alias="scenegraphColorEnabled"
    )
    scenegraph_use_trail_color: Optional[bool] = Field(
        False, alias="scenegraphUseTrailColor"
    )
    scenegraph_color: Optional[Union[Any, List[float]]] = Field(
        None, alias="scenegraphColor"
    )
    scenegraph_custom_model_url: Optional[str] = Field(
        "", alias="scenegraphCustomModelUrl"
    )
    adjust_roll: Optional[confloat(ge=-180.0, le=180.0)] = Field(0, alias="adjustRoll")
    adjust_pitch: Optional[confloat(ge=-180.0, le=180.0)] = Field(
        0, alias="adjustPitch"
    )
    adjust_yaw: Optional[confloat(ge=-180.0, le=180.0)] = Field(0, alias="adjustYaw")
    invert_roll: Optional[bool] = Field(False, alias="invertRoll")
    invert_pitch: Optional[bool] = Field(False, alias="invertPitch")
    invert_yaw: Optional[bool] = Field(False, alias="invertYaw")
    fixed_roll: Optional[bool] = Field(True, alias="fixedRoll")
    fixed_pitch: Optional[bool] = Field(True, alias="fixedPitch")
    fixed_yaw: Optional[bool] = Field(True, alias="fixedYaw")


class VisConfig13(BaseModel):
    preset: Optional[Preset] = None
    mosaic_id: Optional[str] = Field(None, alias="mosaicId")
    use_stac_searching: Optional[bool] = Field(False, alias="useSTACSearching")
    stac_search_provider: Optional[StacSearchProvider] = Field(
        None, alias="stacSearchProvider"
    )
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    dynamic_color: Optional[bool] = Field(False, alias="dynamicColor")
    colormap_id: Optional[ColormapId] = Field(None, alias="colormapId")
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    linear_rescaling_factor: Optional[List[confloat(ge=0.0, le=1.0)]] = Field(
        [0, 1], alias="linearRescalingFactor"
    )
    non_linear_rescaling: Optional[bool] = Field(True, alias="nonLinearRescaling")
    gamma_contrast_factor: Optional[confloat(ge=0.0, le=3.0)] = Field(
        1, alias="gammaContrastFactor"
    )
    sigmoidal_contrast_factor: Optional[confloat(ge=0.0, le=50.0)] = Field(
        0, alias="sigmoidalContrastFactor"
    )
    sigmoidal_bias_factor: Optional[confloat(ge=0.0, le=1.0)] = Field(
        0.5, alias="sigmoidalBiasFactor"
    )
    saturation_value: Optional[confloat(ge=0.0, le=2.0)] = Field(
        1, alias="saturationValue"
    )
    filter_enabled: Optional[bool] = Field(False, alias="filterEnabled")
    filter_range: Optional[List[confloat(ge=-1.0, le=1.0)]] = Field(
        [-1, 1], alias="filterRange"
    )
    opacity: Optional[confloat(ge=0.0, le=1.0)] = 1
    field_stac_query: Optional[str] = Field(None, alias="_stacQuery")
    single_band_name: Optional[str] = Field(None, alias="singleBandName")
    enable_terrain: Optional[bool] = Field(None, alias="enableTerrain")


class Config18(BaseModel):
    data_id: Optional[str] = Field(
        ...,
        alias="dataId",
        description="The id of the dataset from which this layer was created",
    )
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: Optional[VisConfig13] = Field(None, alias="visConfig")


class Layer14(BaseModel):
    id: Id
    type: Literal["rasterTile"]
    config: Config18


class VisConfig14(BaseModel):
    tile_url: Optional[str] = Field(None, alias="tileUrl")
    stroked: Optional[bool] = None
    stroke_color: Optional[Union[Any, Field1Model2]] = Field(
        None, alias="strokeColor", description="Stroke color"
    )
    stroke_opacity: Optional[Opacity] = Field(None, alias="strokeOpacity")
    stroke_width: Optional[confloat(ge=0.0, le=100.0)] = Field(0.5, alias="strokeWidth")
    radius: Optional[confloat(ge=0.0, le=1000.0)] = 50
    enable3d: Optional[bool] = False
    transition: Optional[bool] = False
    height_range: Optional[List[confloat(ge=0.0, le=1000.0)]] = Field(
        [0, 500], alias="heightRange"
    )
    elevation_scale: Optional[confloat(ge=0.0, le=1000.0)] = Field(
        5, alias="elevationScale"
    )
    opacity: Optional[Opacity] = None
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    stroke_color_range: Optional[Union[Any, Field1Model1]] = Field(
        None, alias="strokeColorRange"
    )
    radius_by_zoom: Optional[Union[Any, Field1Model]] = Field(
        None, alias="radiusByZoom"
    )
    dynamic_color: Optional[bool] = Field(None, alias="dynamicColor")


class Config19(BaseModel):
    data_id: Optional[str] = Field(
        ...,
        alias="dataId",
        description="The id of the dataset from which this layer was created",
    )
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: Optional[VisConfig14] = Field(None, alias="visConfig")


class Layer15(BaseModel):
    id: Id
    type: Literal["vectorTile"]
    config: Config19
    visual_channels: VisualChannels13 = Field(..., alias="visualChannels")


class VisConfig15(BaseModel):
    opacity: Optional[Opacity] = None
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    size_scale: Optional[confloat(ge=0.0, le=1000.0)] = Field(10, alias="sizeScale")
    angle_x: Optional[confloat(ge=0.0, le=360.0)] = Field(0, alias="angleX")
    angle_y: Optional[confloat(ge=0.0, le=360.0)] = Field(0, alias="angleY")
    angle_z: Optional[confloat(ge=0.0, le=360.0)] = Field(0, alias="angleZ")
    scenegraph: Optional[str] = "default-model"
    scenegraph_color_enabled: Optional[bool] = Field(
        False, alias="scenegraphColorEnabled"
    )
    scenegraph_color: Optional[Union[Any, List[float]]] = Field(
        None, alias="scenegraphColor"
    )
    scenegraph_custom_model_url: Optional[str] = Field(
        "", alias="scenegraphCustomModelUrl"
    )


class Config20(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    columns: Columns17
    vis_config: Optional[VisConfig15] = Field(None, alias="visConfig")


class Layer16(BaseModel):
    id: Id
    type: Literal["3D"]
    config: Config20
    visual_channels: VisualChannels14 = Field(..., alias="visualChannels")


class VisConfig16(BaseModel):
    color_range: Optional[Field1Model1] = Field(None, alias="colorRange")
    opacity: Optional[confloat(ge=0.0, le=1.0)] = 1
    flow_animation_enabled: Optional[bool] = Field(False, alias="flowAnimationEnabled")
    flow_adaptive_scales_enabled: Optional[bool] = Field(
        True, alias="flowAdaptiveScalesEnabled"
    )
    flow_fade_enabled: Optional[bool] = Field(True, alias="flowFadeEnabled")
    flow_fade_amount: Optional[confloat(ge=0.0, le=100.0)] = Field(
        50, alias="flowFadeAmount"
    )
    max_top_flows_display_num: Optional[confloat(ge=0.0, le=10000.0)] = Field(
        5000, alias="maxTopFlowsDisplayNum"
    )
    flow_location_totals_enabled: Optional[bool] = Field(
        True, alias="flowLocationTotalsEnabled"
    )
    flow_clustering_enabled: Optional[bool] = Field(True, alias="flowClusteringEnabled")
    dark_base_map_enabled: Optional[bool] = Field(True, alias="darkBaseMapEnabled")


class Config21(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: Optional[VisConfig16] = Field(None, alias="visConfig")
    column_mode: Literal["LAT_LNG"] = Field(
        "LAT_LNG", alias="columnMode", description="Column mode"
    )
    columns: Columns18


class Config22(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: Optional[VisConfigModel2] = Field(None, alias="visConfig")
    column_mode: Literal["H3"] = Field(
        ..., alias="columnMode", description="Column mode"
    )
    columns: Columns19


class Layer17(BaseModel):
    id: Id
    type: Literal["flow"]
    config: Union[Config21, Config22]


class Config23(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: Optional[VisConfig17] = Field(None, alias="visConfig")


class Layer18(BaseModel):
    id: Id
    type: Literal["WMS"]
    config: Config23


class Config24(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: VisConfig18 = Field(..., alias="visConfig")


class Layer19(BaseModel):
    id: Id
    type: Literal["tile3d"]
    config: Config24


class TextLabelItem1(BaseModel):
    size: Optional[confloat(ge=1.0, le=100.0)] = 18
    color: Field1Model2
    field: Optional[List[FieldItem1]] = None
    offset: Optional[List[float]] = Field([0, 0], max_length=2, min_length=2)
    anchor: Optional[Anchor] = "start"
    alignment: Optional[Alignment] = "center"
    background: Optional[bool] = Field(
        None, description="Show background for text label"
    )
    background_color: Optional[Union[Any, Field1Model2]] = Field(
        None, alias="backgroundColor", description="Background color for text label"
    )
    outline_color: Optional[Field1Model2] = Field(
        None, alias="outlineColor", description="Outline color for text label"
    )
    outline_width: Optional[confloat(ge=0.0, le=1.0)] = Field(
        None, alias="outlineWidth", description="Outline width for text label"
    )


class TextLabel(RootModel[List[TextLabelItem1]]):
    root: List[TextLabelItem1]


class ItemsModel(BaseModel):
    size: Optional[confloat(ge=1.0, le=100.0)] = 18
    color: Field1Model2
    field: Optional[List[FieldItem2]] = None
    offset: Optional[List[float]] = Field([0, 0], max_length=2, min_length=2)
    anchor: Optional[Anchor] = "start"
    alignment: Optional[Alignment] = "center"
    background: Optional[bool] = Field(
        None, description="Show background for text label"
    )
    background_color: Optional[Union[Any, Field1Model2]] = Field(
        None, alias="backgroundColor", description="Background color for text label"
    )
    outline_color: Optional[Field1Model2] = Field(
        None, alias="outlineColor", description="Outline color for text label"
    )
    outline_width: Optional[confloat(ge=0.0, le=1.0)] = Field(
        None, alias="outlineWidth", description="Outline width for text label"
    )


class VisConfigModel5(BaseModel):
    radius: Optional[confloat(ge=0.0, le=100.0)] = 10
    fixed_radius: Optional[bool] = Field(False, alias="fixedRadius")
    opacity: Optional[confloat(ge=0.0, le=1.0)] = 0.8
    outline: Optional[bool] = False
    thickness: Optional[confloat(ge=0.0, le=100.0)] = 2
    stroke_color: Optional[Union[Any, Union[Field0Model2, Field1]]] = Field(
        None, alias="strokeColor", description="Stroke color"
    )
    color_range: Optional[Union[Any, ColorRange1]] = Field(
        None, alias="colorRange", description="Color range"
    )
    stroke_color_range: Optional[Union[Any, Field1Model1]] = Field(
        None, alias="strokeColorRange", description="Stroke color range"
    )
    radius_range: Optional[List[confloat(ge=0.0, le=500.0)]] = Field(
        [0, 50], alias="radiusRange"
    )
    filled: Optional[bool] = True
    billboard: Optional[bool] = False
    allow_hover: Optional[bool] = Field(True, alias="allowHover")
    show_neighbor_on_hover: Optional[bool] = Field(False, alias="showNeighborOnHover")
    show_highlight_color: Optional[bool] = Field(True, alias="showHighlightColor")


class TextLabelModel(RootModel[List[ItemsModel]]):
    root: List[ItemsModel]


class Config1(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: VisConfigModel5 = Field(..., alias="visConfig")
    text_label: Optional[TextLabel] = Field(None, alias="textLabel")
    highlight_color: Optional[HighlightColor] = Field(None, alias="highlightColor")
    column_mode: Literal["points"] = Field(
        ..., alias="columnMode", description="Column mode"
    )
    columns: Columns1


class Layer1(BaseModel):
    id: str = Field(..., description="Layer id, use a string without space")
    type: Literal["point"]
    config: Union[Config, Config1]
    visual_channels: Optional[VisualChannels] = Field(None, alias="visualChannels")


class Config9(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    columns: Columns9
    vis_config: Optional[VisConfig6] = Field(None, alias="visConfig")
    text_label: Optional[List[ItemsModel]] = Field(None, alias="textLabel")
    highlight_color: Optional[Union[Any, Field1Model2]] = Field(
        None, alias="highlightColor", description="Highlight color"
    )


class Layer7(BaseModel):
    id: Id
    type: Literal["hexagonId"]
    config: Config9
    visual_channels: VisualChannels6 = Field(..., alias="visualChannels")


class Config14(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: Optional[VisConfig11] = Field(None, alias="visConfig")
    text_label: Optional[List[ItemsModel]] = Field(None, alias="textLabel")
    highlight_color: Optional[Union[Any, Field1Model2]] = Field(
        None, alias="highlightColor", description="Highlight color"
    )
    column_mode: Literal["geojson"] = Field(
        ..., alias="columnMode", description="Column mode"
    )
    columns: Columns13


class Config15(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: Optional[VisConfigModel] = Field(None, alias="visConfig")
    text_label: Optional[TextLabelModel] = Field(None, alias="textLabel")
    highlight_color: Optional[HighlightColor] = Field(None, alias="highlightColor")
    column_mode: Literal["polygon"] = Field(
        ..., alias="columnMode", description="Column mode"
    )
    columns: Columns14


class Layer12(BaseModel):
    id: Id
    type: Literal["geojson"]
    config: Union[Config14, Config15]
    visual_channels: VisualChannels11 = Field(..., alias="visualChannels")


class Config16(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: Optional[VisConfig12] = Field(None, alias="visConfig")
    text_label: Optional[List[ItemsModel]] = Field(None, alias="textLabel")
    column_mode: Literal["geojson"] = Field(
        "geojson", alias="columnMode", description="Column mode"
    )
    columns: Columns15


class Config17(BaseModel):
    data_id: DataId = Field(..., alias="dataId")
    label: Optional[Label] = None
    color: Optional[Color] = None
    is_visible: Optional[IsVisible] = Field(None, alias="isVisible")
    hidden: Optional[Hidden] = None
    legend: Optional[Legend] = None
    vis_config: Optional[VisConfigModel1] = Field(None, alias="visConfig")
    text_label: Optional[TextLabelModel] = Field(None, alias="textLabel")
    column_mode: Literal["table"] = Field(
        ..., alias="columnMode", description="Column mode"
    )
    columns: Columns16


class Layer13(BaseModel):
    id: Id
    type: Literal["trip"]
    config: Union[Config16, Config17]
    visual_channels: VisualChannels12 = Field(..., alias="visualChannels")


class Layer(
    RootModel[
        Union[
            Layer1,
            Layer2,
            Layer3,
            Layer4,
            Layer5,
            Layer6,
            Layer7,
            Layer8,
            Layer9,
            Layer10,
            Layer11,
            Layer12,
            Layer13,
            Layer14,
            Layer15,
            Layer16,
            Layer17,
            Layer18,
            Layer19,
        ]
    ]
):
    root: Union[
        Layer1,
        Layer2,
        Layer3,
        Layer4,
        Layer5,
        Layer6,
        Layer7,
        Layer8,
        Layer9,
        Layer10,
        Layer11,
        Layer12,
        Layer13,
        Layer14,
        Layer15,
        Layer16,
        Layer17,
        Layer18,
        Layer19,
    ] = Field(..., title="Layer")
