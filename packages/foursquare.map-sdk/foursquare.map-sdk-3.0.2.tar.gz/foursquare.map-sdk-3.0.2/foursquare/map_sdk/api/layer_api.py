import json
from typing import Any, Callable, Dict, List, Literal, Optional, Union, cast

from pydantic import StrictBool, StrictStr

from foursquare.map_sdk.api.base import Action, CamelCaseBaseModel, Number, TimeRange
from foursquare.map_sdk.api.enums import ActionType, LayerType
from foursquare.map_sdk.generated.Layer import Layer as FullLayerConfig  # type: ignore
from foursquare.map_sdk.transport.base import (
    BaseInteractiveTransport,
    BaseNonInteractiveTransport,
    BaseTransport,
)


class VisualChannel(CamelCaseBaseModel):
    name: StrictStr
    type: StrictStr


VisualChannels = Dict[StrictStr, Union[VisualChannel, StrictStr, None]]


class _PartialLayerConfig(CamelCaseBaseModel):
    visual_channels: Optional[VisualChannels] = None
    """Dictionary of visualization properties that the layer supports."""

    vis_config: Optional[Dict[StrictStr, Any]] = None
    """General layer settings."""

    column_mode: Optional[
        Literal["points", "geojson", "table", "neighbors", "LAT_LNG", "H3"]
    ] = None
    """Column mode for the layer (some of the layers support multiple input data formats)."""

    text_label: Optional[List[Dict[StrictStr, Any]]] = None
    """Label settings."""


class LayerConfig(_PartialLayerConfig):
    visual_channels: VisualChannels
    """Dictionary of visualization properties that the layer supports."""

    vis_config: Dict[StrictStr, Any]
    """General layer settings."""

    column_mode: Optional[
        Literal["points", "geojson", "table", "neighbors", "LAT_LNG", "H3"]
    ] = None
    """Column mode for the layer (some of the layers support multiple input data formats)."""

    text_label: Optional[List[Dict[StrictStr, Any]]] = None
    """Label settings."""


class LayerUpdateProps(CamelCaseBaseModel):
    type: Optional[LayerType] = None
    """Type of the layer."""

    data_id: Optional[StrictStr] = None
    """Unique identifier of the dataset this layer visualizes."""

    fields: Optional[Dict[StrictStr, Optional[StrictStr]]] = None
    """Dictionary that maps fields that the layer requires for visualization to appropriate dataset fields."""

    label: Optional[StrictStr] = None
    """Canonical label of this layer."""

    is_visible: Optional[StrictBool] = None
    """Flag indicating whether layer is visible or not."""

    config: Optional[_PartialLayerConfig] = None
    """Layer configuration specific to its type."""


class LayerCreationProps(LayerUpdateProps):
    id: Optional[StrictStr] = None
    """Unique identifier of the layer."""

    type: Optional[LayerType] = None
    """Type of the layer."""

    data_id: StrictStr
    """Unique identifier of the dataset this layer visualizes."""

    fields: Optional[Dict[StrictStr, Optional[StrictStr]]] = None
    """Dictionary that maps fields that the layer requires for visualization to appropriate dataset fields."""

    label: Optional[StrictStr] = None
    """Canonical label of this layer."""

    is_visible: Optional[StrictBool] = None
    """Flag indicating whether layer is visible or not."""

    config: Optional[_PartialLayerConfig] = None
    """Layer configuration specific to its type."""


class Layer(LayerCreationProps):
    """Type encapsulating layer properties."""

    id: StrictStr
    """Unique identifier of the layer."""

    type: Optional[LayerType] = None
    """Type of the layer."""

    data_id: StrictStr
    """Unique identifier of the dataset this layer visualizes."""

    fields: Dict[StrictStr, Optional[StrictStr]]
    """Dictionary that maps fields that the layer requires for visualization to appropriate dataset fields."""

    label: StrictStr
    """Canonical label of this layer."""

    is_visible: StrictBool
    """Flag indicating whether layer is visible or not."""

    config: LayerConfig
    """Layer configuration specific to its type."""


class LayerGroupUpdateProps(CamelCaseBaseModel):
    label: Optional[StrictStr] = None
    """Canonical label of this layer group."""

    is_visible: Optional[StrictBool] = None
    """Flag indicating whether layer group is visible or not."""

    layer_ids: Optional[List[StrictStr]] = None
    """Layers that are part of this group, sorted in the order in which they are shown."""


