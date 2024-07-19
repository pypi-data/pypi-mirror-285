import json
from typing import Any, Callable, Dict, List, Literal, Optional, Union, cast

from pydantic import Field, StrictBool, StrictStr

from foursquare.map_sdk.api.base import (
    Action,
    CamelCaseBaseModel,
    Number,
    Range,
    TimeRange,
)
from foursquare.map_sdk.api.enums import ActionType, FilterType
from foursquare.map_sdk.transport.base import (
    BaseInteractiveTransport,
    BaseNonInteractiveTransport,
    BaseTransport,
)


class PartialFilterSource(CamelCaseBaseModel):
    """Partially defined filter source where the datasetId can be left out."""

    data_id: Optional[StrictStr] = None
    """Identifier of the dataset that the filter applies to."""

    field_name: StrictStr
    """Field name to filter by.
    The field name can be retrieved as part of the dataset record.
    """


class FilterSource(PartialFilterSource):
    """Source that the filter is applied to."""

    data_id: StrictStr
    """Identifier of the dataset that the filter applies to."""

    field_name: StrictStr
    """Field name to filter by. The field name can be retrieved as part of the dataset record.
    """


class _PartialBaseFilter(CamelCaseBaseModel):
    """Partial version of Filter for Filter creation"""

    id: Optional[StrictStr] = None
    """Unique identifier of the filter."""

    type: FilterType
    """Type of the filter."""

    # Incompatible types in assignment (expression has type "List[_T]", variable has type
    # "List[PartialFilterSource]")  [assignment]
    sources: List[PartialFilterSource] = Field(default_factory=list)
    """ Data source(s) to apply the filter to.
    note: Only TimeRangeFilter currently supports multiple sources.
    The first given source will be used for other filter types.
    """

    value: Any = None
    """Value to filter based on."""


class BaseFilter(_PartialBaseFilter):
    """Type encapsulating common filter properties."""

    id: StrictStr
    # Incompatible types in assignment (expression has type "List[FilterSource]", base class
    # "_PartialBaseFilter" defined the type as "List[PartialFilterSource]")
    sources: List[FilterSource]  # type: ignore[assignment]


class PartialRangeFilter(_PartialBaseFilter):
    """Partial RangeFilter for Filter creation"""

    type: FilterType = FilterType.RANGE
    value: Range


class RangeFilter(BaseFilter):
    """Filter type that filters a range of values."""

    type: FilterType = FilterType.RANGE
    value: Range


class PartialSelectFilter(_PartialBaseFilter):
    """Partial SelectFilter for Filter creation"""

    type: FilterType = FilterType.SELECT
    value: StrictBool


class SelectFilter(BaseFilter):
    """Filter type that filters a range of values."""

    type: FilterType = FilterType.SELECT
    value: StrictBool


class FilterTimelineUpdateProps(CamelCaseBaseModel):
    """A set of properties that can be updated on a timeline."""

    view: Optional[Literal["side", "enlarged", "minified"]] = None
    """Current timeline presentation."""

    time_format: Optional[StrictStr] = None
    """Time format that the timeline is using in day.js supported format.
    https://day.js.org/docs/en/display/format
    """

    timezone: Optional[StrictStr] = None
    """Timezone that the timeline is using in tz format.
    https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    """

    is_animating: Optional[StrictBool] = None
    """Flag indicating whether the timeline is animating or not."""

    animation_speed: Optional[Number] = None
    """Speed at which timeline is animating."""


class FilterTimeline(FilterTimelineUpdateProps):
    """Time range filter properties that encapsulate timeline interaction."""

    view: Literal["side", "enlarged", "minified"]
    """Current timeline presentation."""

    time_format: StrictStr
    """Time format that the timeline is using in day.js supported format.
    https://day.js.org/docs/en/display/format
    """

    timezone: Optional[StrictStr] = None
    """Timezone that the timeline is using in tz format.
    https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    """

    is_animating: StrictBool
    """Flag indicating whether the timeline is animating or not."""

    animation_speed: Number
    """Speed at which timeline is animating."""

    step: Number
    """Minimum animation step size in milliseconds."""


class PartialTimeRangeFilter(_PartialBaseFilter):
    """Partial TimeRangeFilter for Filter creation"""

    type: FilterType = FilterType.TIME_RANGE
    value: TimeRange
    domain: TimeRange
    timeline: FilterTimeline


class TimeRangeFilter(BaseFilter):

    type: FilterType = FilterType.TIME_RANGE
    value: TimeRange
    domain: TimeRange
    timeline: FilterTimeline


class PartialMultiSelectFilter(_PartialBaseFilter):
    """Partial MultiSelectFilter for Filter creation"""

    type: FilterType = FilterType.MULTI_SELECT
    value: List[StrictStr]


