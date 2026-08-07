"""Kansas City Regional Pilot Entrance Catalog for OVON Core."""

from dataclasses import dataclass

from packages.ovon_core.domain import Coordinate, SpatialCellId
from packages.ovon_core.spatial import lat_lng_to_h3_cell


@dataclass(frozen=True, slots=True)
class ParkEntrance:
    """Candidate entrance or access location for public parks."""

    name: str
    park_name: str
    coordinate: Coordinate
    cell: SpatialCellId
    access_status: str = "open_public"
    parking_available: bool = True


# Kansas City Regional Pilot Entrances
LOOSE_PARK_MAIN = ParkEntrance(
    name="Loose Park Main North Entrance",
    park_name="Jacob L. Loose Park",
    coordinate=Coordinate(39.0355, -94.5906),
    cell=lat_lng_to_h3_cell(Coordinate(39.0355, -94.5906), resolution=8),
)

LOOSE_PARK_SOUTH = ParkEntrance(
    name="Loose Park Rose Garden Entrance",
    park_name="Jacob L. Loose Park",
    coordinate=Coordinate(39.0325, -94.5920),
    cell=lat_lng_to_h3_cell(Coordinate(39.0325, -94.5920), resolution=8),
)

MILL_CREEK_FOUNTAIN = ParkEntrance(
    name="Mill Creek Fountain Plaza Entrance",
    park_name="Mill Creek Park",
    coordinate=Coordinate(39.0430, -94.5880),
    cell=lat_lng_to_h3_cell(Coordinate(39.0430, -94.5880), resolution=8),
)

SWOPE_NATURE_CENTER = ParkEntrance(
    name="Lakeside Nature Center Entrance",
    park_name="Swope Park",
    coordinate=Coordinate(39.0060, -94.5260),
    cell=lat_lng_to_h3_cell(Coordinate(39.0060, -94.5260), resolution=8),
)

OVERLAND_PARK_ARBORETUM_ENTRANCE = ParkEntrance(
    name="Arboretum Visitor Center Entrance",
    park_name="Overland Park Arboretum",
    coordinate=Coordinate(38.8075, -94.6780),
    cell=lat_lng_to_h3_cell(Coordinate(38.8075, -94.6780), resolution=8),
)

ENGLISH_LANDING_RIVER = ParkEntrance(
    name="English Landing Park Trailhead",
    park_name="English Landing Park",
    coordinate=Coordinate(39.1890, -94.6820),
    cell=lat_lng_to_h3_cell(Coordinate(39.1890, -94.6820), resolution=8),
)

KC_PARK_ENTRANCES: tuple[ParkEntrance, ...] = (
    LOOSE_PARK_MAIN,
    LOOSE_PARK_SOUTH,
    MILL_CREEK_FOUNTAIN,
    SWOPE_NATURE_CENTER,
    OVERLAND_PARK_ARBORETUM_ENTRANCE,
    ENGLISH_LANDING_RIVER,
)
