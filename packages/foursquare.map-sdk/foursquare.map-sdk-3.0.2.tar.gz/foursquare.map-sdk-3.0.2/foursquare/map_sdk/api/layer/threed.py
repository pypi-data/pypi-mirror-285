from dataclasses import dataclass, field, replace
from typing import Literal, Optional

import glom

from foursquare.map_sdk.api.base import generate_uuid, remove_none_values
from foursquare.map_sdk.api.color import Color, ColorRange
from foursquare.map_sdk.api.columns import LatLngAltColumns


class ThreeDLayerColumns(LatLngAltColumns):
    ...


@dataclass
class ThreeDLayer:
    """
    3D layer displays 3D models on map by using latitude and longitude coordinates.

    Required:
      data_id: str - Dataset ID
      columns: ThreeDLayerColumns - Mapping between data columns and layer properties

    Optional:
      id: str - Layer ID (use a string without space)
      label: str - The displayed layer label
      color: Color - Layer color
      is_visible: bool - Layer visibility on the map
      hidden: bool - Hide layer from the layer panel. This will prevent user from editing the layer
      include_legend: bool - Control of the layer is included in the legend
      opacity: float - Opacity of the layer
      color_range: ColorRange - Mapping configuration between color and values
      size_scale: float - A scaling factor
      angle_x: float - Additional X angle offset
      angle_y: float - Additional Y angle offset
      angle_z: float - Additional Z angle offset
      model_3d: Literal["airplane", "helicopter", "bicycle", "scooter", "car", "truck", "semitruck", "cargoship", "boeing777", "uber-evtol", "hang-glider"] - One of the built-in 3D models to use
      model_3d_custom_url: str - URL of a custom 3D model to load and use
      model_3d_color_enabled: bool - Color 3D models used
      model_3d_color: Color - A fixed color for 3D models
      color_column: str - Name of the data column with color data
      color_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional color column type override
      color_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for color values
      size_column: str - Name of the data column with size data
      size_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional size column type override
      size_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for size values
    """

    data_id: str
    columns: ThreeDLayerColumns

    id: Optional[str] = field(default_factory=generate_uuid)
    label: Optional[str] = None
    color: Optional[Color] = None
    is_visible: Optional[bool] = None
    hidden: Optional[bool] = None
    include_legend: Optional[bool] = None
    opacity: Optional[float] = None
    color_range: Optional[ColorRange] = None
    size_scale: Optional[float] = None
    angle_x: Optional[float] = None
    angle_y: Optional[float] = None
    angle_z: Optional[float] = None
    model_3d: Optional[
        Literal[
            "airplane",
            "helicopter",
            "bicycle",
            "scooter",
            "car",
            "truck",
            "semitruck",
            "cargoship",
            "boeing777",
            "uber-evtol",
            "hang-glider",
        ]
    ] = None
    model_3d_custom_url: Optional[str] = None
    model_3d_color_enabled: Optional[bool] = None
    model_3d_color: Optional[Color] = None
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
        glom.assign(result, "type", "3D")
        glom.assign(result, "config.dataId", self.data_id, dict)
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
        glom.assign(result, "config.visConfig.opacity", self.opacity, dict)
        glom.assign(
            result,
            "config.visConfig.colorRange",
            self.color_range.to_json() if self.color_range else None,
            dict,
        )
        glom.assign(result, "config.visConfig.sizeScale", self.size_scale, dict)
        glom.assign(result, "config.visConfig.angleX", self.angle_x, dict)
        glom.assign(result, "config.visConfig.angleY", self.angle_y, dict)
        glom.assign(result, "config.visConfig.angleZ", self.angle_z, dict)
        glom.assign(result, "config.visConfig.scenegraph", self.model_3d, dict)
        glom.assign(
            result,
            "config.visConfig.scenegraphCustomModelUrl",
            self.model_3d_custom_url,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.scenegraphColorEnabled",
            self.model_3d_color_enabled,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.scenegraphColor",
            self.model_3d_color.to_json() if self.model_3d_color else None,
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
    def from_json(json: dict):
        assert json["type"] == "3D", "Layer 'type' is not '3D'"
        obj = ThreeDLayer(
            data_id=glom.glom(json, "config.dataId"),
            columns=ThreeDLayerColumns.from_json(glom.glom(json, "config.columns")),
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
        obj.size_scale = glom.glom(json, "config.visConfig.sizeScale", default=None)
        obj.angle_x = glom.glom(json, "config.visConfig.angleX", default=None)
        obj.angle_y = glom.glom(json, "config.visConfig.angleY", default=None)
        obj.angle_z = glom.glom(json, "config.visConfig.angleZ", default=None)
        obj.model_3d = glom.glom(json, "config.visConfig.scenegraph", default=None)
        obj.model_3d_custom_url = glom.glom(
            json, "config.visConfig.scenegraphCustomModelUrl", default=None
        )
        obj.model_3d_color_enabled = glom.glom(
            json, "config.visConfig.scenegraphColorEnabled", default=None
        )
        __model_3d_color = glom.glom(
            json, "config.visConfig.scenegraphColor", default=None
        )
        obj.model_3d_color = (
            Color.from_json(__model_3d_color) if __model_3d_color else None
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
        obj.size_column = glom.glom(json, "visualChannels.sizeField.name", default=None)
        obj.size_column_type = glom.glom(
            json, "visualChannels.sizeField.type", default=None
        )
        obj.size_column_scale = glom.glom(
            json, "visualChannels.sizeScale", default=None
        )
        return obj

    def clone(self) -> "ThreeDLayer":
        return replace(self)
