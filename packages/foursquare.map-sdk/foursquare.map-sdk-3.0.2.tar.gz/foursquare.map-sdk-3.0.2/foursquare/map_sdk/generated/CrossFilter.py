# type: ignore

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Union

from pydantic import BaseModel, Field, RootModel


class SelectionMode(Enum):
    cell = "cell"
    row = "row"
    column = "column"
    row_column = "rowColumn"


class Signals(BaseModel):
    type: Literal["filter"]
    dataset_id: str = Field(
        ...,
        alias="datasetId",
        description="The ID of the *other* dataset that should be cross-filtered.",
    )
    field_names: Dict[str, str] = Field(
        ..., alias="fieldNames", description="The field names in a filter."
    )


class Signals1(BaseModel):
    type: Literal["parameter"]
    dataset_id: str = Field(
        ...,
        alias="datasetId",
        description="The ID of the *other* dataset that should be cross-filtered.",
    )
    parameter_keys: Dict[str, str] = Field(
        ...,
        alias="parameterKeys",
        description="The dynamic parameter key names in a SQL dataset",
    )


class CrossFilter1(BaseModel):
    enabled: bool
    selection_mode: SelectionMode = Field(..., alias="selectionMode")
    value: Dict[str, Union[float, str]] = Field(
        ..., description="The selected values of the originating cross filter."
    )
    signals: List[Union[Signals, Signals1]]
    type: Literal["heatmapChart"]


class CrossFilter(RootModel[CrossFilter1]):
    root: CrossFilter1 = Field(..., title="CrossFilter")