class MultiSelectFilter(BaseFilter):
    """Filter type that filters a range of values."""

    type: FilterType = FilterType.MULTI_SELECT
    value: List[StrictStr]


class _FilterTimelineUpdateProps(CamelCaseBaseModel):

    view: Optional[Literal["side", "enlarged", "minified"]] = None
    """Current timeline presentation."""

    time_format: Optional[StrictStr] = None
    """Time format that the timeline is using in day.js supported format.
    https://day.js.org/docs/en/display/format
    """

    timezone: Optional[StrictStr] = None
    """Timezone that the timeline is using in tz format.
    https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    """

    is_animating: Optional[StrictBool] = None
    """Flag indicating whether the timeline is animating or not."""

    animation_speed: Optional[Number] = None
    """Speed at which timeline is animating."""


class FilterEventHandlers(CamelCaseBaseModel):
    on_filter_update: Optional[
        Callable[
            [Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter]], None
        ]
    ] = None


###########
# ACTIONS #
###########


class GetFiltersAction(Action):
    """Action payload sent with `get_filters` calls"""

    type: ActionType = ActionType.GET_FILTERS


class GetFilterByIdAction(Action):
    """Action payload sent with `get_filter_by_id` calls"""

    class Meta(Action.Meta):
        args = ["filter_id"]

    type: ActionType = ActionType.GET_FILTER_BY_ID
    filter_id: StrictStr


class AddFilterAction(Action):
    class Meta(Action.Meta):
        args = ["filter"]

    type: ActionType = ActionType.ADD_FILTER
    filter: Union[
        PartialRangeFilter,
        PartialSelectFilter,
        PartialTimeRangeFilter,
        PartialMultiSelectFilter,
    ]


class UpdateFilterAction(Action):
    class Meta(Action.Meta):
        args = ["filter_id", "values"]

    type: ActionType = ActionType.UPDATE_FILTER
    filter_id: StrictStr
    values: Union[
        PartialRangeFilter,
        PartialSelectFilter,
        PartialTimeRangeFilter,
        PartialMultiSelectFilter,
    ]


class RemoveFilterAction(Action):
    class Meta(Action.Meta):
        args = ["filter_id"]

    type: ActionType = ActionType.REMOVE_FILTER
    filter_id: StrictStr


class UpdateTimelineAction(Action):
    class Meta(Action.Meta):
        args = ["filter_id", "values"]

    type: ActionType = ActionType.UPDATE_TIMELINE
    filter_id: StrictStr
    values: _FilterTimelineUpdateProps


class AddFilterFromConfigAction(Action):
    class Meta(Action.Meta):
        args = ["filter_config"]

    type: ActionType = ActionType.ADD_FILTER_FROM_CONFIG
    filter_config: Dict


###########
# METHODS #
###########


class BaseFilterApiMethods:

    transport: BaseTransport

    def add_filter(
        self,
        # pylint:disable = redefined-builtin
        filter: Union[
            PartialRangeFilter,
            PartialSelectFilter,
            PartialTimeRangeFilter,
            PartialMultiSelectFilter,
            dict,
        ],
    ) -> Optional[Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter]]:
        """Adds a new filter to the map.

        Args:
            filter (Union[
                PartialRangeFilter,
                PartialSelectFilter,
                PartialTimeRangeFilter,
                PartialMultiSelectFilter,
                dict]
            ): The filter to add.

        Returns (widget map only):
            Filter: The filter that was added.
        """
        action = AddFilterAction(filter=filter)

        # Fails mypy because Filter is a Union
        return self.transport.send_action_non_null(action=action, response_class=Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter])  # type: ignore[arg-type]

    def update_filter(
        self,
        filter_id: str,
        values: Union[
            PartialRangeFilter,
            PartialSelectFilter,
            PartialTimeRangeFilter,
            PartialMultiSelectFilter,
            dict,
        ],
    ) -> Optional[Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter]]:
        """Updates an existing filter with given values.

        Args:
            filter_id (str): The id of the filter to update.
            values (Union[
            PartialRangeFilter,
            PartialSelectFilter,
            PartialTimeRangeFilter,
            PartialMultiSelectFilter,
            dict,
        ]): The new filter values.

        Returns (widget map only):
            Filter: The updated filter.
        """
        action = UpdateFilterAction(filter_id=filter_id, values=values)

        # Fails mypy because Filter is a Union
        return self.transport.send_action_non_null(action=action, response_class=Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter])  # type: ignore[arg-type]

    def remove_filter(self, filter_id: str) -> None:
        """Removes a filter from the map.

        Args:
            filter_id (str): The id of the filter to remove.

        Returns:
            None
        """
        action = RemoveFilterAction(filter_id=filter_id)
        self.transport.send_action(action=action, response_class=None)

    def update_timeline(
        self,
        filter_id: str,
        values: Union[FilterTimelineUpdateProps, dict],
    ) -> Optional[TimeRangeFilter]:
        """Updates a time range filter timeline with given values.

        Args:
            filter_id (str): The id of the time range filter to update.
            values (Union[FilterTimelineUpdateProps, dict]): The new timeline values.

        Returns (widget map only):
            TimeRangeFilter: The updated time range filter.
        """
        action = UpdateTimelineAction(filter_id=filter_id, values=values)

        return self.transport.send_action_non_null(
            action=action, response_class=TimeRangeFilter
        )

    def add_filter_from_config(
        self, filter_config: Union[Dict, str]
    ) -> Optional[Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter]]:
        """Adds a new filter based on its JSON config.

        Args:
            filter_config (Union[Dict, str]): The config of the filter to add

        Returns (widget map only):
            Filter: The filter that was added.
        """

        if isinstance(filter_config, str):
            filter_config = json.loads(filter_config)

        action = AddFilterFromConfigAction(filter_config=filter_config)
        return self.transport.send_action_non_null(action=action, response_class=Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter])  # type: ignore[arg-type]


