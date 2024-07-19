import json
import re
from typing import Any, Dict, List, Literal, Optional, Union, cast

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import geopandas as gpd
except ImportError:
    gpd = None

from pydantic import (
    AnyHttpUrl,
    ConfigDict,
    Field,
    PlainSerializer,
    StrictStr,
    field_validator,
    model_validator,
)
from typing_extensions import Annotated

from foursquare.map_sdk.api.base import Action, CamelCaseBaseModel, Number, RGBColor
from foursquare.map_sdk.api.enums import (
    ActionType,
    BasicFieldType,
    DatasetType,
    FieldType,
    TimestampFieldType,
    VectorTileAttributeType,
)
from foursquare.map_sdk.transport.base import (
    BaseInteractiveTransport,
    BaseNonInteractiveTransport,
    BaseTransport,
)


class BaseField(CamelCaseBaseModel):

    name: StrictStr
    """Unique identifier of the field."""

    label: StrictStr
    """User facing field label."""

    type: FieldType
    """Type of the field."""


class BasicField(BaseField):
    """Contains semantics around a single field in a dataset table."""

    type: BasicFieldType


class TimestampField(BaseField):
    """Contains semantics around a single timestamp field in a dataset table."""

    type: TimestampFieldType = TimestampFieldType.TIMESTAMP
    time_format: StrictStr
    """moment.js time format of this field data."""


class BaseDataset(CamelCaseBaseModel):

    id: StrictStr
    """Unique identifier of the dataset."""

    type: DatasetType
    """Type of dataset."""

    label: StrictStr
    """Displayable dataset label."""

    color: RGBColor
    """Color label of the dataset."""

    fields: List[Union[BasicField, TimestampField]]
    """Schema describing the fields of the dataset."""


class LocalDataset(BaseDataset):
    """Dataset record representing a local dataset, with data provided by the caller."""

    type: DatasetType = DatasetType.LOCAL


class DatasetWithData(LocalDataset):

    data: List[List[Any]] = Field(..., repr=False)
    """Tabular data backing the dataset, where the order of fields matches the order in `Dataset.fields`."""


class VectorTileBaseMetadata(CamelCaseBaseModel):
    """Vector tileset base metadata."""

    model_config = ConfigDict(extra="ignore")

    data_url: AnyHttpUrl
    """URL template for tiles, with {x}/{y}/{z} placeholders"""


class _VectorAttributes(CamelCaseBaseModel):
    """Attributes of a Vector layer."""

    model_config = ConfigDict(extra="ignore")

    attribute: StrictStr
    """The name of this attribute."""

    type: VectorTileAttributeType
    """The type of this attribute's values."""

    min: Optional[Number] = None
    """The minimum value of this attribute (if numeric)."""

    max: Optional[Number] = None
    """The maximum value of this attribute (if numeric)."""


class VectorTileLayer(CamelCaseBaseModel):
    """Layer attribute of the Vector TileJSON."""

    model_config = ConfigDict(extra="ignore")

    attributes: List[_VectorAttributes]
    """Attributes in the layer."""


