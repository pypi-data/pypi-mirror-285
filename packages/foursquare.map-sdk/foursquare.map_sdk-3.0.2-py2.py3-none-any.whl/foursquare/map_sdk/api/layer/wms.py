from dataclasses import dataclass, field, replace
from typing import List, Optional

import glom

from foursquare.map_sdk.api.base import generate_uuid, remove_none_values
from foursquare.map_sdk.api.color import Color


@dataclass
class WMSLayer:
    """
    The WMS Layer lets you connect to a Web Map Services (WMS) to render map images optimized for the current view. Instead of downloading a detailed map of the entire globe, an image is rendered covering the current viewport.

    Required:
      data_id: str - Dataset ID

    Optional:
      id: str - Layer ID (use a string without space)
      label: str - The displayed layer label
      color: Color - Layer color
      is_visible: bool - Layer visibility on the map
      hidden: bool - Hide layer from the layer panel. This will prevent user from editing the layer
      include_legend: bool - Control of the layer is included in the legend
      opacity: float - Opacity of the layer
      service_layers: List[str] - Percentile range
    """

    data_id: str

    id: Optional[str] = field(default_factory=generate_uuid)
    label: Optional[str] = None
    color: Optional[Color] = None
    is_visible: Optional[bool] = None
    hidden: Optional[bool] = None
    include_legend: Optional[bool] = None
    opacity: Optional[float] = None
    service_layers: Optional[List[str]] = None

    def to_json(self) -> dict:
        result: dict = {}
        glom.assign(result, "type", "WMS")
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
        glom.assign(result, "config.visConfig.opacity", self.opacity, dict)
        glom.assign(result, "config.visConfig.serviceLayers", self.service_layers, dict)
        return remove_none_values(result)

    @staticmethod
    def from_json(json: dict) -> "WMSLayer":
        assert json["type"] == "WMS", "Layer 'type' is not 'WMS'"
        obj = WMSLayer(data_id=glom.glom(json, "config.dataId"))
        obj.id = glom.glom(json, "id", default=None)
        obj.label = glom.glom(json, "config.label", default=None)
        __color = glom.glom(json, "config.color", default=None)
        obj.color = Color.from_json(__color) if __color else None
        obj.is_visible = glom.glom(json, "config.isVisible", default=None)
        obj.hidden = glom.glom(json, "config.hidden", default=None)
        obj.include_legend = glom.glom(json, "config.legend.isIncluded", default=None)
        obj.opacity = glom.glom(json, "config.visConfig.opacity", default=None)
        obj.service_layers = glom.glom(
            json, "config.visConfig.serviceLayers", default=None
        )
        return obj

    def clone(self) -> "WMSLayer":
        return replace(self)
