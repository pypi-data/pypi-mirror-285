# type: ignore

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, RootModel, confloat


class AnchorPointItem(RootModel[confloat(ge=-180.0, le=180.0)]):
    root: confloat(ge=-180.0, le=180.0)


class AnchorPointItem1(RootModel[confloat(ge=-90.0, le=90.0)]):
    root: confloat(ge=-90.0, le=90.0)


class TextVerticalAlign(Enum):
    top = "top"
    middle = "middle"
    bottom = "bottom"


class Annotation1(BaseModel):
    id: str = Field(..., description="The unique identifier of the annotation")
    kind: Literal["POINT"] = Field(
        ...,
        description="The type of annotation. Must be one of: TEXT, ARROW, POINT, CIRCLE",
    )
    is_visible: bool = Field(
        ...,
        alias="isVisible",
        description="Whether the annotation should be visible on the map",
    )
    auto_size: Optional[bool] = Field(
        True,
        alias="autoSize",
        description="Whether the annotation should be auto-sized horizontally to fit the text",
    )
    auto_size_y: Optional[bool] = Field(
        True,
        alias="autoSizeY",
        description="Whether the annotation should be auto-sized vertically to fit the text",
    )
    anchor_point: List[Union[AnchorPointItem, AnchorPointItem1]] = Field(
        ...,
        alias="anchorPoint",
        description="lng, lat of the anchor point",
        max_length=2,
        min_length=2,
    )
    label: str = Field(..., description="The textual description of the annotation")
    editor_state: Optional[Dict[str, Any]] = Field(
        None,
        alias="editorState",
        description="Serialized text editor state. Refer to https://lexical.dev/docs/api/interfaces/lexical.SerializedEditorState",
    )
    map_index: Optional[float] = Field(
        None,
        alias="mapIndex",
        description="The index of the map this annotation is attached to",
    )
    line_color: str = Field(
        ..., alias="lineColor", description="The color of the annotation line"
    )
    line_width: float = Field(
        ..., alias="lineWidth", description="The width of the annotation line"
    )
    text_width: float = Field(
        ..., alias="textWidth", description="The width of the annotation text"
    )
    text_height: float = Field(
        ..., alias="textHeight", description="The height of the annotation text"
    )
    text_vertical_align: Optional[TextVerticalAlign] = Field(
        None,
        alias="textVerticalAlign",
        description="The vertical alignment of the annotation text",
    )
    arm_length: float = Field(
        ..., alias="armLength", description="The length of the annotation arm in pixels"
    )
    angle: float = Field(..., description="The angle of the annotation in degrees")


class AnchorPointItem2(RootModel[confloat(ge=-180.0, le=180.0)]):
    root: confloat(ge=-180.0, le=180.0)


class AnchorPointItem3(RootModel[confloat(ge=-90.0, le=90.0)]):
    root: confloat(ge=-90.0, le=90.0)


class AnchorPoint(RootModel[List[Union[AnchorPointItem2, AnchorPointItem3]]]):
    root: List[Union[AnchorPointItem2, AnchorPointItem3]] = Field(
        ..., description="lng, lat of the anchor point", max_length=2, min_length=2
    )


class Angle(RootModel[float]):
    root: float = Field(..., description="The angle of the annotation in degrees")


class ArmLength(RootModel[float]):
    root: float = Field(..., description="The length of the annotation arm in pixels")


class AutoSize(RootModel[bool]):
    root: bool = Field(
        ...,
        description="Whether the annotation should be auto-sized horizontally to fit the text",
    )


class AutoSizeY(RootModel[bool]):
    root: bool = Field(
        ...,
        description="Whether the annotation should be auto-sized vertically to fit the text",
    )


class EditorState(RootModel[Optional[Dict[str, Any]]]):
    root: Optional[Dict[str, Any]] = None


class Id(RootModel[str]):
    root: str = Field(..., description="The unique identifier of the annotation")


class IsVisible(RootModel[bool]):
    root: bool = Field(
        ..., description="Whether the annotation should be visible on the map"
    )


class Label(RootModel[str]):
    root: str = Field(..., description="The textual description of the annotation")


