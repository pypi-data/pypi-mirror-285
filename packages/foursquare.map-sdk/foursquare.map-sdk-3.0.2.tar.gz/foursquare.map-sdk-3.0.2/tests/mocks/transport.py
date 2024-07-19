from typing import Callable, Dict, List, Optional, Sequence, Type, Union

from foursquare.map_sdk.api.base import Action
from foursquare.map_sdk.api.enums import EventType
from foursquare.map_sdk.transport.base import BaseInteractiveTransport
from foursquare.map_sdk.types import (
    ErrorResponse,
    EventResponse,
    MessageResponse,
    ResponseClass,
)


class MockInteractiveTransport(BaseInteractiveTransport):
    def send_action(
        self, *, action: Action, response_class: Optional[Type[ResponseClass]] = None
    ) -> Optional[ResponseClass]:
        pass

    def send_action_non_null(
        self,
        *,
        action: Action,
        response_class: Optional[Type[ResponseClass]] = None,
    ) -> ResponseClass:
        pass

    def receive_message(
        self,
        content: Union[EventResponse, MessageResponse, ErrorResponse],
        buffers: List[bytes],
    ) -> None:
        pass

    def set_event_handlers(self, event_handlers: Dict[str, Callable]) -> None:
        pass

    def remove_event_handlers(self, names: Sequence[Union[str, EventType]]) -> None:
        pass
