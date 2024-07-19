from typing import Dict, List, Optional, Union, cast

from pydantic import StrictBool, StrictStr

from foursquare.map_sdk.api.base import Action, CamelCaseBaseModel, Number
from foursquare.map_sdk.api.enums import ActionType, EffectType
from foursquare.map_sdk.transport.base import (
    BaseInteractiveTransport,
    BaseNonInteractiveTransport,
    BaseTransport,
)


class EffectUpdateProps(CamelCaseBaseModel):
    is_enabled: Optional[StrictBool] = None
    """Flag indicating whether effect is enabled or not."""

    parameters: Optional[
        Dict[StrictStr, Union[Number, List[Number], StrictBool, StrictStr]]
    ] = None
    """Dictionary that maps fields that the effect uses."""


class EffectCreationProps(EffectUpdateProps):
    id: Optional[StrictStr] = None
    """Unique identifier of the effect."""

    type: Optional[EffectType] = None
    """Type of the effect."""

    is_enabled: Optional[StrictBool] = None
    """Flag indicating whether effect is enabled or not."""

    parameters: Optional[
        Dict[StrictStr, Union[Number, List[Number], StrictBool, StrictStr]]
    ] = None
    """Dictionary that maps fields that the effect uses."""


class Effect(EffectCreationProps):
    """Type encapsulating effect properties."""

    id: StrictStr
    """Unique identifier of the effect."""

    type: EffectType
    """Type of the effect."""

    is_enabled: StrictBool
    """Flag indicating whether effect is enabled or not."""

    parameters: Dict[StrictStr, Union[Number, List[Number], StrictBool, StrictStr]]
    """Dictionary that maps fields that the effect uses."""


###########
# ACTIONS #
###########


class GetEffectsAction(Action):
    type: ActionType = ActionType.GET_EFFECTS


class GetEffectByIdAction(Action):
    class Meta(Action.Meta):
        args = ["effect_id"]

    type: ActionType = ActionType.GET_EFFECT_BY_ID
    effect_id: StrictStr


class AddEffectAction(Action):
    class Meta(Action.Meta):
        args = ["effect"]

    type: ActionType = ActionType.ADD_EFFECT
    effect: EffectCreationProps


class UpdateEffectAction(Action):
    class Meta(Action.Meta):
        args = ["effect_id", "values"]

    type: ActionType = ActionType.UPDATE_EFFECT
    effect_id: StrictStr
    values: EffectUpdateProps


class RemoveEffectAction(Action):
    class Meta(Action.Meta):
        args = ["effect_id"]

    type: ActionType = ActionType.REMOVE_EFFECT
    effect_id: StrictStr


###########
# METHODS #
###########


class BaseEffectApiMethods:
    transport: BaseTransport

    def add_effect(self, effect: Union[EffectCreationProps, dict]) -> Optional[Effect]:
        """Adds a new effect to the map.

        Args:
            effect (Union[EffectCreationProps, dict): The effect to add.

        Returns (widget map only):
            Effect: The effect that was added.
        """
        action = AddEffectAction(effect=effect)
        return self.transport.send_action_non_null(action=action, response_class=Effect)

    def update_effect(
        self,
        effect_id: str,
        values: Union[EffectUpdateProps, dict],
    ) -> Optional[Effect]:
        """Updates an existing effect with given values.

        Args:
            effect_id (str): The id of the effect to update.
            values (Union[EffectUpdateProps, dict]): The values to update.

        Returns (widget map only)
            Effect: The updated effect.
        """
        action = UpdateEffectAction(effect_id=effect_id, values=values)
        return self.transport.send_action_non_null(action=action, response_class=Effect)

    def remove_effect(self, effect_id: str) -> None:
        """Removes a effect from the map.

        Args:
            effect_id (str): The id of the effect to remove

        Returns:
            None
        """
        action = RemoveEffectAction(effect_id=effect_id)
        self.transport.send_action(action=action, response_class=None)


class BaseInteractiveEffectApiMethods:
    transport: BaseInteractiveTransport

    def get_effects(self) -> List[Effect]:
        """Gets all the effects currently available in the map.

        Returns:
            List[Effect]: An array of effects.
        """
        action = GetEffectsAction()
        return self.transport.send_action_non_null(
            action=action, response_class=List[Effect]
        )

    def get_effect_by_id(self, effect_id: str) -> Optional[Effect]:
        """Retrieves a effect by its identifier if it exists.

        Args:
            effect_id (str): Identifier of the effect to get.

        Returns:
            Optional[Effect]: Effect with a given identifier, or None if one doesn't exist.
        """
        action = GetEffectByIdAction(effect_id=effect_id)
        return self.transport.send_action(action=action, response_class=Effect)


class EffectApiNonInteractiveMixin(BaseEffectApiMethods):
    """Effect methods that are supported in non-interactive (i.e. pure HTML) maps"""

    transport: BaseNonInteractiveTransport

    def add_effect(self, effect: Union[EffectCreationProps, dict]) -> None:
        super().add_effect(effect=effect)
        return

    def update_effect(
        self, effect_id: str, values: Union[EffectUpdateProps, dict]
    ) -> None:
        super().update_effect(effect_id=effect_id, values=values)
        return


class EffectApiInteractiveMixin(BaseEffectApiMethods, BaseInteractiveEffectApiMethods):
    """Effect methods that are supported in interactive (i.e. widget) maps"""

    transport: BaseInteractiveTransport

    def add_effect(self, effect: Union[EffectCreationProps, dict]) -> Effect:
        return cast(Effect, super().add_effect(effect=effect))

    def update_effect(
        self, effect_id: str, values: Union[EffectUpdateProps, dict]
    ) -> Effect:
        return cast(Effect, super().update_effect(effect_id=effect_id, values=values))