class VectorTilestats(CamelCaseBaseModel):
    """Tilestats attribute of the Vector TileJSON."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(num_layers={len(self.layers)})"

    model_config = ConfigDict(extra="ignore")

    layers: List[VectorTileLayer]
    """Layers in the tileset."""


class VectorTileEmbeddedMetadata(CamelCaseBaseModel):
    """Minimal shape for the embedded JSON metadata in a Tippecanoe vector
    tileset metadata file.
    """

    model_config = ConfigDict(extra="ignore")

    tilestats: VectorTilestats
    """The tilestats for this tileset."""


class VectorTileLocalMetadata(VectorTileBaseMetadata):
    """Vector tileset metadata, following the metadata format generated
    by Tippecanoe. This metadata shape can be passed to the
    map to synchronously add a vector tileset.
    see https://github.com/mapbox/tippecanoe
    """

    # JSON metadata has multiple names in different contexts
    # maxzoom and minzoom are returned by studio in camelCase
    @model_validator(mode="before")
    @classmethod
    # pylint:disable=no-self-argument
    def allow_alternate_aliases(cls, values):
        if not values.get("json"):
            values["json"] = values.get("metaJson")

        if not values.get("maxzoom"):
            values["maxzoom"] = values.get("maxZoom")

        if not values.get("minzoom"):
            values["minzoom"] = values.get("minZoom")

        return values

    metadata_url: Optional[AnyHttpUrl] = None
    """URL for tileset metadata."""

    bounds: Optional[Union[StrictStr, List[Number]]] = None
    """Tileset bounds, as an array or comma-delimited string in format "w,s,e,n"."""

    center: Optional[Union[StrictStr, List[Number]]] = None
    """Tileset center, as an array or comma-delimited string in format "lng,lat"."""

    maxzoom: Optional[Number] = None
    """Maximum zoom supported by the tileset."""

    minzoom: Optional[Number] = None
    """Minimum zoom supported by the tileset."""

    metadata_json: Union[StrictStr, VectorTileEmbeddedMetadata, None] = Field(
        ..., alias="json"
    )
    """Metadata for the tileset, as a JSON string or object."""


class VectorTileRemoteMetadata(VectorTileBaseMetadata):
    """Vector tileset metadata with a remote metadata URL. The remote metadata file
    should follow the metadata format generated by Tippecanoe. This metadata can
    be passed to the map to asynchronously load a vector tileset.
    see https://github.com/mapbox/tippecanoe
    """

    metadata_url: AnyHttpUrl
    """URL for tileset metadata."""


VectorTileMetadata = Union[VectorTileLocalMetadata, VectorTileRemoteMetadata]


class VectorTileDataset(BaseDataset):
    """Dataset record representing a vector tileset."""

    type: DatasetType = DatasetType.VECTOR_TILE

    metadata: VectorTileMetadata = Field(..., union_mode="left_to_right")
    """Metadata about the vector tileset."""


class RasterTileBaseMetadata(CamelCaseBaseModel):
    """Raster tileset base metadata."""

    model_config = ConfigDict(extra="allow")


class RasterTileLocalItemMetadata(RasterTileBaseMetadata):
    """Raster tileset metadata in STAC Item format. STAC version must be >= 1.0.0,
    and the EO and Raster STAC extensions are required. This metadata shape can
    be passed to the map to synchronously add a raster tileset.
    see https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md
    """

    # pylint:disable=no-self-argument

    type: Literal["Feature"]
    """Type of the raster tileset."""

    stac_version: StrictStr = Field(..., alias="stac_version")
    """STAC version for tileset."""

    stac_extensions: List[StrictStr] = Field(..., alias="stac_extensions")
    """A list of extensions the Item implements."""

    assets: Dict[StrictStr, Any]
    """Dictionary of asset objects that can be downloaded, each with a unique key."""

    @field_validator("stac_version")
    @classmethod
    def validate_stac_version(cls, v: str):
        if v[0] == "0":
            raise ValueError("stac_version must be 1.0 or higher")

        return v

    @field_validator("stac_extensions")
    @classmethod
    def validate_stac_extensions(cls, v: List[str]):
        extension_regex = (
            r"https://stac-extensions.github.io/{ext}/v1\.\d\.\d/schema\.json"
        )
        if not any(re.match(extension_regex.format(ext="eo"), s) for s in v):
            raise ValueError("STAC eo extension, 1.0 or higher, is required")

        if not any(re.match(extension_regex.format(ext="raster"), s) for s in v):
            raise ValueError("STAC raster extension, 1.0 or higher, is required")

        return v


class RasterTileLocalCollectionMetadata(RasterTileBaseMetadata):
    # pylint:disable=no-self-argument

    type: Literal["Collection"]

    stac_version: StrictStr = Field(..., alias="stac_version")
    """STAC version for tileset."""

    stac_extensions: List[StrictStr] = Field(..., alias="stac_extensions")
    """A list of extensions the Item implements."""

    item_assets: Dict[StrictStr, Any] = Field(..., alias="item_assets")
    """Dictionary of asset objects that items in the collection expose, each with a unique key."""

    @field_validator("stac_version")
    @classmethod
    def validate_stac_version(cls, v: str):
        if v[0] == "0":
            raise ValueError("stac_version must be 1.0 or higher")

        return v

    @field_validator("stac_extensions")
    @classmethod
    def validate_stac_extensions(cls, v: List[str]):
        extension_regex = (
            r"https://stac-extensions.github.io/{ext}/v1\.\d\.\d/schema\.json"
        )
        if not any(re.match(extension_regex.format(ext="eo"), s) for s in v):
            raise ValueError("STAC eo extension, 1.0 or higher, is required")

        if not any(re.match(extension_regex.format(ext="raster"), s) for s in v):
            raise ValueError("STAC raster extension, 1.0 or higher, is required")

        if not any(re.match(extension_regex.format(ext="item-assets"), s) for s in v):
            raise ValueError("STAC item-assets extension, 1.0 or higher, is required")

        return v


class RasterTileRemoteMetadata(RasterTileBaseMetadata):
    """Raster tileset metadata with a remote metadata URL. This metadata can
    be passed to the map to asynchronously load a raster tileset.
    """

    metadata_url: AnyHttpUrl
    """URL for tileset metadata."""


RasterTileMetadata = Union[
    Union[RasterTileLocalItemMetadata, RasterTileLocalCollectionMetadata],
    RasterTileRemoteMetadata,
]


class RasterTileDataset(BaseDataset):
    """Dataset record representing a raster tileset."""

    type: DatasetType = DatasetType.RASTER_TILE

    metadata: RasterTileMetadata = Field(..., union_mode="left_to_right")
    """Metadata about the raster tileset."""


Dataset = Union[LocalDataset, VectorTileDataset, RasterTileDataset]


class _BaseDatasetCreationProps(CamelCaseBaseModel):

    id: Optional[StrictStr] = None
    """Unique identifier of the dataset."""

    type: DatasetType
    """Type of dataset."""

    label: Optional[StrictStr] = None
    """Displayable dataset label."""

    color: Optional[RGBColor] = None
    """Color label of the dataset."""


def serialize_data(
    data: Union[StrictStr, dict, List[List[Any]], "pd.DataFrame", "gpd.GeoDataFrame"]
) -> Union[str, dict, List[List[Any]]]:

    if gpd is not None and isinstance(data, gpd.GeoDataFrame):
        # convert to GeoJSON FeatureCollection
        return json.loads(data.to_json())
    elif pd is not None and isinstance(data, pd.DataFrame):
        # convert to CSV string
        return data.to_csv()
    else:
        return data


class LocalDatasetCreationProps(_BaseDatasetCreationProps):
    """A set of properties used to create a dataset with inline data."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    type: DatasetType = Field(default=DatasetType.LOCAL)

    data: Annotated[
        Union[
            StrictStr, dict, List[List[Any]], Any
        ],  # also supports "pd.DataFrame", "gpd.GeoDataFrame"
        PlainSerializer(
            return_type=Union[str, dict, List[List[Any]]], func=serialize_data
        ),
    ]
    """Data used to create a dataset, in CSV, JSON, GeoJSON format."""


