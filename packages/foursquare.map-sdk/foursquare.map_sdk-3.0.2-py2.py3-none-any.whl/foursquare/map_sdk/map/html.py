from html import escape
from pathlib import Path
from typing import Dict, Optional

from foursquare.map_sdk.environment import CURRENT_ENVIRONMENT, Environment
from foursquare.map_sdk.map.base import (
    BasemapParams,
    BaseNonInteractiveMap,
    MapInitialState,
    MapStyle,
    URLParams,
)
from foursquare.map_sdk.transport.html import HTMLTransport

TEMPLATE_DIR = (Path(__file__).parent / ".." / "templates").resolve()

IFRAME_TEMPLATE = """\
<iframe
    height="{height}"
    width="{width}"
    srcdoc="{srcdoc}"
></iframe>
"""


class HTMLMap(BaseNonInteractiveMap):
    transport: HTMLTransport
    style: MapStyle
    iframe: bool
    api_key: str

    def __init__(
        self,
        api_key: str,
        initial_state: Optional[Dict] = None,
        style: Optional[Dict] = None,
        basemaps: Optional[Dict] = None,
        urls: Optional[Dict] = None,
        iframe: Optional[bool] = None,
    ):
        self.api_key = api_key

        if CURRENT_ENVIRONMENT == Environment.DATABRICKS:
            self.iframe = True
        else:
            if iframe is not None:
                self.iframe = iframe
            else:
                self.iframe = False

        if initial_state:
            self.initial_state = MapInitialState(**initial_state).model_dump(
                mode="json", by_alias=True, exclude_none=True
            )
        else:
            self.initial_state = {}

        if style:
            self.style = MapStyle(**style)
        else:
            self.style = MapStyle()

        if basemaps:
            validated_basemaps = BasemapParams(**basemaps)
            self.basemaps = validated_basemaps.model_dump(
                mode="json", by_alias=True, exclude_none=True
            )
        else:
            self.basemaps = {}

        if urls:
            validated_urls = URLParams(**urls)
            self.urls = validated_urls.model_dump(
                mode="json", by_alias=True, exclude_none=True
            )
        else:
            self.urls = {}

        self.transport = HTMLTransport()
        self.rendered = False

    def _repr_html_(self) -> str:
        return self.render()

    def render(self) -> str:
        html_string = self.transport.render_template(
            api_key=self.api_key,
            initial_state=self.initial_state,
            style=self.style.model_dump(mode="json", exclude_none=True),
            basemaps=self.basemaps,
            urls=self.urls,
        )
        if not self.iframe:
            return html_string

        return IFRAME_TEMPLATE.format(
            height=self.style.height, width=self.style.width, srcdoc=escape(html_string)
        )
