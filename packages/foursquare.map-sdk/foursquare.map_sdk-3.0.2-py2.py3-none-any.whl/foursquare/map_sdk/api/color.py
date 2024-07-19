from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional, Tuple, Union

import glom


@dataclass
class Color:
    """RGB(A) color representation (all channel values are in range [0,255])

    Optional:
      r: int - red channel
      g: int - green channel
      b: int - blue channel
      a: int - alpha channel
    """

    r: int = 255
    g: int = 255
    b: int = 255
    a: Optional[int] = None

    def to_json(self) -> list:
        if self.a:
            return [self.r, self.g, self.b, self.a]
        else:
            return [self.r, self.g, self.b]

    @staticmethod
    def from_json(json: list):
        return Color(
            r=glom.glom(json, "0"),
            g=glom.glom(json, "1"),
            b=glom.glom(json, "2"),
            a=glom.glom(json, "3", default=None),
        )

    @staticmethod
    def from_hex(hex_color: str):
        # Check if the hex string starts with a '#' and remove it if present
        if hex_color.startswith("#"):
            hex_color = hex_color[1:]

        # Ensure the length of the hex string is either 6 (RGB) or 8 (RGBA)
        if len(hex_color) not in (6, 8):
            raise ValueError(
                "Invalid hex string length. Must be 6 (RGB) or 8 (RGBA) characters long."
            )

        # Convert the hex string to RGBA
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        if len(hex_color) == 8:
            a = int(hex_color[6:8], 16)
        else:
            # Default alpha value if not provided
            a = 255

        return Color(r=r, g=g, b=b, a=a)


Value = Union[str, float, int]
ValueRange = Tuple[Value, Value]


@dataclass
class ColorRange:
    """Describes the mapping and the distribution between values and colors.

    Optional:
        type: Literal["sequential", "qualitative", "diverging", "cyclical", "custom", "ordinal", "customOrdinal"]
        colors: List[str] - The list of colors (hex values)
        color_map: List[Tuple[Union[Value, ValueRange], str]] - Mapping between values (or value ranges) and colors
        color_legends: Dict[str, str] - Names of the colors displayed in the map legend
        name: str - Name of the color range
        category: str - Name of the category for the color range
        reversed: bool - Controls whether to reverse the mappings
    """

    type: Optional[
        Literal[
            "sequential",
            "qualitative",
            "diverging",
            "cyclical",
            "custom",
            "ordinal",
            "customOrdinal",
        ]
    ] = None
    name: Optional[str] = None
    category: Optional[str] = None
    colors: List[str] = field(default_factory=list)
    reversed: Optional[bool] = None
    color_map: Optional[List[Tuple[Union[Value, ValueRange], str]]] = None
    color_legends: Optional[Dict[str, str]] = None

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "category": self.category,
            "colors": self.colors,
            "reversed": self.reversed,
            "colorMap": self.color_map,
            "colorLegends": self.color_legends,
        }

    @staticmethod
    def from_json(json: dict) -> "ColorRange":
        return ColorRange(
            name=glom.glom(json, "name", default=None),
            type=glom.glom(json, "type", default=None),
            category=glom.glom(json, "category", default=None),
            colors=glom.glom(json, "colors", default=None),
            reversed=glom.glom(json, "reversed", default=None),
            color_map=glom.glom(json, "colorMap", default=None),
            color_legends=glom.glom(json, "colorLegends", default=None),
        )
