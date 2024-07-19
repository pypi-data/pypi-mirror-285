# type: ignore

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class AnimationWindow(Enum):
    free = "free"
    incremental = "incremental"
    point = "point"
    interval = "interval"


class SyncTimelineMode(Enum):
    number_0 = 0
    number_1 = 1


class FilterAnimation(BaseModel):
    data_id: List[str] = Field(
        ..., alias="dataId", description="Dataset ids that this filter applies to"
    )
    value: Optional[List[float]] = Field(..., description="Range of the filter")
    animation_window: Optional[AnimationWindow] = Field(
        "free", alias="animationWindow", description="Animation window type"
    )
    speed: Optional[float] = Field(1, description="Speed of the animation")
    synced_with_layer_timeline: Optional[bool] = Field(
        None,
        alias="syncedWithLayerTimeline",
        description="Whether the filter should be synced with the layer timeline",
    )
    sync_timeline_mode: Optional[SyncTimelineMode] = Field(
        None,
        alias="syncTimelineMode",
        description="Sync timeline mode: 0 (sync with range start) or 1 (sync with range end)",
    )
    timezone: Optional[str] = Field(
        None,
        description="Timezone (TZ identifier) for displaying time, e.g. America/New_York",
    )
