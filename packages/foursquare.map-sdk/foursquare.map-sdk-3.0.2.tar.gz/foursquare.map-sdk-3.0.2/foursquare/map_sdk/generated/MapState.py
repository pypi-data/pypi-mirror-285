# type: ignore

from __future__ import annotations

from typing import List, Literal, Optional, Union

import MapState2 as MapState2_1
from pydantic import BaseModel, Field, RootModel, confloat


class MapState1(BaseModel):
    map_view_mode: Literal["MODE_2D"] = Field(..., alias="mapViewMode")


class MapState2(BaseModel):
    latitude: Latitude
    longitude: Longitude
    zoom: Optional[Zoom] = None
    bearing: Optional[Bearing] = None
    pitch: Pitch
    drag_rotate: Optional[DragRotate] = Field(None, alias="dragRotate")
    map_split_mode: Literal["SWIPE_COMPARE"] = Field(..., alias="mapSplitMode")
    is_split: Literal[True] = Field(True, alias="isSplit")


class LabelsColorItem(RootModel[confloat(ge=0.0, le=255.0)]):
    root: confloat(ge=0.0, le=255.0)


class MapState5(BaseModel):
    pass


class MapState6(MapState1, MapState5):
    pass


class MapState7(MapState2, MapState5):
    pass


class MapState10(MapState1, MapState5):
    pass


class MapState11(MapState2, MapState5):
    pass


class Bearing(RootModel[float]):
    root: float


class DragRotate(RootModel[bool]):
    root: bool


class Latitude(RootModel[confloat(ge=-90.0, le=90.0)]):
    root: confloat(ge=-90.0, le=90.0)


class Longitude(RootModel[confloat(ge=-180.0, le=180.0)]):
    root: confloat(ge=-180.0, le=180.0)


class Pitch(RootModel[confloat(ge=0.0, lt=90.0)]):
    root: confloat(ge=0.0, lt=90.0)


class Zoom(RootModel[confloat(ge=0.0, le=25.0)]):
    root: confloat(ge=0.0, le=25.0)


class Field0(RootModel[confloat(ge=0.0, le=255.0)]):
    root: confloat(ge=0.0, le=255.0)


class MapState3(BaseModel):
    map_view_mode: Literal["MODE_GLOBE"] = Field(..., alias="mapViewMode")
    globe: Globe


class SplitMapViewport(BaseModel):
    latitude: Latitude
    longitude: Longitude
    zoom: Optional[Zoom] = None
    bearing: Optional[Bearing] = None
    pitch: Pitch
    drag_rotate: Optional[DragRotate] = Field(None, alias="dragRotate")


class MapState4(BaseModel):
    latitude: Latitude
    longitude: Longitude
    zoom: Optional[Zoom] = None
    bearing: Optional[Bearing] = None
    pitch: Pitch
    drag_rotate: Optional[DragRotate] = Field(None, alias="dragRotate")
    map_split_mode: Literal["DUAL_MAP"] = Field(..., alias="mapSplitMode")
    is_split: Literal[True] = Field(True, alias="isSplit")
    is_viewport_synced: Literal[False] = Field(False, alias="isViewportSynced")
    is_zoom_locked: Optional[bool] = Field(False, alias="isZoomLocked")
    split_map_viewports: List[SplitMapViewport] = Field(..., alias="splitMapViewports")


class MapState8(MapState3, MapState5):
    pass


class MapState9(MapState4, MapState5):
    pass


class MapState12(MapState3, MapState5):
    pass


class MapState(
    RootModel[
        Union[
            MapState6,
            MapState7,
            MapState8,
            MapState9,
            MapState10,
            MapState11,
            MapState12,
        ]
    ]
):
    root: Union[
        MapState6, MapState7, MapState8, MapState9, MapState10, MapState11, MapState12
    ] = Field(..., title="MapState")


class LabelsColor(RootModel[Union[List[Union[LabelsColorItem, Field0]], List[Field0]]]):
    root: Union[List[Union[LabelsColorItem, Field0]], List[Field0]]


class Config(BaseModel):
    atmosphere: bool
    azimuth: bool
    azimuth_angle: float = Field(..., alias="azimuthAngle")
    terminator: bool
    terminator_opacity: confloat(ge=0.0, le=1.0) = Field(..., alias="terminatorOpacity")
    basemap: bool
    labels: Optional[bool] = False
    labels_color: Optional[
        Union[List[Union[LabelsColorItem, Field0]], List[Field0]]
    ] = Field([114.75, 114.75, 114.75], alias="labelsColor")
    admin_lines: Optional[bool] = Field(True, alias="adminLines")
    admin_lines_color: Optional[LabelsColor] = Field(
        default_factory=lambda: LabelsColor.model_validate([40, 63, 93]),
        alias="adminLinesColor",
    )
    water: Optional[bool] = True
    water_color: Optional[LabelsColor] = Field(
        default_factory=lambda: LabelsColor.model_validate([17, 35, 48]),
        alias="waterColor",
    )
    surface: Optional[bool] = True
    surface_color: Optional[LabelsColor] = Field(
        default_factory=lambda: LabelsColor.model_validate([9, 16, 29]),
        alias="surfaceColor",
    )


class Globe(BaseModel):
    enabled: bool
    config: Config
