from dataclasses import dataclass, field, replace
from typing import Dict, List, Literal, Optional

import glom

from foursquare.map_sdk.api.base import generate_uuid, remove_none_values
from foursquare.map_sdk.api.color import Color, ColorRange


@dataclass
class VectorLayer:
    """
    Vector layers use the three basic GIS features - lines, points, and polygons - to represent real-world features in digital format.

    Required:
      data_id: str - Dataset ID

    Optional:
      id: str - Layer ID (use a string without space)
      label: str - The displayed layer label
      color: Color - Layer color
      is_visible: bool - Layer visibility on the map
      hidden: bool - Hide layer from the layer panel. This will prevent user from editing the layer
      include_legend: bool - Control of the layer is included in the legend
      tile_url: str - A URL for the tiles
      stroked: bool - Is stroke enabled
      stroke_color: Color - Stroke color
      stroke_opacity: float - Stroke opacity of the layer
      stroke_width: float - Stroke width
      radius: float - Radius of points
      enable_3d: bool - Is 3D mode enabled
      transition: bool - Controls whether to use transition
      height_range: List[float] - A range of values that height can take
      elevation_scale: float - Factor for scaling the elevation values with
      opacity: float - Opacity of the layer
      color_range: ColorRange - Mapping configuration between color and values
      stroke_color_range: ColorRange - Mapping configuration between stroke color and values
      radius_by_zoom: Dict[int, float] - Dynamically select radius based on the zoom level
      dynamic_color: bool - Color ranges are dynamicly calculated and mapped based on the content visible in the viewport
      color_column: str - Name of the data column with color data
      color_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional color column type override
      color_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for color values
      stroke_color_column: str - Name of the data column with stroke color data
      stroke_color_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional stroke color column type override
      stroke_color_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for stroke color values
      height_column: str - Name of the data column with height data
      height_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional height column type override
      height_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for height values
    """

    data_id: str

    id: Optional[str] = field(default_factory=generate_uuid)
    label: Optional[str] = None
    color: Optional[Color] = None
    is_visible: Optional[bool] = None
    hidden: Optional[bool] = None
    include_legend: Optional[bool] = None
    tile_url: Optional[str] = None
    stroked: Optional[bool] = None
    stroke_color: Optional[Color] = None
    stroke_opacity: Optional[float] = None
    stroke_width: Optional[float] = None
    radius: Optional[float] = None
    enable_3d: Optional[bool] = None
    transition: Optional[bool] = None
    height_range: Optional[List[float]] = None
    elevation_scale: Optional[float] = None
    opacity: Optional[float] = None
    color_range: Optional[ColorRange] = None
    stroke_color_range: Optional[ColorRange] = None
    radius_by_zoom: Optional[Dict[int, float]] = None
    dynamic_color: Optional[bool] = None
    color_column: Optional[str] = None
    color_column_type: Optional[
        Literal["string", "real", "timestamp", "integer", "boolean", "date"]
    ] = None
    color_column_scale: Optional[
        Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"]
    ] = None
    stroke_color_column: Optional[str] = None
    stroke_color_column_type: Optional[
        Literal["string", "real", "timestamp", "integer", "boolean", "date"]
    ] = None
    stroke_color_column_scale: Optional[
        Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"]
    ] = None
    height_column: Optional[str] = None
    height_column_type: Optional[
        Literal["string", "real", "timestamp", "integer", "boolean", "date"]
    ] = None
    height_column_scale: Optional[
        Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"]
    ] = None

    def to_json(self) -> dict:
        result: dict = {}
        glom.assign(result, "type", "vectorTile")
        glom.assign(result, "config.dataId", self.data_id, dict)
        glom.assign(result, "id", self.id, dict)
        glom.assign(result, "config.label", self.label, dict)
        glom.assign(
            result, "config.color", self.color.to_json() if self.color else None, dict
        )
        glom.assign(result, "config.isVisible", self.is_visible, dict)
        glom.assign(result, "config.hidden", self.hidden, dict)
        if self.include_legend is not None:
            glom.assign(result, "config.legend.isIncluded", self.include_legend, dict)
        glom.assign(result, "config.visConfig.tileUrl", self.tile_url, dict)
        glom.assign(result, "config.visConfig.stroked", self.stroked, dict)
        glom.assign(
            result,
            "config.visConfig.strokeColor",
            self.stroke_color.to_json() if self.stroke_color else None,
            dict,
        )
        glom.assign(result, "config.visConfig.strokeOpacity", self.stroke_opacity, dict)
        glom.assign(result, "config.visConfig.strokeWidth", self.stroke_width, dict)
        glom.assign(result, "config.visConfig.radius", self.radius, dict)
        glom.assign(result, "config.visConfig.enable3d", self.enable_3d, dict)
        glom.assign(result, "config.visConfig.transition", self.transition, dict)
        glom.assign(result, "config.visConfig.heightRange", self.height_range, dict)
        glom.assign(
            result, "config.visConfig.elevationScale", self.elevation_scale, dict
        )
        glom.assign(result, "config.visConfig.opacity", self.opacity, dict)
        glom.assign(
            result,
            "config.visConfig.colorRange",
            self.color_range.to_json() if self.color_range else None,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.strokeColorRange",
            self.stroke_color_range.to_json() if self.stroke_color_range else None,
            dict,
        )
        if self.radius_by_zoom is not None:
            glom.assign(
                result,
                "config.visConfig.radiusByZoom.stops",
                [[z, r] for (z, r) in self.radius_by_zoom.items()],
                dict,
            )
        glom.assign(result, "config.visConfig.dynamicColor", self.dynamic_color, dict)
        glom.assign(result, "visualChannels.colorField.name", self.color_column, dict)
        glom.assign(
            result, "visualChannels.colorField.type", self.color_column_type, dict
        )
        glom.assign(result, "visualChannels.colorScale", self.color_column_scale, dict)
        glom.assign(
            result,
            "visualChannels.strokeColorField.name",
            self.stroke_color_column,
            dict,
        )
        glom.assign(
            result,
            "visualChannels.strokeColorField.type",
            self.stroke_color_column_type,
            dict,
        )
        glom.assign(
            result,
            "visualChannels.strokeColorScale",
            self.stroke_color_column_scale,
            dict,
        )
        glom.assign(result, "visualChannels.heightField.name", self.height_column, dict)
        glom.assign(
            result, "visualChannels.heightField.type", self.height_column_type, dict
        )
        glom.assign(
            result, "visualChannels.heightScale", self.height_column_scale, dict
        )
        return remove_none_values(result)

    @staticmethod
    def from_json(json: dict) -> "VectorLayer":
        assert json["type"] == "vectorTile", "Layer 'type' is not 'vectorTile'"
        obj = VectorLayer(data_id=glom.glom(json, "config.dataId"))
        obj.id = glom.glom(json, "id", default=None)
        obj.label = glom.glom(json, "config.label", default=None)
        __color = glom.glom(json, "config.color", default=None)
        obj.color = Color.from_json(__color) if __color else None
        obj.is_visible = glom.glom(json, "config.isVisible", default=None)
        obj.hidden = glom.glom(json, "config.hidden", default=None)
        obj.include_legend = glom.glom(json, "config.legend.isIncluded", default=None)
        obj.tile_url = glom.glom(json, "config.visConfig.tileUrl", default=None)
        obj.stroked = glom.glom(json, "config.visConfig.stroked", default=None)
        __stroke_color = glom.glom(json, "config.visConfig.strokeColor", default=None)
        obj.stroke_color = Color.from_json(__stroke_color) if __stroke_color else None
        obj.stroke_opacity = glom.glom(
            json, "config.visConfig.strokeOpacity", default=None
        )
        obj.stroke_width = glom.glom(json, "config.visConfig.strokeWidth", default=None)
        obj.radius = glom.glom(json, "config.visConfig.radius", default=None)
        obj.enable_3d = glom.glom(json, "config.visConfig.enable3d", default=None)
        obj.transition = glom.glom(json, "config.visConfig.transition", default=None)
        obj.height_range = glom.glom(json, "config.visConfig.heightRange", default=None)
        obj.elevation_scale = glom.glom(
            json, "config.visConfig.elevationScale", default=None
        )
        obj.opacity = glom.glom(json, "config.visConfig.opacity", default=None)
        __color_range = glom.glom(json, "config.visConfig.colorRange", default=None)
        obj.color_range = ColorRange.from_json(__color_range) if __color_range else None
        __stroke_color_range = glom.glom(
            json, "config.visConfig.strokeColorRange", default=None
        )
        obj.stroke_color_range = (
            ColorRange.from_json(__stroke_color_range) if __stroke_color_range else None
        )
        __radius_by_zoom = glom.glom(
            json, "config.visConfig.radiusByZoom.stops", default=None
        )
        if __radius_by_zoom is None:
            obj.radius_by_zoom = None
        else:
            obj.radius_by_zoom = {}
            for [z, r] in __radius_by_zoom:
                obj.radius_by_zoom[z] = r
        obj.dynamic_color = glom.glom(
            json, "config.visConfig.dynamicColor", default=None
        )
        obj.color_column = glom.glom(
            json, "visualChannels.colorField.name", default=None
        )
        obj.color_column_type = glom.glom(
            json, "visualChannels.colorField.type", default=None
        )
        obj.color_column_scale = glom.glom(
            json, "visualChannels.colorScale", default=None
        )
        obj.stroke_color_column = glom.glom(
            json, "visualChannels.strokeColorField.name", default=None
        )
        obj.stroke_color_column_type = glom.glom(
            json, "visualChannels.strokeColorField.type", default=None
        )
        obj.stroke_color_column_scale = glom.glom(
            json, "visualChannels.strokeColorScale", default=None
        )
        obj.height_column = glom.glom(
            json, "visualChannels.heightField.name", default=None
        )
        obj.height_column_type = glom.glom(
            json, "visualChannels.heightField.type", default=None
        )
        obj.height_column_scale = glom.glom(
            json, "visualChannels.heightScale", default=None
        )
        return obj

    def clone(self) -> "VectorLayer":
        return replace(self)