class LayerGroupCreationProps(LayerGroupUpdateProps):
    id: Optional[StrictStr] = None
    """Unique identifier of the layer group."""

    label: Optional[StrictStr] = None
    """Canonical label of this layer group."""

    is_visible: Optional[StrictBool] = None
    """Flag indicating whether layer group is visible or not."""

    layer_ids: Optional[List[StrictStr]] = None
    """Layers that are part of this group, sorted in the order in which they are shown."""


class LayerGroup(CamelCaseBaseModel):
    """A conceptual group used to organize layers."""

    id: StrictStr
    """Unique identifier of the layer group."""

    label: StrictStr
    """Canonical label of this layer group."""

    is_visible: StrictBool
    """Flag indicating whether layer group is visible or not."""

    layer_ids: List[StrictStr]
    """Layers that are part of this group, sorted in the order in which they are shown."""


class LayerTimelineUpdateProps(CamelCaseBaseModel):
    current_time: Optional[Number] = None
    """Current time on the timeline in milliseconds."""

    is_animating: Optional[StrictBool] = None
    """Flag indicating whether the timeline is animating or not."""

    is_visible: Optional[StrictBool] = None
    """Flag indicating whether the timeline is visible or not."""

    animation_speed: Optional[Number] = None
    """Speed at which timeline is animating."""

    time_format: Optional[StrictStr] = None
    """Time format that the timeline is using in day.js supported format.

    https://day.js.org/docs/en/display/format
    """

    timezone: Optional[StrictStr] = None
    """Timezone that the timeline is using in tz format.

    https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    """


class LayerTimeline(LayerTimelineUpdateProps):
    current_time: Number
    """Current time on the timeline in milliseconds."""

    domain: TimeRange
    """Range of time that the timeline shows."""

    is_animating: StrictBool
    """Flag indicating whether the timeline is animating or not."""

    is_visible: StrictBool
    """Flag indicating whether the timeline is visible or not."""

    animation_speed: Number
    """Speed at which timeline is animating."""

    time_format: StrictStr
    """Time format that the timeline is using in day.js supported format.

    https://day.js.org/docs/en/display/format
    """

    timezone: Optional[StrictStr] = None
    """Timezone that the timeline is using in tz format.

    https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    """

    time_steps: Optional[List[Number]] = None
    """Step duration for all the animation keyframes in milliseconds."""


class LayerEventHandlers(CamelCaseBaseModel):
    on_layer_timeline_update: Optional[Callable[[LayerTimeline], None]] = None


###########
# ACTIONS #
###########


class GetLayersAction(Action):
    type: ActionType = ActionType.GET_LAYERS


class GetLayerByIdAction(Action):
    class Meta(Action.Meta):
        args = ["layer_id"]

    type: ActionType = ActionType.GET_LAYER_BY_ID
    layer_id: StrictStr


class AddLayerAction(Action):
    class Meta(Action.Meta):
        args = ["layer"]

    type: ActionType = ActionType.ADD_LAYER
    layer: LayerCreationProps


class AddLayerFromConfigAction(Action):
    class Meta(Action.Meta):
        args = ["layer_config"]

    type: ActionType = ActionType.ADD_LAYER_FROM_CONFIG
    layer_config: FullLayerConfig


class UpdateLayerAction(Action):
    class Meta(Action.Meta):
        args = ["layer_id", "values"]

    type: ActionType = ActionType.UPDATE_LAYER
    layer_id: StrictStr
    values: LayerUpdateProps


class RemoveLayerAction(Action):
    class Meta(Action.Meta):
        args = ["layer_id"]

    type: ActionType = ActionType.REMOVE_LAYER
    layer_id: StrictStr


class GetLayerGroupsAction(Action):
    type: ActionType = ActionType.GET_LAYER_GROUPS


class GetLayerGroupByIdAction(Action):
    class Meta(Action.Meta):
        args = ["layer_group_id"]

    type: ActionType = ActionType.GET_LAYER_GROUP_BY_ID
    layer_group_id: StrictStr


class AddLayerGroupAction(Action):
    class Meta(Action.Meta):
        args = ["layer_group"]

    type: ActionType = ActionType.ADD_LAYER_GROUP
    layer_group: LayerGroupCreationProps


class UpdateLayerGroupAction(Action):
    class Meta(Action.Meta):
        args = ["layer_group_id", "values"]

    type: ActionType = ActionType.UPDATE_LAYER_GROUP
    layer_group_id: StrictStr
    values: LayerGroupUpdateProps


