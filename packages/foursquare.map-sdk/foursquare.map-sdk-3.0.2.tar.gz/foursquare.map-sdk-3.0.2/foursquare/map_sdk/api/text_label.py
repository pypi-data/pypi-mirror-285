from dataclasses import dataclass, field
from typing import Literal, Optional, Tuple, cast

import glom

from foursquare.map_sdk.api.color import Color


@dataclass
class TextLabel:
    """Display and data mapping configuration for a text label item.

    Optional:
      field_name: str - name of the data column which to use
      field_type: str - an override for the column data type for how it will be interpreted
      field_format: str - additional field fomatting
      size: float - font size
      color: Color - font color
      background: bool - has background
      background_color: Color - background color
      outline_width: float - outline width
      outline_color: Color - outline color
      offset: Tuple[float, float] - a label's (x,y) offset
      anchor: Literal["start", "middle", "end"] - text anchor position
      alignment: Literal["top", "center", "bottom"] - text alignment option
    """

    field_name: Optional[str] = None
    field_type: Optional[str] = None
    field_format: Optional[str] = None
    size: Optional[float] = cast(Optional[float], None)
    color: Color = field(default_factory=Color)
    offset: Optional[Tuple[float, float]] = None
    anchor: Optional[Literal["start", "middle", "end"]] = None
    alignment: Optional[Literal["top", "center", "bottom"]] = None
    background: Optional[bool] = None
    background_color: Optional[Color] = None
    outline_color: Optional[Color] = None
    outline_width: Optional[float] = None

    def to_json(self) -> dict:
        result: dict = {}
        result["field"] = [
            {
                "field": {"name": self.field_name, "type": self.field_type},
                "format": self.field_format,
            }
        ]
        glom.assign(result, "size", self.size, dict)
        glom.assign(result, "color", self.color.to_json() if self.color else None, dict)
        glom.assign(result, "offset", self.offset, dict)
        glom.assign(result, "anchor", self.anchor, dict)
        glom.assign(result, "alignment", self.alignment, dict)
        glom.assign(result, "background", self.background, dict)
        glom.assign(
            result,
            "backgroundColor",
            self.background_color.to_json() if self.background_color else None,
            dict,
        )
        glom.assign(
            result,
            "outlineColor",
            self.outline_color.to_json() if self.outline_color else None,
            dict,
        )
        glom.assign(result, "outlineWidth", self.outline_width, dict)
        return result

    @staticmethod
    def from_json(json: dict):
        obj = TextLabel()
        obj.field_name = glom.glom(json, "field.0.field.name", default=None)
        obj.field_type = glom.glom(json, "field.0.field.type", default=None)
        obj.field_format = glom.glom(json, "field.0.format", default=None)
        obj.size = glom.glom(json, "size", default=None)
        __color = glom.glom(json, "color", default=None)
        obj.color = Color.from_json(__color) if __color else None
        obj.offset = glom.glom(json, "offset", default=None)
        obj.anchor = glom.glom(json, "anchor", default=None)
        obj.alignment = glom.glom(json, "alignment", default=None)
        obj.background = glom.glom(json, "background", default=None)
        __background_color = glom.glom(json, "backgroundColor", default=None)
        obj.background_color = (
            Color.from_json(__background_color) if __background_color else None
        )
        __outline_color = glom.glom(json, "outlineColor", default=None)
        obj.outline_color = (
            Color.from_json(__outline_color) if __outline_color else None
        )
        obj.outline_width = glom.glom(json, "outlineWidth", default=None)
        return obj
