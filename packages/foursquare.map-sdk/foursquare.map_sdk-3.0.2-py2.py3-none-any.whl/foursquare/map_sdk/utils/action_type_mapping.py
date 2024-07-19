from typing import Dict

from foursquare.map_sdk.api.enums import ActionType

# Mapping from message type to MapApi function name for message dispatch
FUNCTION_MAPPING: Dict[ActionType, str] = {
    # Map API
    ActionType.GET_VIEW: "getView",
    ActionType.SET_VIEW: "setView",
    ActionType.GET_VIEW_LIMITS: "getViewLimits",
    ActionType.SET_VIEW_LIMITS: "setViewLimits",
    ActionType.GET_VIEW_MODE: "getViewMode",
    ActionType.SET_VIEW_MODE: "setViewMode",
    ActionType.SET_VIEW_FROM_CONFIG: "setViewFromConfig",
    ActionType.GET_MAP_CONTROL_VISIBILITY: "getMapControlVisibility",
    ActionType.SET_MAP_CONTROL_VISIBILITY: "setMapControlVisibility",
    ActionType.GET_SPLIT_MODE: "getSplitMode",
    ActionType.SET_SPLIT_MODE: "setSplitMode",
    ActionType.GET_MAP_CONFIG: "getMapConfig",
    ActionType.SET_MAP_CONFIG: "setMapConfig",
    ActionType.GET_MAP_STYLES: "getMapStyles",
    ActionType.SET_THEME: "setUiTheme",
    ActionType.SET_ANIMATION_FROM_CONFIG: "setAnimationFromConfig",
    # Filter API
    ActionType.GET_FILTERS: "getFilters",
    ActionType.GET_FILTER_BY_ID: "getFilterById",
    ActionType.ADD_FILTER: "addFilter",
    ActionType.UPDATE_FILTER: "updateFilter",
    ActionType.REMOVE_FILTER: "removeFilter",
    ActionType.UPDATE_TIMELINE: "updateTimeline",
    ActionType.ADD_FILTER_FROM_CONFIG: "addFilterFromConfig",
    # Datasets API
    ActionType.GET_DATASETS: "getDatasets",
    ActionType.GET_DATASET_BY_ID: "getDatasetById",
    ActionType.ADD_DATASET: "addDataset",
    ActionType.ADD_TILE_DATASET: "addTileDataset",
    ActionType.UPDATE_DATASET: "updateDataset",
    ActionType.REMOVE_DATASET: "removeDataset",
    ActionType.REPLACE_DATASET: "replaceDataset",
    ActionType.GET_DATASET_WITH_DATA: "getDatasetWithData",
    # Layer API
    ActionType.GET_LAYERS: "getLayers",
    ActionType.GET_LAYER_BY_ID: "getLayerById",
    ActionType.ADD_LAYER: "addLayer",
    ActionType.ADD_LAYER_FROM_CONFIG: "addLayerFromConfig",
    ActionType.UPDATE_LAYER: "updateLayer",
    ActionType.REMOVE_LAYER: "removeLayer",
    ActionType.GET_LAYER_GROUPS: "getLayerGroups",
    ActionType.GET_LAYER_GROUP_BY_ID: "getLayerGroupById",
    ActionType.ADD_LAYER_GROUP: "addLayerGroup",
    ActionType.UPDATE_LAYER_GROUP: "updateLayerGroup",
    ActionType.REMOVE_LAYER_GROUP: "removeLayerGroup",
    ActionType.GET_LAYER_TIMELINE: "getLayerTimeline",
    ActionType.UPDATE_LAYER_TIMELINE: "updateLayerTimeline",
    # Effect API
    ActionType.GET_EFFECTS: "getEffects",
    ActionType.GET_EFFECT_BY_ID: "getEffectById",
    ActionType.ADD_EFFECT: "addEffect",
    ActionType.UPDATE_EFFECT: "updateEffect",
    ActionType.REMOVE_EFFECT: "removeEffect",
    # Annotation API
    ActionType.GET_ANNOTATIONS: "getAnnotations",
    ActionType.GET_ANNOTATION_BY_ID: "getAnnotationById",
    ActionType.ADD_ANNOTATION: "addAnnotation",
    ActionType.UPDATE_ANNOTATION: "updateAnnotation",
    ActionType.REMOVE_ANNOTATION: "removeAnnotation",
}