class RemoveLayerGroupAction(Action):
    class Meta(Action.Meta):
        args = ["layer_group_id"]

    type: ActionType = ActionType.REMOVE_LAYER_GROUP
    layer_group_id: StrictStr


class GetLayerTimelineAction(Action):
    type: ActionType = ActionType.GET_LAYER_TIMELINE


class UpdateLayerTimelineAction(Action):
    class Meta(Action.Meta):
        args = ["values"]

    type: ActionType = ActionType.UPDATE_LAYER_TIMELINE
    values: LayerTimelineUpdateProps


###########
# METHODS #
###########


class BaseLayerApiMethods:
    transport: BaseTransport

    def add_layer(self, layer: Union[LayerCreationProps, dict]) -> Optional[Layer]:
        """Adds a new layer to the map.

        Args:
            layer (Union[LayerCreationProps, dict]): The layer to add.

        Returns (widget map only):
            Layer: The layer that was added.
        """
        action = AddLayerAction(layer=layer)
        return self.transport.send_action_non_null(action=action, response_class=Layer)

    def add_layer_from_config(
        self, layer_config: Union[FullLayerConfig, str]
    ) -> Optional[Layer]:
        """Adds a new layer to the map, specified by its config.

        Args:
            layer_config (Union[FullLayerConfig, str]): The config of the layer to add.

        Returns (widget map only):
            Layer: The layer that was added.
        """

        if isinstance(layer_config, str):
            layer_config = json.loads(layer_config)

        action = AddLayerFromConfigAction(layer_config=layer_config)
        return self.transport.send_action_non_null(action=action, response_class=Layer)

    def update_layer(
        self, layer_id: str, values: Union[LayerUpdateProps, dict]
    ) -> Optional[Layer]:
        """Updates an existing layer with given values.

        Args:
            layer_id (str): The id of the layer to update.
            values (Union[LayerUpdateProps, dict]): The values to update.

        Returns (widget map only)
            Layer: The updated layer.
        """
        action = UpdateLayerAction(layer_id=layer_id, values=values)
        return self.transport.send_action_non_null(action=action, response_class=Layer)

    def remove_layer(self, layer_id: str) -> None:
        """Removes a layer from the map.

        Args:
            layer_id (str): The id of the layer to remove

        Returns:
            None
        """
        action = RemoveLayerAction(layer_id=layer_id)
        self.transport.send_action(action=action, response_class=None)

    def add_layer_group(
        self, layer_group: Union[LayerGroupCreationProps, dict]
    ) -> Optional[LayerGroup]:
        """Adds a new layer group to the map.

        Args:
            layer_group (Union[LayerGroupCreationProps, dict]): The layer group to add.

        Returns (widget map only):
            LayerGroup: The layer group that was added.
        """
        action = AddLayerGroupAction(layer_group=layer_group)
        return self.transport.send_action_non_null(
            action=action, response_class=LayerGroup
        )

    def update_layer_group(
        self, layer_group_id: str, values: Union[LayerGroupUpdateProps, dict]
    ) -> Optional[LayerGroup]:
        """Updates an existing layer group with given values.

        Args:
            layer_group_id (str): The id of the layer group to update.
            values (Union[LayerGroupUpdateProps, dict]): The values to update.

        Returns (widget map only):
            LayerGroup: The updated layer group.
        """
        action = UpdateLayerGroupAction(
            layer_group_id=layer_group_id,
            values=values,
        )
        return self.transport.send_action_non_null(
            action=action, response_class=LayerGroup
        )

    def remove_layer_group(self, layer_group_id: str) -> None:
        """Removes a layer group from the map.

        Args:
            layer_group_id (str): The id of the layer group to remove

        Returns:
            None
        """
        action = RemoveLayerGroupAction(layer_group_id=layer_group_id)
        self.transport.send_action(action=action, response_class=None)

    def update_layer_timeline(
        self, values: Union[LayerTimelineUpdateProps, dict]
    ) -> Optional[LayerTimeline]:
        """Updates the current layer timeline configuration.

        Args:
            values (Union[LayerTimelineUpdateProps, dict]): The new layer timeline values.

        Returns (widget map only):
            LayerTimeline: The updated layer timeline.
        """
        action = UpdateLayerTimelineAction(values=values)
        return self.transport.send_action_non_null(
            action=action, response_class=LayerTimeline
        )