class LineColor(RootModel[str]):
    root: str = Field(..., description="The color of the annotation line")


class LineWidth(RootModel[float]):
    root: float = Field(..., description="The width of the annotation line")


class MapIndex(RootModel[float]):
    root: float = Field(
        ..., description="The index of the map this annotation is attached to"
    )


class TextHeight(RootModel[float]):
    root: float = Field(..., description="The height of the annotation text")


class TextWidth(RootModel[float]):
    root: float = Field(..., description="The width of the annotation text")


class Annotation2(BaseModel):
    id: Id
    kind: Literal["CIRCLE"] = Field(
        ...,
        description="The type of annotation. Must be one of: TEXT, ARROW, POINT, CIRCLE",
    )
    is_visible: IsVisible = Field(..., alias="isVisible")
    auto_size: Optional[AutoSize] = Field(None, alias="autoSize")
    auto_size_y: Optional[AutoSizeY] = Field(None, alias="autoSizeY")
    anchor_point: AnchorPoint = Field(..., alias="anchorPoint")
    label: Label
    editor_state: Optional[EditorState] = Field(None, alias="editorState")
    map_index: Optional[MapIndex] = Field(None, alias="mapIndex")
    line_color: LineColor = Field(..., alias="lineColor")
    line_width: LineWidth = Field(..., alias="lineWidth")
    text_width: TextWidth = Field(..., alias="textWidth")
    text_height: TextHeight = Field(..., alias="textHeight")
    text_vertical_align: Optional[TextVerticalAlign] = Field(
        None, alias="textVerticalAlign"
    )
    arm_length: ArmLength = Field(..., alias="armLength")
    angle: Angle
    radius_in_meters: float = Field(..., alias="radiusInMeters")


class Annotation3(BaseModel):
    id: Id
    kind: Literal["ARROW"] = Field(
        ...,
        description="The type of annotation. Must be one of: TEXT, ARROW, POINT, CIRCLE",
    )
    is_visible: IsVisible = Field(..., alias="isVisible")
    auto_size: Optional[AutoSize] = Field(None, alias="autoSize")
    auto_size_y: Optional[AutoSizeY] = Field(None, alias="autoSizeY")
    anchor_point: AnchorPoint = Field(..., alias="anchorPoint")
    label: Label
    editor_state: Optional[EditorState] = Field(None, alias="editorState")
    map_index: Optional[MapIndex] = Field(None, alias="mapIndex")
    line_color: LineColor = Field(..., alias="lineColor")
    line_width: LineWidth = Field(..., alias="lineWidth")
    text_width: TextWidth = Field(..., alias="textWidth")
    text_height: TextHeight = Field(..., alias="textHeight")
    text_vertical_align: Optional[TextVerticalAlign] = Field(
        None, alias="textVerticalAlign"
    )
    arm_length: ArmLength = Field(..., alias="armLength")
    angle: Angle


class Annotation4(BaseModel):
    id: Id
    kind: Literal["TEXT"] = Field(
        ...,
        description="The type of annotation. Must be one of: TEXT, ARROW, POINT, CIRCLE",
    )
    is_visible: IsVisible = Field(..., alias="isVisible")
    auto_size: Optional[AutoSize] = Field(None, alias="autoSize")
    auto_size_y: Optional[AutoSizeY] = Field(None, alias="autoSizeY")
    anchor_point: AnchorPoint = Field(..., alias="anchorPoint")
    label: Label
    editor_state: Optional[EditorState] = Field(None, alias="editorState")
    map_index: Optional[MapIndex] = Field(None, alias="mapIndex")
    line_color: LineColor = Field(..., alias="lineColor")
    line_width: LineWidth = Field(..., alias="lineWidth")
    text_width: TextWidth = Field(..., alias="textWidth")
    text_height: TextHeight = Field(..., alias="textHeight")
    text_vertical_align: Optional[TextVerticalAlign] = Field(
        None, alias="textVerticalAlign"
    )


class Annotation(RootModel[Union[Annotation1, Annotation2, Annotation3, Annotation4]]):
    root: Union[Annotation1, Annotation2, Annotation3, Annotation4] = Field(
        ..., description="Annotation item to render on the map.", title="Annotation"
    )