class VectorTileDatasetCreationProps(_BaseDatasetCreationProps):
    """A set of properties used to create a vector tile dataset with provided metadata."""

    type: DatasetType = DatasetType.VECTOR_TILE

    metadata: VectorTileLocalMetadata
    """Metadata about the vector tileset."""


class VectorTileDatasetRemoteCreationProps(_BaseDatasetCreationProps):
    """A set of properties used to create a vector tile dataset with remote metadata."""

    type: DatasetType = DatasetType.VECTOR_TILE

    metadata: VectorTileRemoteMetadata
    """Metadata about the vector tileset."""


class RasterTileDatasetCreationProps(_BaseDatasetCreationProps):
    """A set of properties used to create a raster tile dataset with provided metadata."""

    type: DatasetType = DatasetType.RASTER_TILE

    metadata: Union[RasterTileLocalItemMetadata, RasterTileLocalCollectionMetadata]
    """Metadata about the raster tileset."""


class RasterTileDatasetRemoteCreationProps(_BaseDatasetCreationProps):
    """A set of properties used to create a raster tile dataset with remote metadata."""

    type: DatasetType = DatasetType.RASTER_TILE

    metadata: RasterTileRemoteMetadata
    """Metadata about the raster tileset."""


class DatasetUpdateProps(CamelCaseBaseModel):
    """A set of properties used to update a dataset."""

    label: Optional[StrictStr] = None
    """Displayable dataset label."""

    color: Optional[RGBColor] = None
    """Color label of the dataset."""


#########
# UTILS #
#########


