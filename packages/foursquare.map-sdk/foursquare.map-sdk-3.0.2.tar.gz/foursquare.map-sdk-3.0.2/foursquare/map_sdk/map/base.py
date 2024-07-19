from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from foursquare.map_sdk.api.annotation_api import (
    AnnotationApiInteractiveMixin,
    AnnotationApiNonInteractiveMixin,
)
from foursquare.map_sdk.api.base import CamelCaseBaseModel
from foursquare.map_sdk.api.dataset_api import (
    DatasetApiInteractiveMixin,
    DatasetApiNonInteractiveMixin,
)
from foursquare.map_sdk.api.effect_api import (
    EffectApiInteractiveMixin,
    EffectApiNonInteractiveMixin,
)
from foursquare.map_sdk.api.event_api import EventApiInteractiveMixin
from foursquare.map_sdk.api.filter_api import (
    FilterApiInteractiveMixin,
    FilterApiNonInteractiveMixin,
)
from foursquare.map_sdk.api.layer_api import (
    LayerApiInteractiveMixin,
    LayerApiNonInteractiveMixin,
)
from foursquare.map_sdk.api.map_api import (
    MapApiInteractiveMixin,
    MapApiNonInteractiveMixin,
    MapStyleCreationProps,
)
from foursquare.map_sdk.environment import default_height
from foursquare.map_sdk.transport.base import (
    BaseInteractiveTransport,
    BaseNonInteractiveTransport,
    BaseTransport,
)


class MapInitialState(CamelCaseBaseModel):
    published_map_id: str


class BasemapParams(CamelCaseBaseModel):
    custom_map_styles: Optional[List[MapStyleCreationProps]] = None
    initial_map_style_id: Optional[str] = None
    mapbox_access_token: Optional[str] = None


class URLParams(CamelCaseBaseModel):
    static_asset_url_base: Optional[str] = None
    application_url_base: Optional[str] = None


# This doesn't subclass from CamelCaseBaseModel because we don't want to mangle key
# names
class MapStyle(BaseModel):
    height: Union[str, float, int] = Field(default_factory=default_height)
    width: Union[str, float, int] = "100%"
    model_config = ConfigDict(extra="allow")


class BaseMap:
    """
    Base class for all map types (both widget and non-widget)
    """

    transport: BaseTransport


class BaseInteractiveMap(
    BaseMap,
    MapApiInteractiveMixin,
    DatasetApiInteractiveMixin,
    FilterApiInteractiveMixin,
    LayerApiInteractiveMixin,
    EventApiInteractiveMixin,
    EffectApiInteractiveMixin,
    AnnotationApiInteractiveMixin,
):
    transport: BaseInteractiveTransport
    pass


class BaseNonInteractiveMap(
    BaseMap,
    MapApiNonInteractiveMixin,
    DatasetApiNonInteractiveMixin,
    FilterApiNonInteractiveMixin,
    LayerApiNonInteractiveMixin,
    EffectApiNonInteractiveMixin,
    AnnotationApiNonInteractiveMixin,
):
    transport: BaseNonInteractiveTransport
    pass
