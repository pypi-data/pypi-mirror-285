from typing import Dict, List, Optional

from ipywidgets import DOMWidget
from pydantic import AnyHttpUrl
from traitlets import Dict as TraitletsDict
from traitlets import Unicode

from foursquare.map_sdk._frontend import module_name, module_version
from foursquare.map_sdk._version import __version__
from foursquare.map_sdk.api.base import CamelCaseBaseModel
from foursquare.map_sdk.map.base import (
    BaseInteractiveMap,
    BasemapParams,
    MapInitialState,
    MapStyle,
    URLParams,
)
from foursquare.map_sdk.transport.widget import BlockingWidgetTransport


class RasterParams(CamelCaseBaseModel):
    server_urls: Optional[List[AnyHttpUrl]] = None
    stac_search_url: Optional[AnyHttpUrl] = None


class SyncWidgetMap(DOMWidget, BaseInteractiveMap):
    _model_name = Unicode("UnfoldedMapModel").tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode("UnfoldedMapView").tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    api_key = Unicode().tag(sync=True)
    initial_state = TraitletsDict().tag(sync=True)
    style = TraitletsDict().tag(sync=True)
    basemaps = TraitletsDict().tag(sync=True)
    raster = TraitletsDict().tag(sync=True)
    urls = TraitletsDict().tag(sync=True)
    _internal = TraitletsDict().tag(sync=True)

    # Note: We define an unused kwargs so that an error is not produced for invalid initialization
    # args between the widget and HTML implementations
    def __init__(
        self,
        *,
        api_key: str,
        initial_state: Optional[Dict] = None,
        style: Optional[Dict] = None,
        basemaps: Optional[Dict] = None,
        raster: Optional[Dict] = None,
        urls: Optional[Dict] = None,
        _internal: Optional[Dict] = None,
        **kwargs  # pylint: disable=unused-argument
    ):
        """Initializes a new widget map

        Kwargs:
            api_key: an API Key
            style: Optional map container CSS style customization. Uses camelCase as this is React standard.
            basemaps: Basemap customization settings.
            raster: Customization related to raster datasets and tiles.

        """
        super().__init__()

        self.api_key = api_key

        if initial_state:
            self.initial_state = MapInitialState(**initial_state).model_dump(
                mode="json", by_alias=True, exclude_none=True
            )

        if style:
            self.style = MapStyle(**style).model_dump(mode="json", exclude_none=True)
        else:
            self.style = MapStyle().model_dump(mode="json", exclude_none=True)

        if basemaps:
            validated_basemaps = BasemapParams(**basemaps)
            self.basemaps = validated_basemaps.model_dump(
                mode="json", by_alias=True, exclude_none=True
            )

        if raster:
            validated_raster = RasterParams(**raster)
            self.raster = validated_raster.model_dump(
                mode="json", by_alias=True, exclude_none=True
            )

        if urls:
            validated_urls = URLParams(**urls)
            self.urls = validated_urls.model_dump(
                mode="json", by_alias=True, exclude_none=True
            )

        if _internal:
            self._internal = _internal

        self.transport = BlockingWidgetTransport(widget=self)
        on_msg = lambda widget, content, buffers: self.transport.receive_message(
            content, buffers
        )
        self.on_msg(on_msg)

    def render(self) -> None:
        raise NotImplementedError()
