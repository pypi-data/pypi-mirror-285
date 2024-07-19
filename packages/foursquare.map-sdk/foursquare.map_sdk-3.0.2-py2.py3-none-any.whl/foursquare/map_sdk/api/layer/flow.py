from dataclasses import dataclass, field, replace
from typing import Optional, Union

import glom

from foursquare.map_sdk.api.base import generate_uuid, remove_none_values
from foursquare.map_sdk.api.color import Color, ColorRange
from foursquare.map_sdk.api.columns import H3CntPairColumns, LatLngCntPairColumns


class FlowLayerH3Columns(H3CntPairColumns):
    ...


class FlowLayerLatLngColumns(LatLngCntPairColumns):
    ...


@dataclass
class FlowLayer:
    """
    The Flow Layer is an effective way of visualizing origin-destination movement patterns. Flows are a great choice for analyzing traffic flows, commute patterns, and migrations.

    Required:
      data_id: str - Dataset ID
      columns: Union[FlowLayerLatLngColumns, FlowLayerH3Columns] - Mapping between data columns and layer properties

    Optional:
      id: str - Layer ID (use a string without space)
      label: str - The displayed layer label
      color: Color - Layer color
      is_visible: bool - Layer visibility on the map
      hidden: bool - Hide layer from the layer panel. This will prevent user from editing the layer
      include_legend: bool - Control of the layer is included in the legend
      color_range: ColorRange - Mapping configuration between color and values
      opacity: float - Opacity of the layer
      flow_animation_enabled: bool - Is flow animation enabled
      flow_adaptive_scales_enabled: bool - Is flow adaptive scales enabled
      flow_fade_enabled: bool - Enable fade effect
      flow_fade_amount: float - Flow fade amount
      max_top_flows_display_num: float - Maximum top flow value
      flow_location_totals_enabled: bool - Are flow totals enabled
      flow_clustering_enabled: bool - Enable clustering
      dark_base_map_enabled: bool - Is dark base map enabled
    """

    data_id: str
    columns: Union[FlowLayerLatLngColumns, FlowLayerH3Columns]

    id: Optional[str] = field(default_factory=generate_uuid)
    label: Optional[str] = None
    color: Optional[Color] = None
    is_visible: Optional[bool] = None
    hidden: Optional[bool] = None
    include_legend: Optional[bool] = None
    color_range: Optional[ColorRange] = None
    opacity: Optional[float] = None
    flow_animation_enabled: Optional[bool] = None
    flow_adaptive_scales_enabled: Optional[bool] = None
    flow_fade_enabled: Optional[bool] = None
    flow_fade_amount: Optional[float] = None
    max_top_flows_display_num: Optional[float] = None
    flow_location_totals_enabled: Optional[bool] = None
    flow_clustering_enabled: Optional[bool] = None
    dark_base_map_enabled: Optional[bool] = None

    def to_json(self) -> dict:
        result: dict = {}
        glom.assign(result, "type", "flow")
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
            "config.visConfig.colorRange",
            self.color_range.to_json() if self.color_range else None,
            dict,
        )
        glom.assign(result, "config.visConfig.opacity", self.opacity, dict)
        glom.assign(
            result,
            "config.visConfig.flowAnimationEnabled",
            self.flow_animation_enabled,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.flowAdaptiveScalesEnabled",
            self.flow_adaptive_scales_enabled,
            dict,
        )
        glom.assign(
            result, "config.visConfig.flowFadeEnabled", self.flow_fade_enabled, dict
        )
        glom.assign(
            result, "config.visConfig.flowFadeAmount", self.flow_fade_amount, dict
        )
        glom.assign(
            result,
            "config.visConfig.maxTopFlowsDisplayNum",
            self.max_top_flows_display_num,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.flowLocationTotalsEnabled",
            self.flow_location_totals_enabled,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.flowClusteringEnabled",
            self.flow_clustering_enabled,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.darkBaseMapEnabled",
            self.dark_base_map_enabled,
            dict,
        )
        return remove_none_values(result)

    @staticmethod
    def from_json(json: dict) -> "FlowLayer":
        assert json["type"] == "flow", "Layer 'type' is not 'flow'"
        obj = FlowLayer(
            data_id=glom.glom(json, "config.dataId"),
            columns={
                # pylint: disable-next=unnecessary-lambda
                FlowLayerLatLngColumns.mode: lambda columns: FlowLayerLatLngColumns.from_json(
                    columns
                ),
                # pylint: disable-next=unnecessary-lambda
                FlowLayerH3Columns.mode: lambda columns: FlowLayerH3Columns.from_json(
                    columns
                ),
            }[glom.glom(json, "config.columnMode", default=LatLngCntPairColumns.mode)](
                glom.glom(json, "config.columns")
            ),
        )
        obj.id = glom.glom(json, "id", default=None)
        obj.label = glom.glom(json, "config.label", default=None)
        __color = glom.glom(json, "config.color", default=None)
        obj.color = Color.from_json(__color) if __color else None
        obj.is_visible = glom.glom(json, "config.isVisible", default=None)
        obj.hidden = glom.glom(json, "config.hidden", default=None)
        obj.include_legend = glom.glom(json, "config.legend.isIncluded", default=None)
        __color_range = glom.glom(json, "config.visConfig.colorRange", default=None)
        obj.color_range = ColorRange.from_json(__color_range) if __color_range else None
        obj.opacity = glom.glom(json, "config.visConfig.opacity", default=None)
        obj.flow_animation_enabled = glom.glom(
            json, "config.visConfig.flowAnimationEnabled", default=None
        )
        obj.flow_adaptive_scales_enabled = glom.glom(
            json, "config.visConfig.flowAdaptiveScalesEnabled", default=None
        )
        obj.flow_fade_enabled = glom.glom(
            json, "config.visConfig.flowFadeEnabled", default=None
        )
        obj.flow_fade_amount = glom.glom(
            json, "config.visConfig.flowFadeAmount", default=None
        )
        obj.max_top_flows_display_num = glom.glom(
            json, "config.visConfig.maxTopFlowsDisplayNum", default=None
        )
        obj.flow_location_totals_enabled = glom.glom(
            json, "config.visConfig.flowLocationTotalsEnabled", default=None
        )
        obj.flow_clustering_enabled = glom.glom(
            json, "config.visConfig.flowClusteringEnabled", default=None
        )
        obj.dark_base_map_enabled = glom.glom(
            json, "config.visConfig.darkBaseMapEnabled", default=None
        )
        return obj

    def clone(self) -> "FlowLayer":
        return replace(self)