class BaseInteractiveLayerApiMethods:
    transport: BaseInteractiveTransport

    def get_layers(self) -> List[Layer]:
        """Gets all the layers currently available in the map.

        Returns:
            List[Layer]: An array of layers.
        """
        action = GetLayersAction()
        return self.transport.send_action_non_null(
            action=action, response_class=List[Layer]
        )

    def get_layer_by_id(self, layer_id: str) -> Optional[Layer]:
        """Retrieves a layer by its identifier if it exists.

        Args:
            layer_id (str): Identifier of the layer to get.

        Returns:
            Optional[Layer]: Layer with a given identifier, or None if one doesn't exist.
        """
        action = GetLayerByIdAction(layer_id=layer_id)
        return self.transport.send_action(action=action, response_class=Layer)

    def get_layer_groups(self) -> List[LayerGroup]:
        """Gets all the layer groups currently available in the map.

        Returns:
            List[LayerGroup]: An array of layer groups.
        """
        action = GetLayerGroupsAction()
        return self.transport.send_action_non_null(
            action=action, response_class=List[LayerGroup]
        )

    def get_layer_group_by_id(self, layer_group_id: str) -> Optional[LayerGroup]:
        """Retrieves a layer group by its identifier if it exists.

        Args:
            layer_group_id (str): Identifier of the layer group to get.

        Returns:
            Optional[LayerGroup]: Layer group with a given identifier, or None if one doesn't exist.
        """
        action = GetLayerGroupByIdAction(layer_group_id=layer_group_id)
        return self.transport.send_action(action=action, response_class=LayerGroup)

    def get_layer_timeline(self) -> Optional[LayerTimeline]:
        """Gets the current layer timeline configuration.

        Returns:
            Optional[LayerTimeline]: The layer timeline configuration, or None if one doesn't exist.
        """
        action = GetLayerTimelineAction()
        return self.transport.send_action(action=action, response_class=LayerTimeline)


class LayerApiNonInteractiveMixin(BaseLayerApiMethods):
    """Layer methods that are supported in non-interactive (i.e. pure HTML) maps"""

    transport: BaseNonInteractiveTransport

    def add_layer(self, layer: Union[LayerCreationProps, dict]) -> None:
        super().add_layer(layer=layer)
        return

    def add_layer_from_config(self, layer_config: Union[FullLayerConfig, str]) -> None:
        super().add_layer_from_config(layer_config=layer_config)
        return

    def update_layer(
        self,
        layer_id: str,
        values: Union[LayerUpdateProps, dict],
    ) -> None:
        super().update_layer(layer_id=layer_id, values=values)
        return

    def add_layer_group(
        self,
        layer_group: Union[LayerGroupCreationProps, dict],
    ) -> None:
        super().add_layer_group(layer_group=layer_group)
        return

    def update_layer_group(
        self,
        layer_group_id: str,
        values: Union[LayerGroupUpdateProps, dict],
    ) -> None:
        super().update_layer_group(layer_group_id=layer_group_id, values=values)
        return

    def update_layer_timeline(
        self, values: Union[LayerTimelineUpdateProps, dict]
    ) -> None:
        super().update_layer_timeline(values=values)
        return


class LayerApiInteractiveMixin(BaseLayerApiMethods, BaseInteractiveLayerApiMethods):
    """Layer methods that are supported in interactive (i.e. widget) maps"""

    transport: BaseInteractiveTransport

    def add_layer(self, layer: Union[LayerCreationProps, dict]) -> Layer:
        return cast(Layer, super().add_layer(layer=layer))

    def add_layer_from_config(self, layer_config: Union[FullLayerConfig, str]) -> Layer:
        return cast(Layer, super().add_layer_from_config(layer_config=layer_config))

    def update_layer(
        self, layer_id: str, values: Union[LayerUpdateProps, dict]
    ) -> Layer:
        return cast(Layer, super().update_layer(layer_id=layer_id, values=values))

    def add_layer_group(
        self, layer_group: Union[LayerGroupCreationProps, dict]
    ) -> LayerGroup:
        return cast(LayerGroup, super().add_layer_group(layer_group=layer_group))

    def update_layer_group(
        self,
        layer_group_id: str,
        values: Union[LayerGroupUpdateProps, dict],
    ) -> LayerGroup:
        return cast(
            LayerGroup,
            super().update_layer_group(layer_group_id=layer_group_id, values=values),
        )

    def update_layer_timeline(
        self, values: Union[LayerTimelineUpdateProps, dict]
    ) -> LayerTimeline:
        return cast(LayerTimeline, super().update_layer_timeline(values=values))
