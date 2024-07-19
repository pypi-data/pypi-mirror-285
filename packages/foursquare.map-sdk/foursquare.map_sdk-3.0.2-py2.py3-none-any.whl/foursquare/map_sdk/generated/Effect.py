# type: ignore

from __future__ import annotations

from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field, RootModel, confloat


class Parameters(BaseModel):
    brightness: Optional[confloat(ge=-1.0, le=1.0)] = Field(
        0, description="The brightness of the effect"
    )
    contrast: Optional[confloat(ge=-1.0, le=1.0)] = Field(
        0, description="The contrast of the effect"
    )


class Effect1(BaseModel):
    id: str = Field(..., description="The id of the effect")
    type: Literal["brightnessContrast"] = Field(
        ..., description="The type of the effect"
    )
    is_enabled: Optional[bool] = Field(
        True, alias="isEnabled", description="Whether the effect is enabled"
    )
    parameters: Parameters


class CenterItem(RootModel[confloat(ge=0.0, le=1.0)]):
    root: confloat(ge=0.0, le=1.0)


class Parameters1(BaseModel):
    center: Optional[List[CenterItem]] = Field(
        [0.5, 0.5],
        description="The center point of the effect",
        max_length=2,
        min_length=2,
    )
    angle: Optional[confloat(ge=0.0, le=1.5707963267948966)] = Field(
        1.1, description="The rotation angle of the grid"
    )
    size: Optional[confloat(ge=0.0, le=100.0)] = 4


class DeltaItem(RootModel[confloat(ge=0.0, le=1.0)]):
    root: confloat(ge=0.0, le=1.0)


class Parameters3(BaseModel):
    radius: Optional[confloat(ge=0.0, le=100.0)] = Field(
        2, description="The radius of the blur"
    )
    delta: Optional[List[DeltaItem]] = Field(
        [1, 0], description="The direction of the blur", max_length=2, min_length=2
    )


class Parameters5(BaseModel):
    hue: Optional[confloat(ge=-1.0, le=1.0)] = Field(
        0, description="The hue of the effect"
    )
    saturation: Optional[confloat(ge=-1.0, le=1.0)] = Field(
        0, description="The saturation of the effect"
    )


class Parameters6(BaseModel):
    strength: Optional[confloat(ge=0.0, le=1.0)] = Field(
        0.5, description="The strength of the effect"
    )


class ShadowColorItem(RootModel[confloat(ge=0.0, le=255.0)]):
    root: confloat(ge=0.0, le=255.0)


class ScreenXyItem(RootModel[confloat(ge=0.0, le=1.0)]):
    root: confloat(ge=0.0, le=1.0)


class Parameters11(BaseModel):
    amount: Optional[confloat(ge=0.0, le=1.0)] = Field(
        0.5, description="The amount of noise to apply."
    )


class Parameters12(BaseModel):
    amount: Optional[confloat(ge=0.0, le=1.0)] = Field(
        0.5, description="The amount of the effect"
    )


class StartItem(RootModel[confloat(ge=0.0, le=1.0)]):
    root: confloat(ge=0.0, le=1.0)


class EndItem(RootModel[confloat(ge=0.0, le=1.0)]):
    root: confloat(ge=0.0, le=1.0)


class Parameters13(BaseModel):
    blur_radius: Optional[confloat(ge=0.0, le=50.0)] = Field(
        20, alias="blurRadius", description="The radius of the blur"
    )
    gradient_radius: Optional[confloat(ge=0.0, le=400.0)] = Field(
        20, alias="gradientRadius", description="The radius of the gradient"
    )
    start: Optional[List[StartItem]] = Field(
        [0, 0], description="The start of the gradient", max_length=2, min_length=2
    )
    end: Optional[List[EndItem]] = Field(
        [1, 1], description="The end of the gradient", max_length=2, min_length=2
    )
    invert: Optional[bool] = Field(False, description="Whether to invert the gradient")


class Parameters14(BaseModel):
    radius: Optional[confloat(ge=0.0, le=100.0)] = Field(
        20, description="The radius of the blur"
    )
    delta: Optional[List[DeltaItem]] = Field(
        [1, 0], description="The direction of the blur", max_length=2, min_length=2
    )


class Parameters15(BaseModel):
    amount: Optional[confloat(ge=-1.0, le=1.0)] = Field(
        0, description="The amount of the effect"
    )


class Parameters16(BaseModel):
    radius: Optional[confloat(ge=0.0, le=1.0)] = Field(
        0.5, description="The radius of the vignette"
    )
    amount: Optional[confloat(ge=0.0, le=1.0)] = Field(
        0.5, description="The amount of vignette to apply"
    )


class Id(RootModel[str]):
    root: str = Field(..., description="The id of the effect")


class IsEnabled(RootModel[bool]):
    root: bool = Field(..., description="Whether the effect is enabled")


