from foursquare.map_sdk.map.widget import SyncWidgetMap
from tests._utils import check_expected_comm_message
from tests.conftest import MockComm


class TestGetEffects:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.get_effects()

        expected = {
            "type": "v1/map-sdk-get-effects",
            "args": [],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestGetEffectById:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.get_effect_by_id(effect_id="effect-id")

        expected = {
            "type": "v1/map-sdk-get-effect-by-id",
            "args": ["effect-id"],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)


class TestAddEffect:
    @property
    def expected(self):
        return {
            "type": "v1/map-sdk-add-effect",
            "args": [
                {
                    "id": "effect-id",
                    "type": "ink",
                    "isEnabled": False,
                    "parameters": {"strength": 0.33},
                }
            ],
        }

    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        effect = {
            "id": "effect-id",
            "type": "ink",
            "is_enabled": False,
            "parameters": {"strength": 0.33},
        }

        mock_widget_map.add_effect(effect=effect)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)


class TestUpdateEffect:
    @property
    def expected(self):
        return {
            "type": "v1/map-sdk-update-effect",
            "args": [
                "effect-id",
                {"parameters": {"strength": 0.22}},
            ],
        }

    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        values = {"parameters": {"strength": 0.22}}
        mock_widget_map.update_effect(effect_id="effect-id", values=values)

        assert check_expected_comm_message(self.expected, mock_comm.log_send)


class TestRemoveEffect:
    def test_widget_message(self, mock_comm: MockComm, mock_widget_map: SyncWidgetMap):
        mock_widget_map.remove_effect(effect_id="effect-id")

        expected = {
            "type": "v1/map-sdk-remove-effect",
            "args": ["effect-id"],
        }

        assert check_expected_comm_message(expected, mock_comm.log_send)
