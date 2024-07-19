from dataclasses import dataclass, field
from typing import Literal, Optional

import glom


@dataclass
class GeojsonColumns:
    """The mapping between data columns and layer properties.

    Columns:
      geojson: str - name of the data column with geojson data
    """

    mode: Literal["geojson"] = field(init=False, default="geojson")
    geojson: str

    def to_json(self) -> dict:
        return {"geojson": self.geojson}

    @staticmethod
    def from_json(json: dict):
        return GeojsonColumns(
            geojson=json["geojson"],
        )


@dataclass
class LatLngAltNborColumns:
    """The mapping between data columns and layer properties.

    Required:
      lat: str - name of the data column with latitude data
      lng: str - name of the data column with longitude data

    Optional:
      alt: str - name of the data column with altitude data
      neighbors: str - name of the data column with neighbors data
    """

    mode: Literal["points"] = field(init=False, default="points")
    lat: str
    lng: str
    alt: Optional[str] = None
    neighbors: Optional[str] = None

    def to_json(self) -> dict:
        return {
            "lat": self.lat,
            "lng": self.lng,
            "altitude": self.alt,
            "neighbors": self.neighbors,
        }

    @staticmethod
    def from_json(json: dict):
        return LatLngAltNborColumns(
            lat=json["lat"],
            lng=json["lng"],
            alt=glom.glom(json, "altitude", default=None),
            neighbors=glom.glom(json, "neighbors", default=None),
        )


@dataclass
class LatLngPairColumns:
    """The mapping between data columns and layer properties.

    Required:
      source_lat: str - name of the data column with source latitude data
      source_lng: str - name of the data column with source longitude data
      target_lat: str - name of the data column with target latitude data
      target_lng: str - name of the data column with target longitude data
    """

    mode: Literal["points"] = field(init=False, default="points")
    source_lat: str
    source_lng: str
    target_lat: str
    target_lng: str

    def to_json(self) -> dict:
        return {
            "lat0": self.source_lat,
            "lng0": self.source_lng,
            "lat1": self.target_lat,
            "lng1": self.target_lng,
        }

    @staticmethod
    def from_json(json: dict):
        return LatLngPairColumns(
            source_lat=json["lat0"],
            source_lng=json["lng0"],
            target_lat=json["lat1"],
            target_lng=json["lng1"],
        )


@dataclass
class NborLatLngAltColumns:
    """The mapping between data columns and layer properties.

    Required:
      neighbors: str - name of the data column with neighbors data
      lat: str - name of the data column with latitude data
      lng: str - name of the data column with longitude data

    Optional:
      alt: str - name of the data column with altitude data
    """

    mode: Literal["neighbors"] = field(init=False, default="neighbors")
    neighbors: str
    lat: str
    lng: str
    alt: Optional[str] = None

    def to_json(self) -> dict:
        return {
            "neighbors": self.neighbors,
            "lat": self.lat,
            "lng": self.lng,
            "altitude": self.alt,
        }

    @staticmethod
    def from_json(json: dict):
        return NborLatLngAltColumns(
            neighbors=json["neighbors"],
            lat=json["lat"],
            lng=json["lng"],
            alt=glom.glom(json, "altitude", default=None),
        )


@dataclass
class NborLatLngColumns:
    """The mapping between data columns and layer properties.

    Required:
      neighbors: str - name of the data column with neighbors data
      lat: str - name of the data column with latitude data
      lng: str - name of the data column with longitude data
    """

    mode: Literal["neighbors"] = field(init=False, default="neighbors")
    neighbors: str
    lat: str
    lng: str

    def to_json(self) -> dict:
        return {
            "neighbors": self.neighbors,
            "lat": self.lat,
            "lng": self.lng,
        }

    @staticmethod
    def from_json(json: dict):
        return NborLatLngAltColumns(
            neighbors=json["neighbors"],
            lat=json["lat"],
            lng=json["lng"],
        )


@dataclass
class LatLngAltPairColumns:
    """The mapping between data columns and layer properties.

    Required:
      source_lat: str - name of the data column with source latitude data
      source_lng: str - name of the data column with source longitude data
      target_lat: str - name of the data column with target latitude data
      target_lng: str - name of the data column with target longitude data

    Optional:
      source_alt: str - name of the data column with source altitude data
      target_alt: str - name of the data column with target altitude data
    """

    mode: Literal["points"] = field(init=False, default="points")
    source_lat: str
    source_lng: str
    target_lat: str
    target_lng: str
    source_alt: Optional[str] = None
    target_alt: Optional[str] = None

    def to_json(self) -> dict:
        return {
            "lat0": self.source_lat,
            "lng0": self.source_lng,
            "lat1": self.target_lat,
            "lng1": self.target_lng,
            "alt0": self.source_alt,
            "alt1": self.target_alt,
        }

    @staticmethod
    def from_json(json: dict):
        return LatLngAltPairColumns(
            source_lat=json["lat0"],
            source_lng=json["lng0"],
            target_lat=json["lat1"],
            target_lng=json["lng1"],
            source_alt=glom.glom(json, "alt0", default=None),
            target_alt=glom.glom(json, "alt1", default=None),
        )


@dataclass
class LatLngColumns:
    """The mapping between data columns and layer properties.

    Required:
      lat: str - name of the data column with latitude data
      lng: str - name of the data column with longitude data
    """

    lat: str
    lng: str


@dataclass
class H3Columns:
    """The mapping between data columns and layer properties.

    Required:
      hex_id: str - name of the data column with H3 data
    """

    hex_id: str


@dataclass
class S2Columns:
    """The mapping between data columns and layer properties.

    Required:
      token: str - name of the data column with H3 data
    """

    token: str


