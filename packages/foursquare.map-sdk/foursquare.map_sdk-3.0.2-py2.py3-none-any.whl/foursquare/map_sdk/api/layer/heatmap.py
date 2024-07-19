from dataclasses import dataclass, field, replace
from typing import Literal, Optional

import glom

from foursquare.map_sdk.api.base import generate_uuid, remove_none_values
from foursquare.map_sdk.api.color import Color, ColorRange
from foursquare.map_sdk.api.columns import LatLngColumns


class HeatmapLayerColumns(LatLngColumns):
    ...


@dataclass
class HeatmapLayer:
    """
    Heatmap layers describe the intensity of data at geographical points through a colored overlap. The intensity can be weighted by a numerical field.

    Required:
      data_id: str - Dataset ID
      columns: HeatmapLayerColumns - Mapping between data columns and layer properties

    Optional:
      id: str - Layer ID (use a string without space)
      label: str - The displayed layer label
      color: Color - Layer color
      is_visible: bool - Layer visibility on the map
      hidden: bool - Hide layer from the layer panel. This will prevent user from editing the layer
      include_legend: bool - Control of the layer is included in the legend
      opacity: float - Opacity of the layer
      intensity: float - Value that is multiplied with the total weight at a pixel to obtain the final weight (A value larger than 1 biases the output color towards the higher end of the spectrum, and a value less than 1 biases the output color towards the lower end of the spectrum.)
      threshold: float - A larger threshold smoothens the boundaries of color blobs, while making pixels with low weight harder to spot.
      color_range: ColorRange - Mapping configuration between color and values
      radius: float - Radius of points
      weight_column: str - Name of the data column with weight data
      weight_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional weight column type override
      weight_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for weight values
    """

    data_id: str
    columns: HeatmapLayerColumns

    id: Optional[str] = field(default_factory=generate_uuid)
    label: Optional[str] = None
    color: Optional[Color] = None
    is_visible: Optional[bool] = None
    hidden: Optional[bool] = None
    include_legend: Optional[bool] = None
    opacity: Optional[float] = None
    intensity: Optional[float] = None
    threshold: Optional[float] = None
    color_range: Optional[ColorRange] = None
    radius: Optional[float] = None
    weight_column: Optional[str] = None
    weight_column_type: Optional[
        Literal["string", "real", "timestamp", "integer", "boolean", "date"]
    ] = None
    weight_column_scale: Optional[
        Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"]
    ] = None

    def to_json(self) -> dict:
        result: dict = {}
        glom.assign(result, "type", "heatmap")
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
        glom.assign(result, "config.visConfig.intensity", self.intensity, dict)
        glom.assign(result, "config.visConfig.threshold", self.threshold, dict)
        glom.assign(
            result,
            "config.visConfig.colorRange",
            self.color_range.to_json() if self.color_range else None,
            dict,
        )
        glom.assign(result, "config.visConfig.radius", self.radius, dict)
        glom.assign(result, "visualChannels.weightField.name", self.weight_column, dict)
        glom.assign(
            result, "visualChannels.weightField.type", self.weight_column_type, dict
        )
        glom.assign(
            result, "visualChannels.weightScale", self.weight_column_scale, dict
        )
        return remove_none_values(result)

    @staticmethod
    def from_json(json: dict) -> "HeatmapLayer":
        assert json["type"] == "heatmap", "Layer 'type' is not 'heatmap'"
        obj = HeatmapLayer(
            data_id=glom.glom(json, "config.dataId"),
            columns=HeatmapLayerColumns(
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
        obj.intensity = glom.glom(json, "config.visConfig.intensity", default=None)
        obj.threshold = glom.glom(json, "config.visConfig.threshold", default=None)
        __color_range = glom.glom(json, "config.visConfig.colorRange", default=None)
        obj.color_range = ColorRange.from_json(__color_range) if __color_range else None
        obj.radius = glom.glom(json, "config.visConfig.radius", default=None)
        obj.weight_column = glom.glom(
            json, "visualChannels.weightField.name", default=None
        )
        obj.weight_column_type = glom.glom(
            json, "visualChannels.weightField.type", default=None
        )
        obj.weight_column_scale = glom.glom(
            json, "visualChannels.weightScale", default=None
        )
        return obj

    def clone(self) -> "HeatmapLayer":
        return replace(self)
