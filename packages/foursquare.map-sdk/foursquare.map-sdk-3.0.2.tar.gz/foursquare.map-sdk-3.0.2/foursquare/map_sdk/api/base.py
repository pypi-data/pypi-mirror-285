from typing import List, Tuple, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt

from foursquare.map_sdk.api.enums import ActionType

Number = Union[StrictFloat, StrictInt]
Range = Tuple[Number, Number]
TimeRange = Tuple[Number, Number]

RGBColor = Tuple[Number, Number, Number]
"""Red, green and blue channels of a color in [0-255] range."""


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case string to camelCase
    https://stackoverflow.com/a/19053800
    """
    components = snake_str.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + "".join(x.title() for x in components[1:])


def snake_to_kebab(snake_str: str) -> str:
    return snake_str.replace("_", "-")


def remove_none_values(d):
    if isinstance(d, dict):
        return {k: remove_none_values(v) for k, v in d.items() if v is not None}
    elif isinstance(d, list):
        return [remove_none_values(elem) for elem in d if elem is not None]
    else:
        return d


def generate_uuid() -> str:
    return str(uuid4())


class ApiBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True, extra="forbid", populate_by_name=True
    )


class CamelCaseBaseModel(ApiBaseModel):
    model_config = ConfigDict(alias_generator=snake_to_camel)


class KebabCaseBaseModel(ApiBaseModel):
    model_config = ConfigDict(alias_generator=snake_to_kebab)


class Action(CamelCaseBaseModel):
    """Base Action payload class"""

    class Meta:
        args: List[str] = []
        """Order in which arguments should be serialized"""

        options: List[str] = []
        """Fields to be collected into an options dict/object."""

    type: ActionType
    message_id: UUID = Field(default_factory=uuid4)
