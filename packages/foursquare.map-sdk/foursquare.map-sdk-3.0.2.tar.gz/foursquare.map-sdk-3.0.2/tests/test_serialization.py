from pydantic import TypeAdapter

from foursquare.map_sdk.api.dataset_api import (
    Dataset,
    LocalDataset,
    RasterTileDataset,
    RasterTileLocalItemMetadata,
    VectorTileDataset,
    VectorTileLocalMetadata,
)
from foursquare.map_sdk.api.enums import ActionType
from foursquare.map_sdk.utils.serialization import FUNCTION_MAPPING

from .fixtures.dataset_api import (
    LOCAL_RESPONSE,
    RASTER_TILE_RESPONSE,
    VECTOR_TILE_RESPONSE,
)


class TestDataset:
    """Tests relating to dataset serialization/deserialization"""

    def test_deserialize(self):

        local_dataset = TypeAdapter(Dataset).validate_python(LOCAL_RESPONSE)
        assert isinstance(local_dataset, LocalDataset)

        vector_tile_dataset = TypeAdapter(Dataset).validate_python(VECTOR_TILE_RESPONSE)
        assert isinstance(vector_tile_dataset, VectorTileDataset)
        assert isinstance(vector_tile_dataset.metadata, VectorTileLocalMetadata)

        raster_tile_dataset = TypeAdapter(Dataset).validate_python(RASTER_TILE_RESPONSE)
        assert isinstance(raster_tile_dataset, RasterTileDataset)
        assert isinstance(raster_tile_dataset.metadata, RasterTileLocalItemMetadata)


class TestFunctionMapping:
    """Tests relating to the function mapping we maintain for the HTML map"""

    def test_function_mapping(self):

        for key in ActionType:
            # Event handler actions are not translated to Javascript
            if key not in [
                ActionType.SET_EVENT_HANDLERS,
                ActionType.REMOVE_EVENT_HANDLERS,
            ]:
                assert key in FUNCTION_MAPPING