class BaseInteractiveFilterApiMethods:

    transport: BaseInteractiveTransport

    def get_filters(
        self,
    ) -> List[Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter]]:
        """Gets all the filters currently available in the map.

        Returns:
            List[Filter]: An array of filters.
        """
        action = GetFiltersAction()
        return self.transport.send_action_non_null(
            action=action,
            response_class=List[
                Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter]
            ],
        )

    def get_filter_by_id(
        self, filter_id: str
    ) -> Optional[Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter]]:
        """Retrieves a filter by its identifier if it exists.

        Args:
            filter_id (str): Identifier of the filter to get.

        Returns:
            Optional[Filter]: Filter with a given identifier, or None if one doesn't exist.
        """
        action = GetFilterByIdAction(filter_id=filter_id)

        # Fails mypy because Filter is a Union
        return self.transport.send_action(action=action, response_class=Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter])  # type: ignore[arg-type]


class FilterApiNonInteractiveMixin(BaseFilterApiMethods):
    """Filter methods that are supported in non-interactive (i.e. pure HTML) maps"""

    transport: BaseNonInteractiveTransport

    def add_filter(
        self,
        # pylint:disable = redefined-builtin
        filter: Union[
            PartialRangeFilter,
            PartialSelectFilter,
            PartialTimeRangeFilter,
            PartialMultiSelectFilter,
            dict,
        ],
    ) -> None:
        super().add_filter(filter=filter)
        return

    def update_filter(
        self,
        filter_id: str,
        values: Union[
            PartialRangeFilter,
            PartialSelectFilter,
            PartialTimeRangeFilter,
            PartialMultiSelectFilter,
            dict,
        ],
    ) -> None:
        super().update_filter(filter_id=filter_id, values=values)
        return

    def update_timeline(
        self,
        filter_id: str,
        values: Union[FilterTimelineUpdateProps, dict],
    ) -> None:
        super().update_timeline(filter_id=filter_id, values=values)
        return

    def add_filter_from_config(self, filter_config: Union[Dict, str]) -> None:
        super().add_filter_from_config(filter_config=filter_config)
        return


class FilterApiInteractiveMixin(BaseFilterApiMethods, BaseInteractiveFilterApiMethods):

    transport: BaseInteractiveTransport

    def add_filter(
        self,
        # pylint:disable = redefined-builtin
        filter: Union[
            PartialRangeFilter,
            PartialSelectFilter,
            PartialTimeRangeFilter,
            PartialMultiSelectFilter,
            dict,
        ],
    ) -> Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter]:
        return cast(
            Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter],
            super().add_filter(filter=filter),
        )

    def update_filter(
        self,
        filter_id: str,
        values: Union[
            PartialRangeFilter,
            PartialSelectFilter,
            PartialTimeRangeFilter,
            PartialMultiSelectFilter,
            dict,
        ],
    ) -> Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter]:
        return cast(
            Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter],
            super().update_filter(filter_id=filter_id, values=values),
        )

    def update_timeline(
        self,
        filter_id: str,
        values: Union[FilterTimelineUpdateProps, dict],
    ) -> TimeRangeFilter:
        return cast(
            TimeRangeFilter, super().update_timeline(filter_id=filter_id, values=values)
        )

    def add_filter_from_config(
        self, filter_config: Union[Dict, str]
    ) -> Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter]:
        return cast(
            Union[RangeFilter, SelectFilter, TimeRangeFilter, MultiSelectFilter],
            super().add_filter_from_config(filter_config=filter_config),
        )