@dataclass
class IdLatLngAltSortbyColumns:
    """The mapping between data columns and layer properties.

    Required:
      id: str - name of the data column with ID data
      lat: str - name of the data column with latitude data
      lng: str - name of the data column with longitude data

    Optional:
      alt: str - name of the data column with altitude data
      sort_by: str - name of the data column with sort filter data
    """

    mode: Literal["polygon"] = field(init=False, default="polygon")
    id: str
    lat: str
    lng: str
    alt: Optional[str] = None
    sort_by: Optional[str] = None

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "lat": self.lat,
            "lng": self.lng,
            "altitude": self.alt,
            "sortBy": self.sort_by,
        }

    @staticmethod
    def from_json(json: dict):
        return IdLatLngAltSortbyColumns(
            id=json["id"],
            lat=json["lat"],
            lng=json["lng"],
            alt=glom.glom(json, "altitude", default=None),
            sort_by=glom.glom(json, "sortBy", default=None),
        )


@dataclass
class IdLatLngAltTimeColumns:
    """The mapping between data columns and layer properties.

    Required:
      id: str - name of the data column with ID data
      lat: str - name of the data column with latitude data
      lng: str - name of the data column with longitude data
      timestamp: str - name of the data column with timestamp data

    Optional:
      alt: str - name of the data column with altitude data
    """

    mode: Literal["table"] = field(init=False, default="table")
    id: str
    lat: str
    lng: str
    timestamp: str
    alt: Optional[str] = None

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "lat": self.lat,
            "lng": self.lng,
            "altitude": self.alt,
            "timestamp": self.timestamp,
        }

    @staticmethod
    def from_json(json: dict):
        return IdLatLngAltTimeColumns(
            id=json["id"],
            lat=json["lat"],
            lng=json["lng"],
            timestamp=json["timestamp"],
            alt=glom.glom(json, "altitude", default=None),
        )


@dataclass
class LatLngIconAltColumns:
    """The mapping between data columns and layer properties.

    Required:
      lat: str - name of the data column with latitude data
      lng: str - name of the data column with longitude data
      icon: str - name of the data column with icon data

    Optional:
      alt: str - name of the data column with altitude data
    """

    lat: str
    lng: str
    icon: str
    alt: Optional[str] = None

    def to_json(self) -> dict:
        return {
            "lat": self.lat,
            "lng": self.lng,
            "icon": self.icon,
            "altitude": self.alt,
        }

    @staticmethod
    def from_json(json: dict):
        return LatLngIconAltColumns(
            lat=json["lat"],
            lng=json["lng"],
            icon=json["icon"],
            alt=glom.glom(json, "altitude", default=None),
        )


@dataclass
class LatLngAltColumns:
    """The mapping between data columns and layer properties.

    Required:
      lat: str - name of the data column with latitude data
      lng: str - name of the data column with longitude data

    Optional:
      alt: str - name of the data column with altitude data
    """

    lat: str
    lng: str
    alt: Optional[str] = None

    def to_json(self) -> dict:
        return {
            "lat": self.lat,
            "lng": self.lng,
            "altitude": self.alt,
        }

    @staticmethod
    def from_json(json: dict):
        return LatLngAltColumns(
            lat=json["lat"],
            lng=json["lng"],
            alt=glom.glom(json, "altitude", default=None),
        )


@dataclass
class LatLngCntPairColumns:
    """The mapping between data columns and layer properties.

    Required:
      source_lat: str - name of the data column with source latitude data
      source_lng: str - name of the data column with source longitude data
      target_lat: str - name of the data column with target latitude data
      target_lng: str - name of the data column with target longitude data

    Optional:
      count: str - name of the data column with counts data
      source_name: str - name of the data column with source name data
      target_name: str - name of the data column with target name data
    """

    mode: Literal["LAT_LNG"] = field(init=False, default="LAT_LNG")
    source_lat: str
    source_lng: str
    target_lat: str
    target_lng: str
    count: Optional[float] = None
    source_name: Optional[str] = None
    target_name: Optional[str] = None

    def to_json(self) -> dict:
        return {
            "lat0": self.source_lat,
            "lng0": self.source_lng,
            "lat1": self.target_lat,
            "lng1": self.target_lng,
            "count": self.count,
            "sourceName": self.source_name,
            "targetName": self.target_name,
        }

    @staticmethod
    def from_json(json: dict):
        return LatLngCntPairColumns(
            source_lat=json["lat0"],
            source_lng=json["lng0"],
            target_lat=json["lat1"],
            target_lng=json["lng1"],
            count=glom.glom(json, "count", default=None),
            source_name=glom.glom(json, "sourceName", default=None),
            target_name=glom.glom(json, "targetName", default=None),
        )


@dataclass
class H3CntPairColumns:
    """The mapping between data columns and layer properties.

    Required:
      source_h3: str - name of the data column with source H3 cell ID data
      target_h3: str - name of the data column with target H3 cell ID data

    Optional:
      count: str - name of the data column with counts data
      source_name: str - name of the data column with source name data
      target_name: str - name of the data column with target name data
    """

    mode: Literal["H3"] = field(init=False, default="H3")
    source_h3: str
    target_h3: str
    count: Optional[float] = None
    source_name: Optional[str] = None
    target_name: Optional[str] = None

    def to_json(self) -> dict:
        return {
            "sourceH3": self.source_h3,
            "targetH3": self.target_h3,
            "count": self.count,
            "sourceName": self.source_name,
            "targetName": self.target_name,
        }

    @staticmethod
    def from_json(json: dict):
        return H3CntPairColumns(
            source_h3=json["sourceH3"],
            target_h3=json["targetH3"],
            count=glom.glom(json, "count", default=None),
            source_name=glom.glom(json, "sourceName", default=None),
            target_name=glom.glom(json, "targetName", default=None),
        )
