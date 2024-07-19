# type: ignore

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, confloat


class CustomMapState(BaseModel):
    latitude: confloat(ge=-90.0, le=90.0)
    longitude: confloat(ge=-180.0, le=180.0)
    zoom: Optional[confloat(ge=0.0, le=25.0)] = 0
    bearing: Optional[float] = 0
    pitch: confloat(ge=0.0, lt=90.0)
