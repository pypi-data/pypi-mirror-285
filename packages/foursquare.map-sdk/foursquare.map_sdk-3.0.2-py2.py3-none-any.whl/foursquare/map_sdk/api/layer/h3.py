from dataclasses import dataclass, field, replace
from typing import List, Literal, Optional

import glom

from foursquare.map_sdk.api.base import generate_uuid, remove_none_values
from foursquare.map_sdk.api.color import Color, ColorRange
from foursquare.map_sdk.api.columns import H3Columns
from foursquare.map_sdk.api.text_label import TextLabel


class H3LayerColumns(H3Columns):
    ...


@dataclass
class H3Layer:
    """
    H3 layers visualize spatial data using H3 Hexagonal Hierarchical Spatial Index.

    Required:
      data_id: str - Dataset ID
      columns: H3LayerColumns - Mapping between data columns and layer properties

    Optional:
      id: str - Layer ID (use a string without space)
      label: str - The displayed layer label
      color: Color - Layer color
      is_visible: bool - Layer visibility on the map
      hidden: bool - Hide layer from the layer panel. This will prevent user from editing the layer
      include_legend: bool - Control of the layer is included in the legend
      text_label: List[TextLabel] - Layer's label information visible on hover
      highlight_color: Color - Highlight color
      color_range: ColorRange - Mapping configuration between color and values
      filled: bool - Fill the layer
      opacity: float - Opacity of the layer
      outline: bool - Use outlines on the layer
      stroke_color: Color - Stroke color
      stroke_color_range: ColorRange - Mapping configuration between stroke color and values
      stroke_opacity: float - Stroke opacity of the layer
      thickness: float - Outline thickness
      coverage: float - Scaling factor for the geometry (0-1)
      enable_3d: bool - Is 3D mode enabled
      size_range: List[float] - A range of values that size can take
      coverage_range: List[float] - A range of values that coverage can take
      elevation_scale: float - Factor for scaling the elevation values with
      enable_elevation_zoom_factor: bool - Is elevation zoom factor enabled
      fixed_height: bool - Use a fixed height value
      color_column: str - Name of the data column with color data
      color_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional color column type override
      color_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for color values
      stroke_color_column: str - Name of the data column with stroke color data
      stroke_color_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional stroke color column type override
      stroke_color_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for stroke color values
      size_column: str - Name of the data column with size data
      size_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional size column type override
      size_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for size values
      coverage_column: str - Name of the data column with coverage data
      coverage_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional coverage column type override
      coverage_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for coverage values
    """

    data_id: str
    columns: H3LayerColumns

    id: Optional[str] = field(default_factory=generate_uuid)
    label: Optional[str] = None
    color: Optional[Color] = None
    is_visible: Optional[bool] = None
    hidden: Optional[bool] = None
    include_legend: Optional[bool] = None
    text_label: Optional[List[TextLabel]] = None
    highlight_color: Optional[Color] = None
    color_range: Optional[ColorRange] = None
    filled: Optional[bool] = None
    opacity: Optional[float] = None
    outline: Optional[bool] = None
    stroke_color: Optional[Color] = None
    stroke_color_range: Optional[ColorRange] = None
    stroke_opacity: Optional[float] = None
    thickness: Optional[float] = None
    coverage: Optional[float] = None
    enable_3d: Optional[bool] = None
    size_range: Optional[List[float]] = None
    coverage_range: Optional[List[float]] = None
    elevation_scale: Optional[float] = None
    enable_elevation_zoom_factor: Optional[bool] = None
    fixed_height: Optional[bool] = None
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
    coverage_column: Optional[str] = None
    coverage_column_type: Optional[
        Literal["string", "real", "timestamp", "integer", "boolean", "date"]
    ] = None
    coverage_column_scale: Optional[
        Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"]
    ] = None

    def to_json(self) -> dict:
        result: dict = {}
        glom.assign(result, "type", "hexagonId")
        glom.assign(result, "config.dataId", self.data_id, dict)
        glom.assign(result, "config.columns.hex_id", self.columns.hex_id, dict)
        glom.assign(result, "id", self.id, dict)
        glom.assign(result, "config.label", self.label, dict)
        glom.assign(
            result, "config.color", self.color.to_json() if self.color else None, dict
        )
        glom.assign(result, "config.isVisible", self.is_visible, dict)
        glom.assign(result, "config.hidden", self.hidden, dict)
        if self.include_legend is not None:
            glom.assign(result, "config.legend.isIncluded", self.include_legend, dict)
        glom.assign(
            result,
            "config.textLabel",
            [label.to_json() for label in self.text_label] if self.text_label else None,
            dict,
        )
        glom.assign(
            result,
            "config.highlightColor",
            self.highlight_color.to_json() if self.highlight_color else None,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.colorRange",
            self.color_range.to_json() if self.color_range else None,
            dict,
        )
        glom.assign(result, "config.visConfig.filled", self.filled, dict)
        glom.assign(result, "config.visConfig.opacity", self.opacity, dict)
        glom.assign(result, "config.visConfig.outline", self.outline, dict)
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
        glom.assign(result, "config.visConfig.strokeOpacity", self.stroke_opacity, dict)
        glom.assign(result, "config.visConfig.thickness", self.thickness, dict)
        glom.assign(result, "config.visConfig.coverage", self.coverage, dict)
        glom.assign(result, "config.visConfig.enable3d", self.enable_3d, dict)
        glom.assign(result, "config.visConfig.sizeRange", self.size_range, dict)
        glom.assign(result, "config.visConfig.coverageRange", self.coverage_range, dict)
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
        glom.assign(
            result, "visualChannels.coverageField.name", self.coverage_column, dict
        )
        glom.assign(
            result, "visualChannels.coverageField.type", self.coverage_column_type, dict
        )
        glom.assign(
            result, "visualChannels.coverageScale", self.coverage_column_scale, dict
        )
        return remove_none_values(result)

    @staticmethod
    def from_json(json: dict) -> "H3Layer":
        assert json["type"] == "hexagonId", "Layer 'type' is not 'hexagonId'"
        obj = H3Layer(
            data_id=glom.glom(json, "config.dataId"),
            columns=H3LayerColumns(hex_id=glom.glom(json, "config.columns.hex_id")),
        )
        obj.id = glom.glom(json, "id", default=None)
        obj.label = glom.glom(json, "config.label", default=None)
        __color = glom.glom(json, "config.color", default=None)
        obj.color = Color.from_json(__color) if __color else None
        obj.is_visible = glom.glom(json, "config.isVisible", default=None)
        obj.hidden = glom.glom(json, "config.hidden", default=None)
        obj.include_legend = glom.glom(json, "config.legend.isIncluded", default=None)
        __text_label = glom.glom(json, "config.textLabel", default=None)
        obj.text_label = (
            [TextLabel.from_json(label) for label in __text_label]
            if __text_label
            else None
        )
        __highlight_color = glom.glom(json, "config.highlightColor", default=None)
        obj.highlight_color = (
            Color.from_json(__highlight_color) if __highlight_color else None
        )
        __color_range = glom.glom(json, "config.visConfig.colorRange", default=None)
        obj.color_range = ColorRange.from_json(__color_range) if __color_range else None
        obj.filled = glom.glom(json, "config.visConfig.filled", default=None)
        obj.opacity = glom.glom(json, "config.visConfig.opacity", default=None)
        obj.outline = glom.glom(json, "config.visConfig.outline", default=None)
        __stroke_color = glom.glom(json, "config.visConfig.strokeColor", default=None)
        obj.stroke_color = Color.from_json(__stroke_color) if __stroke_color else None
        __stroke_color_range = glom.glom(
            json, "config.visConfig.strokeColorRange", default=None
        )
        obj.stroke_color_range = (
            ColorRange.from_json(__stroke_color_range) if __stroke_color_range else None
        )
        obj.stroke_opacity = glom.glom(
            json, "config.visConfig.strokeOpacity", default=None
        )
        obj.thickness = glom.glom(json, "config.visConfig.thickness", default=None)
        obj.coverage = glom.glom(json, "config.visConfig.coverage", default=None)
        obj.enable_3d = glom.glom(json, "config.visConfig.enable3d", default=None)
        obj.size_range = glom.glom(json, "config.visConfig.sizeRange", default=None)
        obj.coverage_range = glom.glom(
            json, "config.visConfig.coverageRange", default=None
        )
        obj.elevation_scale = glom.glom(
            json, "config.visConfig.elevationScale", default=None
        )
        obj.enable_elevation_zoom_factor = glom.glom(
            json, "config.visConfig.enableElevationZoomFactor", default=None
        )
        obj.fixed_height = glom.glom(json, "config.visConfig.fixedHeight", default=None)
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
        obj.coverage_column = glom.glom(
            json, "visualChannels.coverageField.name", default=None
        )
        obj.coverage_column_type = glom.glom(
            json, "visualChannels.coverageField.type", default=None
        )
        obj.coverage_column_scale = glom.glom(
            json, "visualChannels.coverageScale", default=None
        )
        return obj

    def clone(self) -> "H3Layer":
        return replace(self)
