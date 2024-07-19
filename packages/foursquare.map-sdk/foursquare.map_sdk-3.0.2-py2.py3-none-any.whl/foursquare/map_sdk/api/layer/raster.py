from dataclasses import dataclass, field, replace
from typing import List, Literal, Optional

import glom

from foursquare.map_sdk.api.base import generate_uuid, remove_none_values
from foursquare.map_sdk.api.color import Color, ColorRange


@dataclass
class RasterLayer:
    """
    Raster layers are used to show satellite and aerial imagery. They allow you to work interactively directly with massive, petabyte-scale image collections stored in Cloud Optimized GeoTIFF format.

    Required:
      data_id: str - Dataset ID

    Optional:
      id: str - Layer ID (use a string without space)
      label: str - The displayed layer label
      color: Color - Layer color
      is_visible: bool - Layer visibility on the map
      hidden: bool - Hide layer from the layer panel. This will prevent user from editing the layer
      include_legend: bool - Control of the layer is included in the legend
      preset: Literal["trueColor", "infrared", "agriculture", "forestBurn", "ndvi", "savi", "msavi", "ndmi", "nbr", "nbr2", "singleBand"] - Raster tile preset
      mosaic_id: str - Mosaic ID
      use_stac_searching: bool - Use STAC searcing
      stac_search_provider: Literal["earth-search", "microsoft"] - A STAC search provided which to use
      start_date: str - 🤷
      end_date: str - 🤷
      dynamic_color: bool - Color ranges are dynamicly calculated and mapped based on the content visible in the viewport
      color_map_id: Literal["cfastie", "rplumbo", "schwarzwald", "viridis", "plasma", "inferno", "magma", "cividis", "greys", "purples", "blues", "greens", "oranges", "reds", "ylorbr", "ylorrd", "orrd", "purd", "rdpu", "bupu", "gnbu", "pubu", "ylgnbu", "pubugn", "bugn", "ylgn", "binary", "gray", "bone", "pink", "spring", "summer", "autumn", "winter", "cool", "wistia", "hot", "afmhot", "gist_heat", "copper", "piyg", "prgn", "brbg", "puor", "rdgy", "rdbu", "rdylbu", "rdylgn", "spectral", "coolwarm", "bwr", "seismic", "twilight", "twilight_shifted", "hsv", "flag", "prism", "ocean", "gist_earth", "terrain", "gist_stern", "gnuplot", "gnuplot2", "cmrmap", "cubehelix", "brg", "gist_rainbow", "rainbow", "jet", "nipy_spectral", "gist_ncar"] - One of the predefined color maps to use for mappings
      color_range: ColorRange - Mapping configuration between color and values
      linear_rescaling_factor: List[float] - Linear rescaling factor
      non_linear_rescaling: bool - Use non-linear rescaling
      gamma_contrast_factor: float - Gamma contrast factor
      sigmoidal_contrast_factor: float - Sigmoidal contrast factor
      sigmoidal_bias_factor: float - Sigmoidal bias factor
      saturation_value: float - Saturation value
      filter_enabled: bool - Enable filter
      filter_range: List[float] - Filter's range
      opacity: float - Opacity of the layer
      single_band_name: str - Name of a single band to use
      enable_terrain: bool - Enable terrain
    """

    data_id: str

    id: Optional[str] = field(default_factory=generate_uuid)
    label: Optional[str] = None
    color: Optional[Color] = None
    is_visible: Optional[bool] = None
    hidden: Optional[bool] = None
    include_legend: Optional[bool] = None
    preset: Optional[
        Literal[
            "trueColor",
            "infrared",
            "agriculture",
            "forestBurn",
            "ndvi",
            "savi",
            "msavi",
            "ndmi",
            "nbr",
            "nbr2",
            "singleBand",
        ]
    ] = None
    mosaic_id: Optional[str] = None
    use_stac_searching: Optional[bool] = None
    stac_search_provider: Optional[Literal["earth-search", "microsoft"]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    dynamic_color: Optional[bool] = None
    color_map_id: Optional[
        Literal[
            "cfastie",
            "rplumbo",
            "schwarzwald",
            "viridis",
            "plasma",
            "inferno",
            "magma",
            "cividis",
            "greys",
            "purples",
            "blues",
            "greens",
            "oranges",
            "reds",
            "ylorbr",
            "ylorrd",
            "orrd",
            "purd",
            "rdpu",
            "bupu",
            "gnbu",
            "pubu",
            "ylgnbu",
            "pubugn",
            "bugn",
            "ylgn",
            "binary",
            "gray",
            "bone",
            "pink",
            "spring",
            "summer",
            "autumn",
            "winter",
            "cool",
            "wistia",
            "hot",
            "afmhot",
            "gist_heat",
            "copper",
            "piyg",
            "prgn",
            "brbg",
            "puor",
            "rdgy",
            "rdbu",
            "rdylbu",
            "rdylgn",
            "spectral",
            "coolwarm",
            "bwr",
            "seismic",
            "twilight",
            "twilight_shifted",
            "hsv",
            "flag",
            "prism",
            "ocean",
            "gist_earth",
            "terrain",
            "gist_stern",
            "gnuplot",
            "gnuplot2",
            "cmrmap",
            "cubehelix",
            "brg",
            "gist_rainbow",
            "rainbow",
            "jet",
            "nipy_spectral",
            "gist_ncar",
        ]
    ] = None
    color_range: Optional[ColorRange] = None
    linear_rescaling_factor: Optional[List[float]] = None
    non_linear_rescaling: Optional[bool] = None
    gamma_contrast_factor: Optional[float] = None
    sigmoidal_contrast_factor: Optional[float] = None
    sigmoidal_bias_factor: Optional[float] = None
    saturation_value: Optional[float] = None
    filter_enabled: Optional[bool] = None
    filter_range: Optional[List[float]] = None
    opacity: Optional[float] = None
    single_band_name: Optional[str] = None
    enable_terrain: Optional[bool] = None

    def to_json(self) -> dict:
        result: dict = {}
        glom.assign(result, "type", "rasterTile")
        glom.assign(result, "config.dataId", self.data_id, dict)
        glom.assign(result, "id", self.id, dict)
        glom.assign(result, "config.label", self.label, dict)
        glom.assign(
            result, "config.color", self.color.to_json() if self.color else None, dict
        )
        glom.assign(result, "config.isVisible", self.is_visible, dict)
        glom.assign(result, "config.hidden", self.hidden, dict)
        if self.include_legend is not None:
            glom.assign(result, "config.legend.isIncluded", self.include_legend, dict)
        glom.assign(result, "config.visConfig.preset", self.preset, dict)
        glom.assign(result, "config.visConfig.mosaicId", self.mosaic_id, dict)
        glom.assign(
            result, "config.visConfig.useSTACSearching", self.use_stac_searching, dict
        )
        glom.assign(
            result,
            "config.visConfig.stacSearchProvider",
            self.stac_search_provider,
            dict,
        )
        glom.assign(result, "config.visConfig.startDate", self.start_date, dict)
        glom.assign(result, "config.visConfig.endDate", self.end_date, dict)
        glom.assign(result, "config.visConfig.dynamicColor", self.dynamic_color, dict)
        glom.assign(result, "config.visConfig.colormapId", self.color_map_id, dict)
        glom.assign(
            result,
            "config.visConfig.colorRange",
            self.color_range.to_json() if self.color_range else None,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.linearRescalingFactor",
            self.linear_rescaling_factor,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.nonLinearRescaling",
            self.non_linear_rescaling,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.gammaContrastFactor",
            self.gamma_contrast_factor,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.sigmoidalContrastFactor",
            self.sigmoidal_contrast_factor,
            dict,
        )
        glom.assign(
            result,
            "config.visConfig.sigmoidalBiasFactor",
            self.sigmoidal_bias_factor,
            dict,
        )
        glom.assign(
            result, "config.visConfig.saturationValue", self.saturation_value, dict
        )
        glom.assign(result, "config.visConfig.filterEnabled", self.filter_enabled, dict)
        glom.assign(result, "config.visConfig.filterRange", self.filter_range, dict)
        glom.assign(result, "config.visConfig.opacity", self.opacity, dict)
        glom.assign(
            result, "config.visConfig.singleBandName", self.single_band_name, dict
        )
        glom.assign(result, "config.visConfig.enableTerrain", self.enable_terrain, dict)
        return remove_none_values(result)

    @staticmethod
    def from_json(json: dict) -> "RasterLayer":
        assert json["type"] == "rasterTile", "Layer 'type' is not 'rasterTile'"
        obj = RasterLayer(data_id=glom.glom(json, "config.dataId"))
        obj.id = glom.glom(json, "id", default=None)
        obj.label = glom.glom(json, "config.label", default=None)
        __color = glom.glom(json, "config.color", default=None)
        obj.color = Color.from_json(__color) if __color else None
        obj.is_visible = glom.glom(json, "config.isVisible", default=None)
        obj.hidden = glom.glom(json, "config.hidden", default=None)
        obj.include_legend = glom.glom(json, "config.legend.isIncluded", default=None)
        obj.preset = glom.glom(json, "config.visConfig.preset", default=None)
        obj.mosaic_id = glom.glom(json, "config.visConfig.mosaicId", default=None)
        obj.use_stac_searching = glom.glom(
            json, "config.visConfig.useSTACSearching", default=None
        )
        obj.stac_search_provider = glom.glom(
            json, "config.visConfig.stacSearchProvider", default=None
        )
        obj.start_date = glom.glom(json, "config.visConfig.startDate", default=None)
        obj.end_date = glom.glom(json, "config.visConfig.endDate", default=None)
        obj.dynamic_color = glom.glom(
            json, "config.visConfig.dynamicColor", default=None
        )
        obj.color_map_id = glom.glom(json, "config.visConfig.colormapId", default=None)
        __color_range = glom.glom(json, "config.visConfig.colorRange", default=None)
        obj.color_range = ColorRange.from_json(__color_range) if __color_range else None
        obj.linear_rescaling_factor = glom.glom(
            json, "config.visConfig.linearRescalingFactor", default=None
        )
        obj.non_linear_rescaling = glom.glom(
            json, "config.visConfig.nonLinearRescaling", default=None
        )
        obj.gamma_contrast_factor = glom.glom(
            json, "config.visConfig.gammaContrastFactor", default=None
        )
        obj.sigmoidal_contrast_factor = glom.glom(
            json, "config.visConfig.sigmoidalContrastFactor", default=None
        )
        obj.sigmoidal_bias_factor = glom.glom(
            json, "config.visConfig.sigmoidalBiasFactor", default=None
        )
        obj.saturation_value = glom.glom(
            json, "config.visConfig.saturationValue", default=None
        )
        obj.filter_enabled = glom.glom(
            json, "config.visConfig.filterEnabled", default=None
        )
        obj.filter_range = glom.glom(json, "config.visConfig.filterRange", default=None)
        obj.opacity = glom.glom(json, "config.visConfig.opacity", default=None)
        obj.single_band_name = glom.glom(
            json, "config.visConfig.singleBandName", default=None
        )
        obj.enable_terrain = glom.glom(
            json, "config.visConfig.enableTerrain", default=None
        )
        return obj

    def clone(self) -> "RasterLayer":
        return replace(self)
