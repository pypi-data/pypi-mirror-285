from dataclasses import dataclass, field, replace
from typing import List, Literal, Optional, Union

import glom

from foursquare.map_sdk.api.base import generate_uuid, remove_none_values
from foursquare.map_sdk.api.color import Color, ColorRange
from foursquare.map_sdk.api.columns import GeojsonColumns, LatLngAltNborColumns
from foursquare.map_sdk.api.text_label import TextLabel


class PointLayerGeojsonColumns(GeojsonColumns):
    ...


class PointLayerNeighborsColumns(LatLngAltNborColumns):
    ...


@dataclass
class PointLayer:
    """
    The Point Layer draws dots on the map corresponding to latitude/longitude coordinates.

    Required:
      data_id: str - Dataset ID
      columns: Union[PointLayerGeojsonColumns, PointLayerNeighborsColumns] - Mapping between data columns and layer properties

    Optional:
      id: str - Layer ID (use a string without space)
      label: str - The displayed layer label
      color: Color - Layer color
      is_visible: bool - Layer visibility on the map
      hidden: bool - Hide layer from the layer panel. This will prevent user from editing the layer
      include_legend: bool - Control of the layer is included in the legend
      highlight_color: Color - Highlight color
      text_label: List[TextLabel] - Layer's label information visible on hover
      radius: float - Radius of points
      fixed_radius: bool - Use a fixed radius value
      opacity: float - Opacity of the layer
      outline: bool - Use outlines on the layer
      thickness: float - Outline thickness
      stroke_color: Color - Stroke color
      radius_range: List[float] - A range of values that radius can take
      filled: bool - Fill the layer
      billboard: bool - Whether the layer is billboarded
      allow_hover: bool - Control if hover is allowed
      show_neighbor_on_hover: bool - Show neighbor on hover
      show_highlight_color: bool - Color of the hover highlight
      color_range: ColorRange - Mapping configuration between color and values
      stroke_color_range: ColorRange - Mapping configuration between stroke color and values
      color_column: str - Name of the data column with color data
      color_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional color column type override
      color_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for color values
      stroke_color_column: str - Name of the data column with stroke color data
      stroke_color_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional stroke color column type override
      stroke_color_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for stroke color values
      size_column: str - Name of the data column with size data
      size_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional size column type override
      size_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for size values
    """

    data_id: str
    columns: Union[PointLayerGeojsonColumns, PointLayerNeighborsColumns]

    id: Optional[str] = field(default_factory=generate_uuid)
    label: Optional[str] = None
    color: Optional[Color] = None
    is_visible: Optional[bool] = None
    hidden: Optional[bool] = None
    include_legend: Optional[bool] = None
    highlight_color: Optional[Color] = None
    text_label: Optional[List[TextLabel]] = None
    radius: Optional[float] = None
    fixed_radius: Optional[bool] = None
    opacity: Optional[float] = None
    outline: Optional[bool] = None
    thickness: Optional[float] = None
    stroke_color: Optional[Color] = None
    radius_range: Optional[List[float]] = None
    filled: Optional[bool] = None
    billboard: Optional[bool] = None
    allow_hover: Optional[bool] = None
    show_neighbor_on_hover: Optional[bool] = None
    show_highlight_color: Optional[bool] = None
    color_range: Optional[ColorRange] = None
    stroke_color_range: Optional[ColorRange] = None
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

    def to_json(self) -> dict:
        result: dict = {}
        glom.assign(result, "type", "point")
        glom.assign(result, "config.dataId", self.data_id, dict)
        glom.assign(result, "config.columnMode", self.columns.mode, dict)
        glom.assign(result, "config.columns", self.columns.to_json(), dict)
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
            "config.highlightColor",
            self.highlight_color.to_json() if self.highlight_color else None,
            dict,
        )
        glom.assign(
            result,
            "config.textLabel",
            [label.to_json() for label in self.text_label] if self.text_label else None,
            dict,
        )
        glom.assign(result, "config.visConfig.radius", self.radius, dict)
        glom.assign(result, "config.visConfig.fixedRadius", self.fixed_radius, dict)
        glom.assign(result, "config.visConfig.opacity", self.opacity, dict)
        glom.assign(result, "config.visConfig.outline", self.outline, dict)
        glom.assign(result, "config.visConfig.thickness", self.thickness, dict)
        glom.assign(
            result,
            "config.visConfig.strokeColor",
            self.stroke_color.to_json() if self.stroke_color else None,
            dict,
        )
        glom.assign(result, "config.visConfig.radiusRange", self.radius_range, dict)
        glom.assign(result, "config.visConfig.filled", self.filled, dict)
        glom.assign(result, "config.visConfig.billboard", self.billboard, dict)
        glom.assign(result, "config.visConfig.allowHover", self.allow_hover, dict)
        glom.assign(
            result,
            "config.visConfig.showNeighborOnHover",
            self.show_neighbor_on_hover,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.showHighlightColor",
            self.show_highlight_color,
            dict,
        )
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
        return remove_none_values(result)

    @staticmethod
    def from_json(json: dict):
        assert json["type"] == "point", "Layer 'type' is not 'point'"
        obj = PointLayer(
            data_id=glom.glom(json, "config.dataId"),
            columns={
                # pylint: disable-next=unnecessary-lambda
                PointLayerNeighborsColumns.mode: lambda columns: PointLayerNeighborsColumns.from_json(
                    columns
                ),
                # pylint: disable-next=unnecessary-lambda
                PointLayerGeojsonColumns.mode: lambda columns: PointLayerGeojsonColumns.from_json(
                    columns
                ),
            }[glom.glom(json, "config.columnMode")](glom.glom(json, "config.columns")),
        )
        obj.id = glom.glom(json, "id", default=None)
        obj.label = glom.glom(json, "config.label", default=None)
        __color = glom.glom(json, "config.color", default=None)
        obj.color = Color.from_json(__color) if __color else None
        obj.is_visible = glom.glom(json, "config.isVisible", default=None)
        obj.hidden = glom.glom(json, "config.hidden", default=None)
        obj.include_legend = glom.glom(json, "config.legend.isIncluded", default=None)
        __highlight_color = glom.glom(json, "config.highlightColor", default=None)
        obj.highlight_color = (
            Color.from_json(__highlight_color) if __highlight_color else None
        )
        __text_label = glom.glom(json, "config.textLabel", default=None)
        obj.text_label = (
            [TextLabel.from_json(label) for label in __text_label]
            if __text_label
            else None
        )
        obj.radius = glom.glom(json, "config.visConfig.radius", default=None)
        obj.fixed_radius = glom.glom(json, "config.visConfig.fixedRadius", default=None)
        obj.opacity = glom.glom(json, "config.visConfig.opacity", default=None)
        obj.outline = glom.glom(json, "config.visConfig.outline", default=None)
        obj.thickness = glom.glom(json, "config.visConfig.thickness", default=None)
        __stroke_color = glom.glom(json, "config.visConfig.strokeColor", default=None)
        obj.stroke_color = Color.from_json(__stroke_color) if __stroke_color else None
        obj.radius_range = glom.glom(json, "config.visConfig.radiusRange", default=None)
        obj.filled = glom.glom(json, "config.visConfig.filled", default=None)
        obj.billboard = glom.glom(json, "config.visConfig.billboard", default=None)
        obj.allow_hover = glom.glom(json, "config.visConfig.allowHover", default=None)
        obj.show_neighbor_on_hover = glom.glom(
            json, "config.visConfig.showNeighborOnHover", default=None
        )
        obj.show_highlight_color = glom.glom(
            json, "config.visConfig.showHighlightColor", default=None
        )
        __color_range = glom.glom(json, "config.visConfig.colorRange", default=None)
        obj.color_range = ColorRange.from_json(__color_range) if __color_range else None
        __stroke_color_range = glom.glom(
            json, "config.visConfig.strokeColorRange", default=None
        )
        obj.stroke_color_range = (
            ColorRange.from_json(__stroke_color_range) if __stroke_color_range else None
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
        obj.size_column = glom.glom(json, "visualChannels.sizeField.name", default=None)
        obj.size_column_type = glom.glom(
            json, "visualChannels.sizeField.type", default=None
        )
        obj.size_column_scale = glom.glom(
            json, "visualChannels.sizeScale", default=None
        )
        return obj

    def clone(self) -> "PointLayer":
        return replace(self)
