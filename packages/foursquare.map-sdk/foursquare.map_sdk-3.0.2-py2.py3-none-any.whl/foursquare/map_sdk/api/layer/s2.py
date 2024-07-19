from dataclasses import dataclass, field, replace
from typing import List, Literal, Optional

import glom

from foursquare.map_sdk.api.base import generate_uuid, remove_none_values
from foursquare.map_sdk.api.color import Color, ColorRange
from foursquare.map_sdk.api.columns import S2Columns


class S2LayerColumns(S2Columns):
    ...


@dataclass
class S2Layer:
    """
    S2 layers visualize spatial data using S2 geometry.

    Required:
      data_id: str - Dataset ID
      columns: S2LayerColumns - Mapping between data columns and layer properties

    Optional:
      id: str - Layer ID (use a string without space)
      label: str - The displayed layer label
      color: Color - Layer color
      is_visible: bool - Layer visibility on the map
      hidden: bool - Hide layer from the layer panel. This will prevent user from editing the layer
      include_legend: bool - Control of the layer is included in the legend
      opacity: float - Opacity of the layer
      color_range: ColorRange - Mapping configuration between color and values
      filled: bool - Fill the layer
      thickness: float - Outline thickness
      stroke_color: Color - Stroke color
      stroke_color_range: ColorRange - Mapping configuration between stroke color and values
      size_range: List[float] - A range of values that size can take
      stroked: bool - Is stroke enabled
      enable_3d: bool - Is 3D mode enabled
      elevation_scale: float - Factor for scaling the elevation values with
      enable_elevation_zoom_factor: bool - Is elevation zoom factor enabled
      fixed_height: bool - Use a fixed height value
      height_range: List[float] - A range of values that height can take
      wireframe: bool - Is wireframe enabled
      color_column: str - Name of the data column with color data
      color_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional color column type override
      color_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for color values
      stroke_color_column: str - Name of the data column with stroke color data
      stroke_color_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional stroke color column type override
      stroke_color_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for stroke color values
      size_column: str - Name of the data column with size data
      size_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional size column type override
      size_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for size values
      height_column: str - Name of the data column with height data
      height_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional height column type override
      height_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for height values
    """

    data_id: str
    columns: S2LayerColumns

    id: Optional[str] = field(default_factory=generate_uuid)
    label: Optional[str] = None
    color: Optional[Color] = None
    is_visible: Optional[bool] = None
    hidden: Optional[bool] = None
    include_legend: Optional[bool] = None
    opacity: Optional[float] = None
    color_range: Optional[ColorRange] = None
    filled: Optional[bool] = None
    thickness: Optional[float] = None
    stroke_color: Optional[Color] = None
    stroke_color_range: Optional[ColorRange] = None
    size_range: Optional[List[float]] = None
    stroked: Optional[bool] = None
    enable_3d: Optional[bool] = None
    elevation_scale: Optional[float] = None
    enable_elevation_zoom_factor: Optional[bool] = None
    fixed_height: Optional[bool] = None
    height_range: Optional[List[float]] = None
    wireframe: Optional[bool] = None
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
    size_column: Optional[str] = None
    size_column_type: Optional[
        Literal["string", "real", "timestamp", "integer", "boolean", "date"]
    ] = None
    size_column_scale: Optional[
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
        glom.assign(result, "type", "s2")
        glom.assign(result, "config.dataId", self.data_id, dict)
        glom.assign(result, "config.columns.token", self.columns.token, dict)
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
            result,
            "config.visConfig.colorRange",
            self.color_range.to_json() if self.color_range else None,
            dict,
        )
        glom.assign(result, "config.visConfig.filled", self.filled, dict)
        glom.assign(result, "config.visConfig.thickness", self.thickness, dict)
        glom.assign(
            result,
            "config.visConfig.strokeColor",
            self.stroke_color.to_json() if self.stroke_color else None,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.strokeColorRange",
            self.stroke_color_range.to_json() if self.stroke_color_range else None,
            dict,
        )
        glom.assign(result, "config.visConfig.sizeRange", self.size_range, dict)
        glom.assign(result, "config.visConfig.stroked", self.stroked, dict)
        glom.assign(result, "config.visConfig.enable3d", self.enable_3d, dict)
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
        glom.assign(result, "config.visConfig.heightRange", self.height_range, dict)
        glom.assign(result, "config.visConfig.wireframe", self.wireframe, dict)
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
        glom.assign(result, "visualChannels.sizeField.name", self.size_column, dict)
        glom.assign(
            result, "visualChannels.sizeField.type", self.size_column_type, dict
        )
        glom.assign(result, "visualChannels.sizeScale", self.size_column_scale, dict)
        glom.assign(result, "visualChannels.heightField.name", self.height_column, dict)
        glom.assign(
            result, "visualChannels.heightField.type", self.height_column_type, dict
        )
        glom.assign(
            result, "visualChannels.heightScale", self.height_column_scale, dict
        )
        return remove_none_values(result)

    @staticmethod
    def from_json(json: dict) -> "S2Layer":
        assert json["type"] == "s2", "Layer 'type' is not 's2'"
        obj = S2Layer(
            data_id=glom.glom(json, "config.dataId"),
            columns=S2LayerColumns(token=glom.glom(json, "config.columns.token")),
        )
        obj.id = glom.glom(json, "id", default=None)
        obj.label = glom.glom(json, "config.label", default=None)
        __color = glom.glom(json, "config.color", default=None)
        obj.color = Color.from_json(__color) if __color else None
        obj.is_visible = glom.glom(json, "config.isVisible", default=None)
        obj.hidden = glom.glom(json, "config.hidden", default=None)
        obj.include_legend = glom.glom(json, "config.legend.isIncluded", default=None)
        obj.opacity = glom.glom(json, "config.visConfig.opacity", default=None)
        __color_range = glom.glom(json, "config.visConfig.colorRange", default=None)
        obj.color_range = ColorRange.from_json(__color_range) if __color_range else None
        obj.filled = glom.glom(json, "config.visConfig.filled", default=None)
        obj.thickness = glom.glom(json, "config.visConfig.thickness", default=None)
        __stroke_color = glom.glom(json, "config.visConfig.strokeColor", default=None)
        obj.stroke_color = Color.from_json(__stroke_color) if __stroke_color else None
        __stroke_color_range = glom.glom(
            json, "config.visConfig.strokeColorRange", default=None
        )
        obj.stroke_color_range = (
            ColorRange.from_json(__stroke_color_range) if __stroke_color_range else None
        )
        obj.size_range = glom.glom(json, "config.visConfig.sizeRange", default=None)
        obj.stroked = glom.glom(json, "config.visConfig.stroked", default=None)
        obj.enable_3d = glom.glom(json, "config.visConfig.enable3d", default=None)
        obj.elevation_scale = glom.glom(
            json, "config.visConfig.elevationScale", default=None
        )
        obj.enable_elevation_zoom_factor = glom.glom(
            json, "config.visConfig.enableElevationZoomFactor", default=None
        )
        obj.fixed_height = glom.glom(json, "config.visConfig.fixedHeight", default=None)
        obj.height_range = glom.glom(json, "config.visConfig.heightRange", default=None)
        obj.wireframe = glom.glom(json, "config.visConfig.wireframe", default=None)
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
        obj.size_column = glom.glom(json, "visualChannels.sizeField.name", default=None)
        obj.size_column_type = glom.glom(
            json, "visualChannels.sizeField.type", default=None
        )
        obj.size_column_scale = glom.glom(
            json, "visualChannels.sizeScale", default=None
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

    def clone(self) -> "S2Layer":
        return replace(self)
