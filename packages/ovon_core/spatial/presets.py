"""Public Park Presets Catalog for Sidetrack."""

from dataclasses import dataclass

from packages.ovon_core.domain import Coordinate, SpatialCellId
from packages.ovon_core.spatial.h3_indexer import lat_lng_to_h3_cell


@dataclass(frozen=True, slots=True)
class PublicParkPreset:
    """Preset public park origin for nature walking loops."""

    id: str
    name: str
    city_state: str
    coordinate: Coordinate
    cell: SpatialCellId


# Public Park Presets Catalog
LOOSE_PARK = PublicParkPreset(
    id="loose-park",
    name="Loose Park",
    city_state="Kansas City, MO",
    coordinate=Coordinate(39.0347, -94.5906),
    cell=lat_lng_to_h3_cell(Coordinate(39.0347, -94.5906), resolution=8),
)

MILL_CREEK_PARK = PublicParkPreset(
    id="mill-creek",
    name="Mill Creek Park",
    city_state="Kansas City, MO",
    coordinate=Coordinate(39.0430, -94.5880),
    cell=lat_lng_to_h3_cell(Coordinate(39.0430, -94.5880), resolution=8),
)

SWOPE_PARK = PublicParkPreset(
    id="swope-park",
    name="Swope Park Nature Center",
    city_state="Kansas City, MO",
    coordinate=Coordinate(39.0060, -94.5260),
    cell=lat_lng_to_h3_cell(Coordinate(39.0060, -94.5260), resolution=8),
)

OVERLAND_PARK_ARBORETUM = PublicParkPreset(
    id="op-arboretum",
    name="Overland Park Arboretum",
    city_state="Overland Park, KS",
    coordinate=Coordinate(38.8075, -94.6780),
    cell=lat_lng_to_h3_cell(Coordinate(38.8075, -94.6780), resolution=8),
)

ENGLISH_LANDING_PARK = PublicParkPreset(
    id="english-landing",
    name="English Landing Park",
    city_state="Parkville, MO",
    coordinate=Coordinate(39.1890, -94.6820),
    cell=lat_lng_to_h3_cell(Coordinate(39.1890, -94.6820), resolution=8),
)

PILOT_PARK_PRESETS: tuple[PublicParkPreset, ...] = (
    LOOSE_PARK,
    MILL_CREEK_PARK,
    SWOPE_PARK,
    OVERLAND_PARK_ARBORETUM,
    ENGLISH_LANDING_PARK,
)

PRESETS_BY_ID: dict[str, PublicParkPreset] = {p.id: p for p in PILOT_PARK_PRESETS}
