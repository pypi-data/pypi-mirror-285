# type: ignore

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, confloat


class TimeFormat(Enum):
    l = "L"
    l_lt = "L LT"
    l_lts = "L LTS"


class Animation(BaseModel):
    current_time: Optional[float] = Field(
        None,
        alias="currentTime",
        description="The current time of the animation in epoch milliseconds",
    )
    speed: Optional[confloat(ge=0.0, le=10.0)] = Field(
        1, description="The speed of the animation, a number between 0 and 10"
    )
    domain: Optional[List[float]] = Field(
        None,
        description="Override the time domain of the animation (in epoch milliseconds). By default the domain is calculated from the data.",
        max_length=2,
        min_length=2,
    )
    time_format: Optional[TimeFormat] = Field(
        None,
        alias="timeFormat",
        description='The format for displaying the animation time For the syntax check "Locale aware formats" here: https://momentjs.com/docs/#/parsing/string-format/',
    )
    timezone: Optional[str] = Field(
        None,
        description='The timezone for displaying the animation time e.g. "America/New_York"For the list of timezones check here: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones',
    )
