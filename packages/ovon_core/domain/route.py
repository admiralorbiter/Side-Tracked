from dataclasses import dataclass
from enum import Enum

from packages.ovon_core.domain.media import FieldCue
from packages.ovon_core.domain.spatial import Coordinate
from packages.ovon_core.domain.taxonomy import TaxonRef
from packages.ovon_core.domain.habitat import HabitatType


class RoutePersona(str, Enum):
    """Public route personas."""

    EASY = "The Easy One"
    BIRDY = "The Birdy One"
    WEIRD = "The Weird One"
    SCENIC = "The Scenic One"


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
    observation_point: Coordinate | None = None
    navigation_instruction: str = ""
    habitat_type: HabitatType = HabitatType.OPEN_PARKLAND

    def __post_init__(self) -> None:
        if self.distance_meters <= 0:
            raise ValueError(f"Segment distance_meters ({self.distance_meters}) must be positive.")
        if self.duration_minutes <= 0:
            raise ValueError(
                f"Segment duration_minutes ({self.duration_minutes}) must be positive."
            )
        if self.field_cue and self.focal_species:
            if self.field_cue.taxon_ref not in self.focal_species:
                raise ValueError(
                    f"FieldCue taxon '{self.field_cue.taxon_ref.common_name}' must belong to segment focal_species."
                )

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

        # Reconcile segment distance and duration totals against route totals (tolerance +-1%)
        total_seg_dist = sum(s.distance_meters for s in self.segments)
        total_seg_dur = sum(s.duration_minutes for s in self.segments)

        if not (0.99 * self.distance_meters <= total_seg_dist <= 1.01 * self.distance_meters):
            raise ValueError(
                f"Summed segment distance ({total_seg_dist}m) does not reconcile with route distance ({self.distance_meters}m)."
            )
        if not (0.99 * self.duration_minutes <= total_seg_dur <= 1.01 * self.duration_minutes):
            raise ValueError(
                f"Summed segment duration ({total_seg_dur}min) does not reconcile with route duration ({self.duration_minutes}min)."
            )

    @property
    def unique_focal_species(self) -> tuple[TaxonRef, ...]:
        """Return tuple of distinct focal species across all route segments."""
        species = []
        for s in self.segments:
            for sp in s.focal_species:
                if sp not in species:
                    species.append(sp)
        return tuple(species)

    @property
    def badge_css_class(self) -> str:
        """Return CSS class for badge rendering based on persona."""
        if self.persona == RoutePersona.EASY:
            return "badge-easy"
        elif self.persona == RoutePersona.BIRDY:
            return "badge-birdy"
        elif self.persona == RoutePersona.WEIRD:
            return "badge-weird"
        return "badge-easy"

    @property
    def formatted_distance(self) -> str:
        if self.distance_meters >= 1000.0:
            return f"{self.distance_meters / 1000.0:.1f} km"
        return f"{int(self.distance_meters)}m"

    @property
    def formatted_duration(self) -> str:
        return f"{self.duration_minutes} min"