def normalize_dataset(
    dataset: Union[
        LocalDatasetCreationProps,
        RasterTileDatasetCreationProps,
        VectorTileDatasetCreationProps,
        VectorTileDatasetRemoteCreationProps,
        RasterTileDatasetRemoteCreationProps,
        Dict,
    ],
    fields_to_exclude: Optional[List[str]] = None,
) -> Dict:
    # convert to dict to make transformations
    if isinstance(dataset, _BaseDatasetCreationProps):
        dataset_dict = dataset.model_dump(mode="json", exclude_none=True)
    elif isinstance(dataset, dict):
        dataset_dict = dataset

    if fields_to_exclude:
        for field in fields_to_exclude:
            if field in dataset_dict:
                del dataset_dict[field]

    return dataset_dict


###########
# ACTIONS #
###########


class GetDatasetsAction(Action):
    """Action payload sent with `get_datasets` calls"""

    type: ActionType = ActionType.GET_DATASETS


class GetDatasetByIdAction(Action):
    """Action payload sent with `get_dataset_by_id` calls"""

    class Meta(Action.Meta):
        args = ["dataset_id"]

    type: ActionType = ActionType.GET_DATASET_BY_ID
    dataset_id: StrictStr


class AddDatasetAction(Action):
    """Action payload sent with `add_dataset` calls"""

    class Meta(Action.Meta):
        args = ["dataset"]
        options = ["auto_create_layers", "center_map"]

    type: ActionType = ActionType.ADD_DATASET
    dataset: Union[
        LocalDatasetCreationProps,
        VectorTileDatasetCreationProps,
        RasterTileDatasetCreationProps,
    ]
    auto_create_layers: bool
    center_map: bool


class AddTileDatasetAction(Action):
    """Action payload sent with `add_tile_dataset` calls"""

    class Meta(Action.Meta):
        args = ["dataset"]
        options = ["auto_create_layers", "center_map"]

    type: ActionType = ActionType.ADD_TILE_DATASET
    dataset: Union[
        VectorTileDatasetRemoteCreationProps, RasterTileDatasetRemoteCreationProps
    ]
    auto_create_layers: bool
    center_map: bool


class UpdateDatasetAction(Action):
    """Action payload sent with `update_dataset` calls"""

    class Meta(Action.Meta):
        args = ["dataset_id", "values"]

    type: ActionType = ActionType.UPDATE_DATASET
    dataset_id: StrictStr
    values: DatasetUpdateProps


class RemoveDatasetAction(Action):
    """Action payload sent with `remove_dataset` calls"""

    class Meta(Action.Meta):
        args = ["dataset_id"]

    type: ActionType = ActionType.REMOVE_DATASET
    dataset_id: StrictStr


class ReplaceDatasetAction(Action):
    """Action payload sent with `replace_dataset` calls"""

    class Meta(Action.Meta):
        args = ["this_dataset_id", "with_dataset"]
        options = ["force", "strict"]

    type: ActionType = ActionType.REPLACE_DATASET
    this_dataset_id: StrictStr
    with_dataset: Union[
        LocalDatasetCreationProps,
        VectorTileDatasetCreationProps,
        RasterTileDatasetCreationProps,
    ]
    force: bool
    strict: bool


class GetDatasetWithDataAction(Action):
    """Action payload sent with `get_dataset_with_data` calls"""

    class Meta(Action.Meta):
        args = ["dataset_id"]

    type: ActionType = ActionType.GET_DATASET_WITH_DATA
    dataset_id: StrictStr


###########
# METHODS #
###########


