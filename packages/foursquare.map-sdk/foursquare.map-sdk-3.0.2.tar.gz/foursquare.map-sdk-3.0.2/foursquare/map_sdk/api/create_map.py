import sys
from typing import Dict, Literal, Optional, Union, overload

from foursquare.map_sdk.environment import CURRENT_ENVIRONMENT, Environment
from foursquare.map_sdk.errors import MapSDKException
from foursquare.map_sdk.map import HTMLMap, SyncWidgetMap

__all__ = ("create_map",)

DATABRICKS_HTML_MAP_MSG = """Databricks environment detected, using HTML renderer.
SDK function calls after a map is rendered will not update the map automatically,
the map must be re-rendered to update.
To hide this warning in the future, pass `renderer="html"`.
"""


# Note: not possible (I think) to have this typing overload understand when the current environment
# is databricks
@overload
def create_map(
    *,
    api_key: str,
    renderer: Literal["html"],
    initial_state: Optional[Dict] = None,
    style: Optional[Dict] = None,
    basemaps: Optional[Dict] = None,
    urls: Optional[Dict] = None,
    iframe: Optional[bool] = None,
    raster: Optional[Dict] = None,
    _internal: Optional[Dict] = None,
) -> HTMLMap:
    ...


@overload
def create_map(
    *,
    api_key: str,
    renderer: Literal["widget", None] = None,
    initial_state: Optional[Dict] = None,
    style: Optional[Dict] = None,
    basemaps: Optional[Dict] = None,
    urls: Optional[Dict] = None,
    iframe: Optional[bool] = None,
    raster: Optional[Dict] = None,
    _internal: Optional[Dict] = None,
) -> SyncWidgetMap:
    ...


def create_map(
    *,
    api_key: str,
    renderer: Literal["html", "widget", None] = None,
    initial_state: Optional[Dict] = None,
    style: Optional[Dict] = None,
    basemaps: Optional[Dict] = None,
    urls: Optional[Dict] = None,
    iframe: Optional[bool] = None,
    raster: Optional[Dict] = None,
    _internal: Optional[Dict] = None,
) -> Union[HTMLMap, SyncWidgetMap]:
    """Create a new map

    Kwargs:
        api_key (str): API Key used to authenticate your account
        renderer (str): Which renderer to use for the map, either "html" or "widget".
                        Default: "widget" (if supported by your environment).
    """

    if CURRENT_ENVIRONMENT == Environment.DATABRICKS:
        if renderer == "widget":
            raise MapSDKException(
                "Cannot use widget renderer in Databricks environment"
            )
        elif renderer is None:
            sys.stderr.write(DATABRICKS_HTML_MAP_MSG)
        return HTMLMap(
            api_key=api_key,
            initial_state=initial_state,
            style=style,
            basemaps=basemaps,
            urls=urls,
            iframe=iframe,
        )
    elif renderer == "html":
        return HTMLMap(
            api_key=api_key,
            initial_state=initial_state,
            style=style,
            basemaps=basemaps,
            urls=urls,
            iframe=iframe,
        )
    else:
        return SyncWidgetMap(
            api_key=api_key,
            initial_state=initial_state,
            style=style,
            basemaps=basemaps,
            urls=urls,
            iframe=iframe,
            raster=raster,
            _internal=_internal,
        )