class Center(RootModel[List[CenterItem]]):
    root: List[CenterItem] = Field(
        ..., description="The center point of the effect", max_length=2, min_length=2
    )


class AmbientLightIntensity(RootModel[float]):
    root: float = Field(..., description="The intensity of the ambient light")


class Field0Item(RootModel[confloat(ge=0.0, le=255.0)]):
    root: confloat(ge=0.0, le=255.0)


class Field0(RootModel[confloat(ge=0.0, le=255.0)]):
    root: confloat(ge=0.0, le=255.0)


class Field1(RootModel[List[Field0]]):
    root: List[Field0] = Field(..., max_length=4, min_length=4)


class ShadowIntensity(RootModel[float]):
    root: float = Field(..., description="The intensity of the shadow")


class SunLightIntensity(RootModel[float]):
    root: float = Field(..., description="The intensity of the sun light")


class Effect2(BaseModel):
    id: Id
    type: Literal["colorHalftone"] = Field(..., description="The type of the effect")
    is_enabled: Optional[IsEnabled] = Field(None, alias="isEnabled")
    parameters: Parameters1


class Parameters2(BaseModel):
    center: Optional[Center] = None
    angle: Optional[confloat(ge=0.0, le=1.5707963267948966)] = Field(
        1.1, description="The rotation angle of the grid"
    )
    size: Optional[confloat(ge=0.0, le=100.0)] = Field(
        3, description="The size of the dots."
    )


class Effect3(BaseModel):
    id: Id
    type: Literal["dotScreen"] = Field(..., description="The type of the effect")
    is_enabled: Optional[IsEnabled] = Field(None, alias="isEnabled")
    parameters: Parameters2


class Effect4(BaseModel):
    id: Id
    type: Literal["edgeWork"] = Field(..., description="The type of the effect")
    is_enabled: Optional[IsEnabled] = Field(None, alias="isEnabled")
    parameters: Parameters3


class Parameters4(BaseModel):
    center: Optional[Center] = None
    scale: Optional[confloat(ge=0.0, le=50.0)] = Field(
        10, description="The scale (size) of the hexagons"
    )


class Effect5(BaseModel):
    id: Id
    type: Literal["hexagonalPixelate"] = Field(
        ..., description="The type of the effect"
    )
    is_enabled: Optional[IsEnabled] = Field(None, alias="isEnabled")
    parameters: Parameters4


class Effect6(BaseModel):
    id: Id
    type: Literal["hueSaturation"] = Field(..., description="The type of the effect")
    is_enabled: Optional[IsEnabled] = Field(None, alias="isEnabled")
    parameters: Parameters5


class Effect7(BaseModel):
    id: Id
    type: Literal["ink"] = Field(..., description="The type of the effect")
    is_enabled: Optional[IsEnabled] = Field(None, alias="isEnabled")
    parameters: Parameters6


class Effect10(BaseModel):
    id: Id
    type: Literal["noise"] = Field(..., description="The type of the effect")
    is_enabled: Optional[IsEnabled] = Field(None, alias="isEnabled")
    parameters: Parameters11


class Effect11(BaseModel):
    id: Id
    type: Literal["sepia"] = Field(..., description="The type of the effect")
    is_enabled: Optional[IsEnabled] = Field(None, alias="isEnabled")
    parameters: Parameters12


class Effect12(BaseModel):
    id: Id
    type: Literal["tiltShift"] = Field(..., description="The type of the effect")
    is_enabled: Optional[IsEnabled] = Field(None, alias="isEnabled")
    parameters: Parameters13


class Effect13(BaseModel):
    id: Id
    type: Literal["triangleBlur"] = Field(..., description="The type of the effect")
    is_enabled: Optional[IsEnabled] = Field(None, alias="isEnabled")
    parameters: Parameters14


class Effect14(BaseModel):
    id: Id
    type: Literal["vibrance"] = Field(..., description="The type of the effect")
    is_enabled: Optional[IsEnabled] = Field(None, alias="isEnabled")
    parameters: Parameters15


class Effect15(BaseModel):
    id: Id
    type: Literal["vignette"] = Field(..., description="The type of the effect")
    is_enabled: Optional[IsEnabled] = Field(None, alias="isEnabled")
    parameters: Parameters16


class Parameters17(BaseModel):
    center: Optional[Center] = None
    strength: Optional[confloat(ge=0.0, le=1.0)] = Field(
        0.5, description="The strength of the effect"
    )


class Effect16(BaseModel):
    id: Id
    type: Literal["zoomBlur"] = Field(..., description="The type of the effect")
    is_enabled: Optional[IsEnabled] = Field(None, alias="isEnabled")
    parameters: Parameters17


class ShadowColor(RootModel[Union[List[Union[ShadowColorItem, Field0]], List[Field0]]]):
    root: Union[List[Union[ShadowColorItem, Field0]], List[Field0]] = Field(
        ..., description="The color of the shadow"
    )