class BaseDatasetApiMethods:

    transport: BaseTransport

    def add_dataset(
        self,
        dataset: Union[
            LocalDatasetCreationProps,
            RasterTileDatasetCreationProps,
            VectorTileDatasetCreationProps,
            Dict,
        ],
        *,
        auto_create_layers: bool = True,
        center_map: bool = True,
    ) -> Optional[Dataset]:
        """Adds a new dataset to the map.

        Args:
            dataset (Union[
                LocalDatasetCreationProps,
                RasterTileDatasetCreationProps,
                VectorTileDatasetCreationProps,
                Dict
            ]):
                The dataset or dataset metadata which to add to the map.

        Kwargs:
            auto_create_layers (bool):
                Whether to attempt and create new layer(s) when adding a dataset. Defaults to True.
            center_map (bool):
                Whether to center the map to fit the new layer bounds. Defaults to True.

        Returns (widget map only):
            Dataset: The newly created dataset.
        """

        dataset = normalize_dataset(dataset, ["fields"])

        action = AddDatasetAction(
            dataset=dataset,
            auto_create_layers=auto_create_layers,
            center_map=center_map,
        )
        return self.transport.send_action_non_null(
            action=action, response_class=Dataset  # type: ignore[arg-type]
        )

    def add_tile_dataset(
        self,
        dataset: Union[
            VectorTileDatasetRemoteCreationProps,
            RasterTileDatasetRemoteCreationProps,
            Dict,
        ],
        *,
        auto_create_layers: bool = True,
        center_map: bool = True,
    ) -> Optional[Dataset]:
        """Adds a new dataset to the map.

        Args:
            dataset (Union[
                VectorTileDatasetRemoteCreationProps,
                RasterTileDatasetRemoteCreationProps,
                Dict
            ]):
                The dataset or dataset metadata which to add to the map.

        Kwargs:
            auto_create_layers (bool):
                Whether to attempt and create new layer(s) when adding a dataset. Defaults to True.
            center_map (bool):
                Whether to center the map to fit the new layer bounds. Defaults to True.

        Returns (widget map only):
            Dataset: The newly created dataset.
        """

        dataset = normalize_dataset(dataset, ["fields"])

        action = AddTileDatasetAction(
            dataset=dataset,
            auto_create_layers=auto_create_layers,
            center_map=center_map,
        )

        # Fails mypy because Dataset is a Union
        return self.transport.send_action_non_null(
            action=action, response_class=Dataset  # type: ignore[arg-type]
        )

    def update_dataset(
        self,
        dataset_id: str,
        values: Union[DatasetUpdateProps, dict],
    ) -> Optional[Dataset]:
        """Updates an existing dataset with given values.

        Args:
            dataset_id (str): The identifier of the dataset to update.
            values (Union[DatasetUpdateProps, dict]):
                A dictionary of the values to update.
                    label (Optional[str]): Displayable dataset label.
                    color: (Optional[Tuple[float, float, float]]): Color label of the dataset

        Returns (widget map only):
            Dataset: Updated dataset record.
        """

        action = UpdateDatasetAction(dataset_id=dataset_id, values=values)

        # Fails mypy because Dataset is a Union
        return self.transport.send_action_non_null(
            action=action, response_class=Dataset  # type: ignore[arg-type]
        )

    def remove_dataset(self, dataset_id: str) -> None:
        """Removes a dataset from the map.

        Args:
            dataset_id (str): The identifier of the dataset to remove.

        Returns:
            None
        """
        action = RemoveDatasetAction(dataset_id=dataset_id)
        self.transport.send_action(action=action, response_class=None)

    def replace_dataset(
        self,
        this_dataset_id: str,
        with_dataset: Union[
            LocalDatasetCreationProps,
            RasterTileDatasetCreationProps,
            VectorTileDatasetCreationProps,
            Dict,
        ],
        *,
        force: bool = False,
        strict: bool = False,
    ) -> Optional[Dataset]:
        """Replaces a given dataset with a new one.

        Args:
            this_dataset_id (str): Identifier of the dataset to replace.
            with_dataset (Union[
                LocalDatasetCreationProps,
                RasterTileDatasetCreationProps,
                VectorTileDatasetCreationProps,
                Dict,
            ]):
                Dataset details to replace the dataset with. Defaults to None.

        Kwargs:
            force (bool): Whether to force a dataset replace, even if the compatibility check fails. Defaults to False.
            strict (bool): Whether to ensure strict equality of types for each field being replaced. Defaults to False.

        Returns (widget map only):
            Dataset: The dataset that's now in use.
        """
        with_dataset = normalize_dataset(with_dataset, ["fields"])

        action = ReplaceDatasetAction(
            this_dataset_id=this_dataset_id,
            with_dataset=with_dataset,
            force=force,
            strict=strict,
        )

        # Fails mypy because Dataset is a Union
        return self.transport.send_action_non_null(
            action=action, response_class=Dataset  # type: ignore[arg-type]
        )


