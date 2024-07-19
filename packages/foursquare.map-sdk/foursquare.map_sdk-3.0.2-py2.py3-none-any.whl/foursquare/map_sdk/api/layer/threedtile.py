from dataclasses import dataclass, field, replace
from typing import Optional

import glom

from foursquare.map_sdk.api.base import generate_uuid, remove_none_values
from foursquare.map_sdk.api.color import Color


@dataclass
class ThreeDTileLayer:
    """
    The ThreeDTile Layer can be used for rendering of massive 3D datasets in the 3D Tiles format, e.g. providing photorealistic renderings of hundreds of cities across the globe via Google Map Tiles. These massive 3D datasets are optimized for streaming, analytics, and time-dynamic simulations.

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
    """

    data_id: str

    id: Optional[str] = field(default_factory=generate_uuid)
    label: Optional[str] = None
    color: Optional[Color] = None
    is_visible: Optional[bool] = None
    hidden: Optional[bool] = None
    include_legend: Optional[bool] = None
    opacity: Optional[float] = None

    def to_json(self) -> dict:
        result: dict = {}
        glom.assign(result, "type", "tile3d")
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
        return remove_none_values(result)

    @staticmethod
    def from_json(json: dict) -> "ThreeDTileLayer":
        assert json["type"] == "tile3d", "Layer 'type' is not 'tile3d'"
        obj = ThreeDTileLayer(data_id=glom.glom(json, "config.dataId"))
        obj.id = glom.glom(json, "id", default=None)
        obj.label = glom.glom(json, "config.label", default=None)
        __color = glom.glom(json, "config.color", default=None)
        obj.color = Color.from_json(__color) if __color else None
        obj.is_visible = glom.glom(json, "config.isVisible", default=None)
        obj.hidden = glom.glom(json, "config.hidden", default=None)
        obj.include_legend = glom.glom(json, "config.legend.isIncluded", default=None)
        obj.opacity = glom.glom(json, "config.visConfig.opacity", default=None)
        return obj

    def clone(self) -> "ThreeDTileLayer":
        return replace(self)
