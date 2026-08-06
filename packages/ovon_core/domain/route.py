from dataclasses import dataclass
from enum import Enum
from packages.ovon_core.domain.taxonomy import TaxonRef
from packages.ovon_core.domain.media import FieldCue

class RoutePersona(str, Enum):
    """Public route personas."""
    EASY = "The Easy One"
    BIRDY = "The Birdy One"
    WEIRD = "The Weird One"

@dataclass(frozen=True, slots=True)
class RouteStopAction:
    """Actionable observation stop along a segment."""
    name: str
    action_type: str  # e.g., "scan_tree_line", "listen_creek_edge"
    description: str

@dataclass(frozen=True, slots=True)
class RouteSegment:
    """Individual leg of a walking loop."""
    index: int
    name: str
    habitat_name: str
    distance_meters: float
    duration_minutes: float
    focal_species: tuple[TaxonRef, ...]
    field_cue: FieldCue
    geojson_geometry: dict | None = None

    @property
    def formatted_distance(self) -> str:
        if self.distance_meters >= 1000.0:
            return f"{self.distance_meters / 1000.0:.1f} km"
        return f"{int(self.distance_meters)}m"

@dataclass(frozen=True, slots=True)
class RouteOption:
    """Complete closed walking loop route choice."""
    id: str
    persona: RoutePersona
    name: str
    tagline: str
    duration_minutes: int
    distance_meters: float
    badge_label: str
    tradeoff_description: str
    segments: tuple[RouteSegment, ...]
    geojson_geometry: dict | None = None

    def __post_init__(self) -> None:
        if self.distance_meters <= 0:
            raise ValueError("distance_meters must be positive.")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive.")
        if not self.segments:
            raise ValueError("RouteOption must contain at least one segment.")

    @property
    def formatted_distance(self) -> str:
        if self.distance_meters >= 1000.0:
            return f"{self.distance_meters / 1000.0:.1f} km"
        return f"{int(self.distance_meters)}m"

    @property
    def formatted_duration(self) -> str:
        return f"{self.duration_minutes} min"