class BaseInteractiveDatasetApiMethods:

    transport: BaseInteractiveTransport

    def get_datasets(self) -> List[Dataset]:
        """Gets all the datasets currently available in the map.

        Returns:
            List[Dataset]: An array of datasets.
        """
        action = GetDatasetsAction()
        return self.transport.send_action_non_null(
            action=action, response_class=List[Dataset]
        )

    def get_dataset_by_id(self, dataset_id: str) -> Optional[Dataset]:
        """Retrieves a dataset by its identifier if it exists.

        Args:
            dataset_id (str): Identifier of the dataset to get.

        Returns:
            Dataset with a given identifier, or None if one doesn't exist.
        """
        action = GetDatasetByIdAction(dataset_id=dataset_id)
        return self.transport.send_action(action=action, response_class=Dataset)  # type: ignore[arg-type]

    def get_dataset_with_data(self, dataset_id: str) -> Optional[DatasetWithData]:
        """Retrieves a dataset record with its data for a given dataset if it exists.

        Args:
            dataset_id (str): Identifier of the dataset to get the record for.

        Returns:
            Dataset record with its data based on an identifier, or None if one doesn't exist.
        """
        action = GetDatasetWithDataAction(dataset_id=dataset_id)
        return self.transport.send_action(action=action, response_class=DatasetWithData)


class DatasetApiNonInteractiveMixin(BaseDatasetApiMethods):
    """Dataset methods that are supported in non-interactive (i.e. pure HTML) maps"""

    transport: BaseNonInteractiveTransport

    def add_dataset(
        self,
        dataset: Union[
            LocalDatasetCreationProps,
            VectorTileDatasetCreationProps,
            RasterTileDatasetCreationProps,
            Dict,
        ],
        *,
        auto_create_layers: bool = True,
        center_map: bool = True,
    ) -> None:
        super().add_dataset(
            dataset=dataset,
            auto_create_layers=auto_create_layers,
            center_map=center_map,
        )
        return

    def add_tile_dataset(
        self,
        dataset: Union[
            VectorTileDatasetRemoteCreationProps,
            RasterTileDatasetRemoteCreationProps,
            Dict,
        ],
        *,
        auto_create_layers: bool = True,
        center_map: bool = True,
    ) -> None:
        super().add_tile_dataset(
            dataset=dataset,
            auto_create_layers=auto_create_layers,
            center_map=center_map,
        )
        return

    def update_dataset(
        self, dataset_id: str, values: Union[DatasetUpdateProps, dict]
    ) -> None:
        super().update_dataset(dataset_id=dataset_id, values=values)
        return

    def replace_dataset(
        self,
        this_dataset_id: str,
        with_dataset: Union[
            LocalDatasetCreationProps,
            RasterTileDatasetCreationProps,
            VectorTileDatasetCreationProps,
            Dict,
        ],
        *,
        force: bool = False,
        strict: bool = False,
    ) -> None:
        super().replace_dataset(
            this_dataset_id=this_dataset_id,
            with_dataset=with_dataset,
            force=force,
            strict=strict,
        )
        return


class DatasetApiInteractiveMixin(
    BaseDatasetApiMethods, BaseInteractiveDatasetApiMethods
):

    transport: BaseInteractiveTransport

    def add_dataset(
        self,
        dataset: Union[
            LocalDatasetCreationProps,
            VectorTileDatasetCreationProps,
            RasterTileDatasetCreationProps,
            Dict,
        ],
        *,
        auto_create_layers: bool = True,
        center_map: bool = True,
    ) -> Dataset:
        return cast(
            Dataset,
            super().add_dataset(
                dataset=dataset,
                auto_create_layers=auto_create_layers,
                center_map=center_map,
            ),
        )

    def add_tile_dataset(
        self,
        dataset: Union[
            VectorTileDatasetRemoteCreationProps,
            RasterTileDatasetRemoteCreationProps,
            Dict,
        ],
        *,
        auto_create_layers: bool = True,
        center_map: bool = True,
    ) -> Dataset:
        return cast(
            Dataset,
            super().add_tile_dataset(
                dataset=dataset,
                auto_create_layers=auto_create_layers,
                center_map=center_map,
            ),
        )

    def update_dataset(
        self,
        dataset_id: str,
        values: Union[DatasetUpdateProps, dict],
    ) -> Dataset:
        return cast(
            Dataset, super().update_dataset(dataset_id=dataset_id, values=values)
        )

    def replace_dataset(
        self,
        this_dataset_id: str,
        with_dataset: Union[
            LocalDatasetCreationProps,
            RasterTileDatasetCreationProps,
            VectorTileDatasetCreationProps,
            Dict,
        ],
        *,
        force: bool = False,
        strict: bool = False,
    ) -> Dataset:
        return cast(
            Dataset,
            super().replace_dataset(
                this_dataset_id=this_dataset_id,
                with_dataset=with_dataset,
                force=force,
                strict=strict,
            ),
        )
