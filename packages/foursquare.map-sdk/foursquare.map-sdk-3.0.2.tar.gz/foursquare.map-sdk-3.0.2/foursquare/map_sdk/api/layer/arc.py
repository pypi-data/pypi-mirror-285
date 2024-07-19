from dataclasses import dataclass, field, replace
from typing import List, Literal, Optional, Union

import glom

from foursquare.map_sdk.api.base import generate_uuid, remove_none_values
from foursquare.map_sdk.api.color import Color, ColorRange
from foursquare.map_sdk.api.columns import LatLngPairColumns, NborLatLngColumns


class ArcLayerPairsColumns(LatLngPairColumns):
    ...


class ArcLayerNeighborsColumns(NborLatLngColumns):
    ...


@dataclass
class ArcLayer:
    """
    The Arc Layer draws a 3D arc between a set of points. Arc layers don't show routes between points, instead show the distance between the two points. The tallest arc represents the greatest distance.

    Required:
      data_id: str - Dataset ID
      columns: Union[ArcLayerPairsColumns, ArcLayerNeighborsColumns] - Mapping between data columns and layer properties

    Optional:
      id: str - Layer ID (use a string without space)
      label: str - The displayed layer label
      color: Color - Layer color
      is_visible: bool - Layer visibility on the map
      hidden: bool - Hide layer from the layer panel. This will prevent user from editing the layer
      highlight_color: Color - Highlight color
      include_legend: bool - Control of the layer is included in the legend
      opacity: float - Opacity of the layer
      thickness: float - Outline thickness
      color_range: ColorRange - Mapping configuration between color and values
      size_range: List[float] - A range of values that size can take
      target_color: Color - Target color
      color_column: str - Name of the data column with color data
      color_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional color column type override
      color_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for color values
      size_column: str - Name of the data column with size data
      size_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional size column type override
      size_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for size values
    """

    data_id: str
    columns: Union[ArcLayerPairsColumns, ArcLayerNeighborsColumns]

    id: Optional[str] = field(default_factory=generate_uuid)
    label: Optional[str] = None
    color: Optional[Color] = None
    is_visible: Optional[bool] = None
    hidden: Optional[bool] = None
    highlight_color: Optional[Color] = None
    include_legend: Optional[bool] = None
    opacity: Optional[float] = None
    thickness: Optional[float] = None
    color_range: Optional[ColorRange] = None
    size_range: Optional[List[float]] = None
    target_color: Optional[Color] = None
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
        glom.assign(result, "type", "arc")
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
        glom.assign(
            result,
            "config.highlightColor",
            self.highlight_color.to_json() if self.highlight_color else None,
            dict,
        )
        if self.include_legend is not None:
            glom.assign(result, "config.legend.isIncluded", self.include_legend, dict)
        glom.assign(result, "config.visConfig.opacity", self.opacity, dict)
        glom.assign(result, "config.visConfig.thickness", self.thickness, dict)
        glom.assign(
            result,
            "config.visConfig.colorRange",
            self.color_range.to_json() if self.color_range else None,
            dict,
        )
        glom.assign(result, "config.visConfig.sizeRange", self.size_range, dict)
        glom.assign(
            result,
            "config.visConfig.targetColor",
            self.target_color.to_json() if self.target_color else None,
            dict,
        )
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
    def from_json(json: dict) -> "ArcLayer":
        assert json["type"] == "arc", "Layer 'type' is not 'arc'"
        obj = ArcLayer(
            data_id=glom.glom(json, "config.dataId"),
            columns={
                # pylint: disable-next=unnecessary-lambda
                ArcLayerPairsColumns.mode: lambda columns: ArcLayerPairsColumns.from_json(
                    columns
                ),
                # pylint: disable-next=unnecessary-lambda
                ArcLayerNeighborsColumns.mode: lambda columns: ArcLayerNeighborsColumns.from_json(
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
        __highlight_color = glom.glom(json, "config.highlightColor", default=None)
        obj.highlight_color = (
            Color.from_json(__highlight_color) if __highlight_color else None
        )
        obj.include_legend = glom.glom(json, "config.legend.isIncluded", default=None)
        obj.opacity = glom.glom(json, "config.visConfig.opacity", default=None)
        obj.thickness = glom.glom(json, "config.visConfig.thickness", default=None)
        __color_range = glom.glom(json, "config.visConfig.colorRange", default=None)
        obj.color_range = ColorRange.from_json(__color_range) if __color_range else None
        obj.size_range = glom.glom(json, "config.visConfig.sizeRange", default=None)
        __target_color = glom.glom(json, "config.visConfig.targetColor", default=None)
        obj.target_color = Color.from_json(__target_color) if __target_color else None
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

    def clone(self) -> "ArcLayer":
        return replace(self)
