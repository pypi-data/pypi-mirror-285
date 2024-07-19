from dataclasses import dataclass, field, replace
from typing import List, Literal, Optional

import glom

from foursquare.map_sdk.api.base import generate_uuid, remove_none_values
from foursquare.map_sdk.api.color import Color, ColorRange
from foursquare.map_sdk.api.columns import LatLngColumns


class HexbinLayerColumns(LatLngColumns):
    ...


@dataclass
class HexbinLayer:
    """
    The Hexbin Layer display distributions of aggregate metrics such as point count within each hexbin, aggregate of a numerical field, or mode/unique count of a string field.

    Required:
      data_id: str - Dataset ID
      columns: HexbinLayerColumns - Mapping between data columns and layer properties

    Optional:
      id: str - Layer ID (use a string without space)
      label: str - The displayed layer label
      color: Color - Layer color
      is_visible: bool - Layer visibility on the map
      hidden: bool - Hide layer from the layer panel. This will prevent user from editing the layer
      include_legend: bool - Control of the layer is included in the legend
      opacity: float - Opacity of the layer
      world_unit_size: float - World unit size
      resolution: int - Bin resolution (0 - 13)
      color_range: ColorRange - Mapping configuration between color and values
      coverage: float - Scaling factor for the geometry (0-1)
      size_range: List[float] - A range of values that size can take
      percentile: List[float] - Percentile amount
      elevation_percentile: List[float] - Elevation percentile amount
      elevation_scale: float - Factor for scaling the elevation values with
      enable_elevation_zoom_factor: bool - Is elevation zoom factor enabled
      fixed_height: bool - Use a fixed height value
      color_aggregation: Literal["count", "average", "maximum", "minimum", "median", "stdev", "sum", "variance", "mode", "countUnique"] - The aggregation mode for color
      size_aggregation: Literal["count", "average", "maximum", "minimum", "median", "stdev", "sum", "variance", "mode", "countUnique"] - The aggregation mode for size
      enable_3d: bool - Is 3D mode enabled
      color_column: str - Name of the data column with color data
      color_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional color column type override
      color_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for color values
      size_column: str - Name of the data column with size data
      size_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional size column type override
      size_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for size values
    """

    data_id: str
    columns: HexbinLayerColumns

    id: Optional[str] = field(default_factory=generate_uuid)
    label: Optional[str] = None
    color: Optional[Color] = None
    is_visible: Optional[bool] = None
    hidden: Optional[bool] = None
    include_legend: Optional[bool] = None
    opacity: Optional[float] = None
    world_unit_size: Optional[float] = None
    resolution: Optional[int] = None
    color_range: Optional[ColorRange] = None
    coverage: Optional[float] = None
    size_range: Optional[List[float]] = None
    percentile: Optional[List[float]] = None
    elevation_percentile: Optional[List[float]] = None
    elevation_scale: Optional[float] = None
    enable_elevation_zoom_factor: Optional[bool] = None
    fixed_height: Optional[bool] = None
    color_aggregation: Optional[
        Literal[
            "count",
            "average",
            "maximum",
            "minimum",
            "median",
            "stdev",
            "sum",
            "variance",
            "mode",
            "countUnique",
        ]
    ] = None
    size_aggregation: Optional[
        Literal[
            "count",
            "average",
            "maximum",
            "minimum",
            "median",
            "stdev",
            "sum",
            "variance",
            "mode",
            "countUnique",
        ]
    ] = None
    enable_3d: Optional[bool] = None
    color_column: Optional[str] = None
    color_column_type: Optional[
        Literal["string", "real", "timestamp", "integer", "boolean", "date"]
    ] = None
    color_column_scale: Optional[
        Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"]
    ] = None
    size_column: Optional[str] = None
    size_column_type: Optional[
        Literal["string", "real", "timestamp", "integer", "boolean", "date"]
    ] = None
    size_column_scale: Optional[
        Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"]
    ] = None

    def to_json(self) -> dict:
        result: dict = {}
        glom.assign(result, "type", "hexagon")
        glom.assign(result, "config.dataId", self.data_id, dict)
        glom.assign(result, "config.columns.lat", self.columns.lat, dict)
        glom.assign(result, "config.columns.lng", self.columns.lng, dict)
        glom.assign(result, "id", self.id, dict)
        glom.assign(result, "config.label", self.label, dict)
        glom.assign(
            result, "config.color", self.color.to_json() if self.color else None, dict
        )
        glom.assign(result, "config.isVisible", self.is_visible, dict)
        glom.assign(result, "config.hidden", self.hidden, dict)
        if self.include_legend is not None:
            glom.assign(result, "config.legend.isIncluded", self.include_legend, dict)
        glom.assign(result, "config.visConfig.opacity", self.opacity, dict)
        glom.assign(
            result, "config.visConfig.worldUnitSize", self.world_unit_size, dict
        )
        glom.assign(result, "config.visConfig.resolution", self.resolution, dict)
        glom.assign(
            result,
            "config.visConfig.colorRange",
            self.color_range.to_json() if self.color_range else None,
            dict,
        )
        glom.assign(result, "config.visConfig.coverage", self.coverage, dict)
        glom.assign(result, "config.visConfig.sizeRange", self.size_range, dict)
        glom.assign(result, "config.visConfig.percentile", self.percentile, dict)
        glom.assign(
            result,
            "config.visConfig.elevationPercentile",
            self.elevation_percentile,
            dict,
        )
        glom.assign(
            result, "config.visConfig.elevationScale", self.elevation_scale, dict
        )
        glom.assign(
            result,
            "config.visConfig.enableElevationZoomFactor",
            self.enable_elevation_zoom_factor,
            dict,
        )
        glom.assign(result, "config.visConfig.fixedHeight", self.fixed_height, dict)
        glom.assign(
            result, "config.visConfig.colorAggregation", self.color_aggregation, dict
        )
        glom.assign(
            result, "config.visConfig.sizeAggregation", self.size_aggregation, dict
        )
        glom.assign(result, "config.visConfig.enable3d", self.enable_3d, dict)
        glom.assign(result, "visualChannels.colorField.name", self.color_column, dict)
        glom.assign(
            result, "visualChannels.colorField.type", self.color_column_type, dict
        )
        glom.assign(result, "visualChannels.colorScale", self.color_column_scale, dict)
        glom.assign(result, "visualChannels.sizeField.name", self.size_column, dict)
        glom.assign(
            result, "visualChannels.sizeField.type", self.size_column_type, dict
        )
        glom.assign(result, "visualChannels.sizeScale", self.size_column_scale, dict)
        return remove_none_values(result)

    @staticmethod
    def from_json(json: dict) -> "HexbinLayer":
        assert json["type"] == "hexagon", "Layer 'type' is not 'hexagon'"
        obj = HexbinLayer(
            data_id=glom.glom(json, "config.dataId"),
            columns=HexbinLayerColumns(
                lat=glom.glom(json, "config.columns.lat"),
                lng=glom.glom(json, "config.columns.lng"),
            ),
        )
        obj.id = glom.glom(json, "id", default=None)
        obj.label = glom.glom(json, "config.label", default=None)
        __color = glom.glom(json, "config.color", default=None)
        obj.color = Color.from_json(__color) if __color else None
        obj.is_visible = glom.glom(json, "config.isVisible", default=None)
        obj.hidden = glom.glom(json, "config.hidden", default=None)
        obj.include_legend = glom.glom(json, "config.legend.isIncluded", default=None)
        obj.opacity = glom.glom(json, "config.visConfig.opacity", default=None)
        obj.world_unit_size = glom.glom(
            json, "config.visConfig.worldUnitSize", default=None
        )
        obj.resolution = glom.glom(json, "config.visConfig.resolution", default=None)
        __color_range = glom.glom(json, "config.visConfig.colorRange", default=None)
        obj.color_range = ColorRange.from_json(__color_range) if __color_range else None
        obj.coverage = glom.glom(json, "config.visConfig.coverage", default=None)
        obj.size_range = glom.glom(json, "config.visConfig.sizeRange", default=None)
        obj.percentile = glom.glom(json, "config.visConfig.percentile", default=None)
        obj.elevation_percentile = glom.glom(
            json, "config.visConfig.elevationPercentile", default=None
        )
        obj.elevation_scale = glom.glom(
            json, "config.visConfig.elevationScale", default=None
        )
        obj.enable_elevation_zoom_factor = glom.glom(
            json, "config.visConfig.enableElevationZoomFactor", default=None
        )
        obj.fixed_height = glom.glom(json, "config.visConfig.fixedHeight", default=None)
        obj.color_aggregation = glom.glom(
            json, "config.visConfig.colorAggregation", default=None
        )
        obj.size_aggregation = glom.glom(
            json, "config.visConfig.sizeAggregation", default=None
        )
        obj.enable_3d = glom.glom(json, "config.visConfig.enable3d", default=None)
        obj.color_column = glom.glom(
            json, "visualChannels.colorField.name", default=None
        )
        obj.color_column_type = glom.glom(
            json, "visualChannels.colorField.type", default=None
        )
        obj.color_column_scale = glom.glom(
            json, "visualChannels.colorScale", default=None
        )
        obj.size_column = glom.glom(json, "visualChannels.sizeField.name", default=None)
        obj.size_column_type = glom.glom(
            json, "visualChannels.sizeField.type", default=None
        )
        obj.size_column_scale = glom.glom(
            json, "visualChannels.sizeScale", default=None
        )
        return obj

    def clone(self) -> "HexbinLayer":
        return replace(self)
