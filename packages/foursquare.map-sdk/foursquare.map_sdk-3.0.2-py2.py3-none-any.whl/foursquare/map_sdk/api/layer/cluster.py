from dataclasses import dataclass, field, replace
from typing import List, Literal, Optional

import glom

from foursquare.map_sdk.api.base import generate_uuid, remove_none_values
from foursquare.map_sdk.api.color import Color, ColorRange
from foursquare.map_sdk.api.columns import LatLngColumns


class ClusterLayerColumns(LatLngColumns):
    ...


@dataclass
class ClusterLayer:
    """
    The Cluster Layer visualizes aggregated data based on a geospatial radius. This layer is particularly useful for gathering insight from an area, grouping nearby points into a single entity.

    Required:
      data_id: str - Dataset ID
      columns: ClusterLayerColumns - Mapping between data columns and layer properties

    Optional:
      id: str - Layer ID (use a string without space)
      label: str - The displayed layer label
      color: Color - Layer color
      is_visible: bool - Layer visibility on the map
      hidden: bool - Hide layer from the layer panel. This will prevent user from editing the layer
      include_legend: bool - Control of the layer is included in the legend
      opacity: float - Opacity of the layer
      cluster_radius: float - Radius that a cluster will cover
      color_range: ColorRange - Mapping configuration between color and values
      radius_range: List[float] - A range of values that radius can take
      color_aggregation: Literal["count", "average", "maximum", "minimum", "median", "stdev", "sum", "variance", "mode", "countUnique"] - The aggregation mode for color
      color_column: str - Name of the data column with color data
      color_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional color column type override
      color_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for color values
    """

    data_id: str
    columns: ClusterLayerColumns

    id: Optional[str] = field(default_factory=generate_uuid)
    label: Optional[str] = None
    color: Optional[Color] = None
    is_visible: Optional[bool] = None
    hidden: Optional[bool] = None
    include_legend: Optional[bool] = None
    opacity: Optional[float] = None
    cluster_radius: Optional[float] = None
    color_range: Optional[ColorRange] = None
    radius_range: Optional[List[float]] = None
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
    color_column: Optional[str] = None
    color_column_type: Optional[
        Literal["string", "real", "timestamp", "integer", "boolean", "date"]
    ] = None
    color_column_scale: Optional[
        Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"]
    ] = None

    def to_json(self) -> dict:
        result: dict = {}
        glom.assign(result, "type", "cluster")
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
        glom.assign(result, "config.visConfig.clusterRadius", self.cluster_radius, dict)
        glom.assign(
            result,
            "config.visConfig.colorRange",
            self.color_range.to_json() if self.color_range else None,
            dict,
        )
        glom.assign(result, "config.visConfig.radiusRange", self.radius_range, dict)
        glom.assign(
            result, "config.visConfig.colorAggregation", self.color_aggregation, dict
        )
        glom.assign(result, "visualChannels.colorField.name", self.color_column, dict)
        glom.assign(
            result, "visualChannels.colorField.type", self.color_column_type, dict
        )
        glom.assign(result, "visualChannels.colorScale", self.color_column_scale, dict)
        return remove_none_values(result)

    @staticmethod
    def from_json(json: dict) -> "ClusterLayer":
        assert json["type"] == "cluster", "Layer 'type' is not 'cluster'"
        obj = ClusterLayer(
            data_id=glom.glom(json, "config.dataId"),
            columns=ClusterLayerColumns(
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
        obj.cluster_radius = glom.glom(
            json, "config.visConfig.clusterRadius", default=None
        )
        __color_range = glom.glom(json, "config.visConfig.colorRange", default=None)
        obj.color_range = ColorRange.from_json(__color_range) if __color_range else None
        obj.radius_range = glom.glom(json, "config.visConfig.radiusRange", default=None)
        obj.color_aggregation = glom.glom(
            json, "config.visConfig.colorAggregation", default=None
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
        return obj

    def clone(self) -> "ClusterLayer":
        return replace(self)