class Field0Model(RootModel[List[Union[Field0Item, Field0]]]):
    root: List[Union[Field0Item, Field0]] = Field(..., max_length=3, min_length=3)


class SunLightColor(RootModel[Union[Field0Model, Field1]]):
    root: Union[Field0Model, Field1] = Field(
        ..., description="The color of the sun light"
    )


class Parameters7(BaseModel):
    shadow_intensity: float = Field(
        ..., alias="shadowIntensity", description="The intensity of the shadow"
    )
    shadow_color: Union[List[Union[ShadowColorItem, Field0]], List[Field0]] = Field(
        ..., alias="shadowColor", description="The color of the shadow"
    )
    sun_light_color: Union[Field0Model, Field1] = Field(
        ..., alias="sunLightColor", description="The color of the sun light"
    )
    sun_light_intensity: float = Field(
        ..., alias="sunLightIntensity", description="The intensity of the sun light"
    )
    ambient_light_color: Union[Field0Model, Field1] = Field(
        ..., alias="ambientLightColor", description="The color of the ambient light"
    )
    ambient_light_intensity: float = Field(
        ...,
        alias="ambientLightIntensity",
        description="The intensity of the ambient light",
    )
    time_mode: Literal["pick"] = Field(..., alias="timeMode")
    timestamp: float = Field(
        ..., description="The timestamp to use for the sun position"
    )
    timezone: Optional[str] = Field("UTC", description="The time zone to use")


class Parameters10(BaseModel):
    screen_xy: Optional[List[ScreenXyItem]] = Field(
        [0.5, 0.5],
        alias="screenXY",
        description="The screen position of the magnifier",
        max_length=2,
        min_length=2,
    )
    radius_pixels: Optional[confloat(ge=0.0, le=500.0)] = Field(
        200, alias="radiusPixels", description="The radius of the magnify effect"
    )
    zoom: Optional[confloat(ge=0.0, le=500.0)] = Field(
        2, description="The zoom level of the magnify effect"
    )
    border_width_pixels: Optional[confloat(ge=0.0)] = Field(
        0, alias="borderWidthPixels", description="The width of the border"
    )
    border_color: Optional[Union[Field0Model, Field1]] = Field(
        [255, 255, 255, 255], alias="borderColor", description="The color of the border"
    )


class Effect9(BaseModel):
    id: Id
    type: Literal["magnify"] = Field(..., description="The type of the effect")
    is_enabled: Optional[IsEnabled] = Field(None, alias="isEnabled")
    parameters: Parameters10


class AmbientLightColor(RootModel[Union[Field0Model, Field1]]):
    root: Union[Field0Model, Field1] = Field(
        ..., description="The color of the ambient light"
    )


class Parameters8(BaseModel):
    shadow_intensity: ShadowIntensity = Field(..., alias="shadowIntensity")
    shadow_color: ShadowColor = Field(..., alias="shadowColor")
    sun_light_color: SunLightColor = Field(..., alias="sunLightColor")
    sun_light_intensity: SunLightIntensity = Field(..., alias="sunLightIntensity")
    ambient_light_color: AmbientLightColor = Field(..., alias="ambientLightColor")
    ambient_light_intensity: AmbientLightIntensity = Field(
        ..., alias="ambientLightIntensity"
    )
    time_mode: Literal["current"] = Field(..., alias="timeMode")


class Parameters9(BaseModel):
    shadow_intensity: ShadowIntensity = Field(..., alias="shadowIntensity")
    shadow_color: ShadowColor = Field(..., alias="shadowColor")
    sun_light_color: SunLightColor = Field(..., alias="sunLightColor")
    sun_light_intensity: SunLightIntensity = Field(..., alias="sunLightIntensity")
    ambient_light_color: AmbientLightColor = Field(..., alias="ambientLightColor")
    ambient_light_intensity: AmbientLightIntensity = Field(
        ..., alias="ambientLightIntensity"
    )
    time_mode: Literal["animation"] = Field(..., alias="timeMode")


class Effect8(BaseModel):
    id: Id
    type: Literal["lightAndShadow"] = Field(..., description="The type of the effect")
    is_enabled: Optional[IsEnabled] = Field(None, alias="isEnabled")
    parameters: Union[Parameters7, Parameters8, Parameters9]


class Effect(
    RootModel[
        Union[
            Effect1,
            Effect2,
            Effect3,
            Effect4,
            Effect5,
            Effect6,
            Effect7,
            Effect8,
            Effect9,
            Effect10,
            Effect11,
            Effect12,
            Effect13,
            Effect14,
            Effect15,
            Effect16,
        ]
    ]
):
    root: Union[
        Effect1,
        Effect2,
        Effect3,
        Effect4,
        Effect5,
        Effect6,
        Effect7,
        Effect8,
        Effect9,
        Effect10,
        Effect11,
        Effect12,
        Effect13,
        Effect14,
        Effect15,
        Effect16,
    ] = Field(..., title="Effect")
