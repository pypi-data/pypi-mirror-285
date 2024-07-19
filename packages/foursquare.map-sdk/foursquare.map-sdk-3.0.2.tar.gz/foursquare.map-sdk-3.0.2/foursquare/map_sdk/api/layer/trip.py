from dataclasses import dataclass, field, replace
from typing import List, Literal, Optional, Union

import glom

from foursquare.map_sdk.api.base import generate_uuid, remove_none_values
from foursquare.map_sdk.api.color import Color, ColorRange
from foursquare.map_sdk.api.columns import GeojsonColumns, IdLatLngAltTimeColumns
from foursquare.map_sdk.api.text_label import TextLabel


class TripLayerGeojsonColumns(GeojsonColumns):
    ...


class TripLayerTimeseriesColumns(IdLatLngAltTimeColumns):
    ...


@dataclass
class TripLayer:
    """
    The Trip Layer can animate an object as it traverses space and time. Both the object's model and its path can be highly configured, allowing for detailed visualizations.

    Required:
      data_id: str - Dataset ID
      columns: Union[TripLayerGeojsonColumns, TripLayerTimeseriesColumns] - Mapping between data columns and layer properties

    Optional:
      id: str - Layer ID (use a string without space)
      label: str - The displayed layer label
      color: Color - Layer color
      is_visible: bool - Layer visibility on the map
      hidden: bool - Hide layer from the layer panel. This will prevent user from editing the layer
      include_legend: bool - Control of the layer is included in the legend
      text_label: List[TextLabel] - Layer's label information visible on hover
      opacity: float - Opacity of the layer
      thickness: float - Outline thickness
      color_range: ColorRange - Mapping configuration between color and values
      fade_trail: bool - Make the trail fade out over time
      fade_trail_duration: float - Number of seconds for the trail to fade out completely
      billboard: bool - Whether the layer is billboarded
      size_range: List[float] - A range of values that size can take
      size_scale: float - A scaling factor
      model_3d_enabled: bool - Use 3D models for visualization
      model_3d: Literal["airplane", "helicopter", "bicycle", "scooter", "car", "truck", "semitruck", "cargoship", "boeing777", "uber-evtol", "hang-glider"] - One of the built-in 3D models to use
      model_3d_custom_url: str - URL of a custom 3D model to load and use
      model_3d_color_enabled: bool - Color 3D models used
      model_3d_use_trail_color: bool - Color 3D models based on trail color
      model_3d_color: Color - A fixed color for 3D models
      adjust_roll: float - An additional offset for roll
      adjust_pitch: float - An additional offset for pitch
      adjust_yaw: float - An additional offset for yaw
      invert_roll: bool - Invert the roll angle winding direction
      invert_pitch: bool - Invert the pitch angle winding direction
      invert_yaw: bool - Invert the yaw angle winding direction
      fixed_roll: bool - Use a fixed roll value
      fixed_pitch: bool - Use a fixed pitch value
      fixed_yaw: bool - Use a fixed yaw value
      color_column: str - Name of the data column with color data
      color_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional color column type override
      color_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for color values
      size_column: str - Name of the data column with size data
      size_column_type: Literal["string", "real", "timestamp", "integer", "boolean", "date"] - An additional size column type override
      size_column_scale: Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"] - The value scale for size values
      roll_column: str - Name of the data column with roll data
      roll_column_type: Literal["real", "timestamp", "integer"] - An additional roll column type override
      roll_column_scale: Literal["linear"] - The value scale for roll values
      pitch_column: str - Name of the data column with pitch data
      pitch_column_type: Literal["real", "timestamp", "integer"] - An additional pitch column type override
      pitch_column_scale: Literal["linear"] - The value scale for pitch values
      yaw_column: str - Name of the data column with yaw data
      yaw_column_type: Literal["real", "timestamp", "integer"] - An additional yaw column type override
      yaw_column_scale: Literal["linear"] - The value scale for yaw values
    """

    data_id: str
    columns: Union[TripLayerGeojsonColumns, TripLayerTimeseriesColumns]

    id: Optional[str] = field(default_factory=generate_uuid)
    label: Optional[str] = None
    color: Optional[Color] = None
    is_visible: Optional[bool] = None
    hidden: Optional[bool] = None
    include_legend: Optional[bool] = None
    text_label: Optional[List[TextLabel]] = None
    opacity: Optional[float] = None
    thickness: Optional[float] = None
    color_range: Optional[ColorRange] = None
    fade_trail: Optional[bool] = None
    fade_trail_duration: Optional[float] = None
    billboard: Optional[bool] = None
    size_range: Optional[List[float]] = None
    size_scale: Optional[float] = None
    model_3d_enabled: Optional[bool] = None
    model_3d: Optional[
        Literal[
            "airplane",
            "helicopter",
            "bicycle",
            "scooter",
            "car",
            "truck",
            "semitruck",
            "cargoship",
            "boeing777",
            "uber-evtol",
            "hang-glider",
        ]
    ] = None
    model_3d_custom_url: Optional[str] = None
    model_3d_color_enabled: Optional[bool] = None
    model_3d_use_trail_color: Optional[bool] = None
    model_3d_color: Optional[Color] = None
    adjust_roll: Optional[float] = None
    adjust_pitch: Optional[float] = None
    adjust_yaw: Optional[float] = None
    invert_roll: Optional[bool] = None
    invert_pitch: Optional[bool] = None
    invert_yaw: Optional[bool] = None
    fixed_roll: Optional[bool] = None
    fixed_pitch: Optional[bool] = None
    fixed_yaw: Optional[bool] = None
    color_column: Optional[str] = None
    color_column_type: Optional[
        Literal["string", "real", "timestamp", "integer", "boolean", "date"]
    ] = None
    color_column_scale: Optional[
        Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"]
    ] = None
    size_column: Optional[str] = None
    size_column_type: Optional[
        Literal["string", "real", "timestamp", "integer", "boolean", "date"]
    ] = None
    size_column_scale: Optional[
        Literal["ordinal", "quantize", "quantile", "jenks", "custom", "customOrdinal"]
    ] = None
    roll_column: Optional[str] = None
    roll_column_type: Optional[Literal["real", "timestamp", "integer"]] = None
    roll_column_scale: Optional[Literal["linear"]] = None
    pitch_column: Optional[str] = None
    pitch_column_type: Optional[Literal["real", "timestamp", "integer"]] = None
    pitch_column_scale: Optional[Literal["linear"]] = None
    yaw_column: Optional[str] = None
    yaw_column_type: Optional[Literal["real", "timestamp", "integer"]] = None
    yaw_column_scale: Optional[Literal["linear"]] = None

    def to_json(self) -> dict:
        result: dict = {}
        glom.assign(result, "type", "trip")
        glom.assign(result, "config.dataId", self.data_id, dict)
        glom.assign(result, "config.columnMode", self.columns.mode, dict)
        glom.assign(result, "config.columns", self.columns.to_json(), dict)
        glom.assign(result, "id", self.id, dict)
        glom.assign(result, "config.label", self.label, dict)
        glom.assign(
            result, "config.color", self.color.to_json() if self.color else None, dict
        )
        glom.assign(result, "config.isVisible", self.is_visible, dict)
        glom.assign(result, "config.hidden", self.hidden, dict)
        if self.include_legend is not None:
            glom.assign(result, "config.legend.isIncluded", self.include_legend, dict)
        glom.assign(
            result,
            "config.textLabel",
            [label.to_json() for label in self.text_label] if self.text_label else None,
            dict,
        )
        glom.assign(result, "config.visConfig.opacity", self.opacity, dict)
        glom.assign(result, "config.visConfig.thickness", self.thickness, dict)
        glom.assign(
            result,
            "config.visConfig.colorRange",
            self.color_range.to_json() if self.color_range else None,
            dict,
        )
        glom.assign(result, "config.visConfig.fadeTrail", self.fade_trail, dict)
        glom.assign(
            result, "config.visConfig.trailLength", self.fade_trail_duration, dict
        )
        glom.assign(result, "config.visConfig.billboard", self.billboard, dict)
        glom.assign(result, "config.visConfig.sizeRange", self.size_range, dict)
        glom.assign(result, "config.visConfig.sizeScale", self.size_scale, dict)
        glom.assign(
            result, "config.visConfig.scenegraphEnabled", self.model_3d_enabled, dict
        )
        glom.assign(result, "config.visConfig.scenegraph", self.model_3d, dict)
        glom.assign(
            result,
            "config.visConfig.scenegraphCustomModelUrl",
            self.model_3d_custom_url,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.scenegraphColorEnabled",
            self.model_3d_color_enabled,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.scenegraphUseTrailColor",
            self.model_3d_use_trail_color,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.scenegraphColor",
            self.model_3d_color.to_json() if self.model_3d_color else None,
            dict,
        )
        glom.assign(result, "config.visConfig.adjustRoll", self.adjust_roll, dict)
        glom.assign(result, "config.visConfig.adjustPitch", self.adjust_pitch, dict)
        glom.assign(result, "config.visConfig.adjustYaw", self.adjust_yaw, dict)
        glom.assign(result, "config.visConfig.invertRoll", self.invert_roll, dict)
        glom.assign(result, "config.visConfig.invertPitch", self.invert_pitch, dict)
        glom.assign(result, "config.visConfig.invertYaw", self.invert_yaw, dict)
        glom.assign(result, "config.visConfig.fixedRoll", self.fixed_roll, dict)
        glom.assign(result, "config.visConfig.fixedPitch", self.fixed_pitch, dict)
        glom.assign(result, "config.visConfig.fixedYaw", self.fixed_yaw, dict)
        glom.assign(result, "visualChannels.colorField.name", self.color_column, dict)
        glom.assign(
            result, "visualChannels.colorField.type", self.color_column_type, dict
        )
        glom.assign(result, "visualChannels.colorScale", self.color_column_scale, dict)
        glom.assign(result, "visualChannels.sizeField.name", self.size_column, dict)
        glom.assign(
            result, "visualChannels.sizeField.type", self.size_column_type, dict
        )
        glom.assign(result, "visualChannels.sizeScale", self.size_column_scale, dict)
        glom.assign(result, "visualChannels.rollField.name", self.roll_column, dict)
        glom.assign(
            result, "visualChannels.rollField.type", self.roll_column_type, dict
        )
        glom.assign(result, "visualChannels.rollScale", self.roll_column_scale, dict)
        glom.assign(result, "visualChannels.pitchField.name", self.pitch_column, dict)
        glom.assign(
            result, "visualChannels.pitchField.type", self.pitch_column_type, dict
        )
        glom.assign(result, "visualChannels.pitchScale", self.pitch_column_scale, dict)
        glom.assign(result, "visualChannels.yawField.name", self.yaw_column, dict)
        glom.assign(result, "visualChannels.yawField.type", self.yaw_column_type, dict)
        glom.assign(result, "visualChannels.yawScale", self.yaw_column_scale, dict)
        return remove_none_values(result)

    @staticmethod
    def from_json(json: dict) -> "TripLayer":
        assert json["type"] == "trip", "Layer 'type' is not 'trip'"
        obj = TripLayer(
            data_id=glom.glom(json, "config.dataId"),
            columns={
                # pylint: disable-next=unnecessary-lambda
                TripLayerGeojsonColumns.mode: lambda columns: TripLayerGeojsonColumns.from_json(
                    columns
                ),
                # pylint: disable-next=unnecessary-lambda
                TripLayerTimeseriesColumns.mode: lambda columns: TripLayerTimeseriesColumns.from_json(
                    columns
                ),
            }[glom.glom(json, "config.columnMode")](glom.glom(json, "config.columns")),
        )
        obj.id = glom.glom(json, "id", default=None)
        obj.label = glom.glom(json, "config.label", default=None)
        __color = glom.glom(json, "config.color", default=None)
        obj.color = Color.from_json(__color) if __color else None
        obj.is_visible = glom.glom(json, "config.isVisible", default=None)
        obj.hidden = glom.glom(json, "config.hidden", default=None)
        obj.include_legend = glom.glom(json, "config.legend.isIncluded", default=None)
        __text_label = glom.glom(json, "config.textLabel", default=None)
        obj.text_label = (
            [TextLabel.from_json(label) for label in __text_label]
            if __text_label
            else None
        )
        obj.opacity = glom.glom(json, "config.visConfig.opacity", default=None)
        obj.thickness = glom.glom(json, "config.visConfig.thickness", default=None)
        __color_range = glom.glom(json, "config.visConfig.colorRange", default=None)
        obj.color_range = ColorRange.from_json(__color_range) if __color_range else None
        obj.fade_trail = glom.glom(json, "config.visConfig.fadeTrail", default=None)
        obj.fade_trail_duration = glom.glom(
            json, "config.visConfig.trailLength", default=None
        )
        obj.billboard = glom.glom(json, "config.visConfig.billboard", default=None)
        obj.size_range = glom.glom(json, "config.visConfig.sizeRange", default=None)
        obj.size_scale = glom.glom(json, "config.visConfig.sizeScale", default=None)
        obj.model_3d_enabled = glom.glom(
            json, "config.visConfig.scenegraphEnabled", default=None
        )
        obj.model_3d = glom.glom(json, "config.visConfig.scenegraph", default=None)
        obj.model_3d_custom_url = glom.glom(
            json, "config.visConfig.scenegraphCustomModelUrl", default=None
        )
        obj.model_3d_color_enabled = glom.glom(
            json, "config.visConfig.scenegraphColorEnabled", default=None
        )
        obj.model_3d_use_trail_color = glom.glom(
            json, "config.visConfig.scenegraphUseTrailColor", default=None
        )
        __model_3d_color = glom.glom(
            json, "config.visConfig.scenegraphColor", default=None
        )
        obj.model_3d_color = (
            Color.from_json(__model_3d_color) if __model_3d_color else None
        )
        obj.adjust_roll = glom.glom(json, "config.visConfig.adjustRoll", default=None)
        obj.adjust_pitch = glom.glom(json, "config.visConfig.adjustPitch", default=None)
        obj.adjust_yaw = glom.glom(json, "config.visConfig.adjustYaw", default=None)
        obj.invert_roll = glom.glom(json, "config.visConfig.invertRoll", default=None)
        obj.invert_pitch = glom.glom(json, "config.visConfig.invertPitch", default=None)
        obj.invert_yaw = glom.glom(json, "config.visConfig.invertYaw", default=None)
        obj.fixed_roll = glom.glom(json, "config.visConfig.fixedRoll", default=None)
        obj.fixed_pitch = glom.glom(json, "config.visConfig.fixedPitch", default=None)
        obj.fixed_yaw = glom.glom(json, "config.visConfig.fixedYaw", default=None)
        obj.color_column = glom.glom(
            json, "visualChannels.colorField.name", default=None
        )
        obj.color_column_type = glom.glom(
            json, "visualChannels.colorField.type", default=None
        )
        obj.color_column_scale = glom.glom(
            json, "visualChannels.colorScale", default=None
        )
        obj.size_column = glom.glom(json, "visualChannels.sizeField.name", default=None)
        obj.size_column_type = glom.glom(
            json, "visualChannels.sizeField.type", default=None
        )
        obj.size_column_scale = glom.glom(
            json, "visualChannels.sizeScale", default=None
        )
        obj.roll_column = glom.glom(json, "visualChannels.rollField.name", default=None)
        obj.roll_column_type = glom.glom(
            json, "visualChannels.rollField.type", default=None
        )
        obj.roll_column_scale = glom.glom(
            json, "visualChannels.rollScale", default=None
        )
        obj.pitch_column = glom.glom(
            json, "visualChannels.pitchField.name", default=None
        )
        obj.pitch_column_type = glom.glom(
            json, "visualChannels.pitchField.type", default=None
        )
        obj.pitch_column_scale = glom.glom(
            json, "visualChannels.pitchScale", default=None
        )
        obj.yaw_column = glom.glom(json, "visualChannels.yawField.name", default=None)
        obj.yaw_column_type = glom.glom(
            json, "visualChannels.yawField.type", default=None
        )
        obj.yaw_column_scale = glom.glom(json, "visualChannels.yawScale", default=None)
        return obj

    def clone(self) -> "TripLayer":
        return replace(self)
