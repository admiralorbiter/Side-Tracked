"""Route Evidence Domain Models and Value Objects."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from packages.ovon_core.domain.spatial import Coordinate


class EvidenceLocation(str, Enum):
    """Semantic meaning of an occurrence coordinate."""

    OBSERVATION_POINT = "observation_point"
    CHECKLIST_LOCATION = "checklist_location"
    OBSCURED_PUBLIC_POINT = "obscured_public_point"
    COARSE_REGION = "coarse_region"
    UNKNOWN = "unknown"


class EvidenceVisibility(str, Enum):
    """Visibility policy for displaying evidence items."""

    EXACT_DISPLAY_ALLOWED = "exact_display_allowed"
    UNCERTAINTY_DISPLAY_ONLY = "uncertainty_display_only"
    COARSE_DISPLAY_ONLY = "coarse_display_only"
    HIDDEN = "hidden"


@dataclass(frozen=True, slots=True)
class NormalizedOccurrenceEvidence:
    """Normalized occurrence evidence record across all biodiversity data sources."""

    occurrence_id: str
    concept_id: str  # Sidetrack TaxonConcept UUID
    source_origin: str  # e.g., "ebird_recent", "gbif", "inat", "ebd", "sidetrack_discovery"
    source_occurrence_id: str
    original_scientific_name: str
    taxonomy_authority: str
    observed_at: datetime
    latitude: float
    longitude: float
    location_semantics: EvidenceLocation = EvidenceLocation.OBSERVATION_POINT
    geoprivacy: str = "open"  # "open", "obscured", "private"
    coordinate_uncertainty_m: float | None = None
    source_event_id: str | None = None
    source_dataset_id: str | None = None
    source_record_url: str | None = None
    is_presence_only: bool = True
    sensitive: bool = False
    observation_license: str = "Unspecified"
    lineage_id: str | None = None
    duplicate_cluster_id: str | None = None
    raw_payload: dict | None = None
    retrieved_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def coordinate(self) -> Coordinate:
        return Coordinate(self.latitude, self.longitude)


@dataclass(frozen=True, slots=True)
class SpeciesRouteEvidence:
    """Aggregated route evidence read model for a single species."""

    concept_id: str
    common_name: str
    scientific_name: str
    recent_reports_count: int
    seasonal_reports_count: int
    nearest_displayable_report: Coordinate | None
    nearest_distance_m: float | None
    distance_claim_allowed: bool
    eligible_checklist_count: int
    checklist_detection_count: int
    checklist_detection_rate: float | None  # Beta-Binomial smoothed rate (D_s + 1) / (N + 2)
    evidence_score: float
    evidence_score_status: str
    source_names: tuple[str, ...]
    freshness_days: float | None
    visibility_policy: EvidenceVisibility
    display_note: str = ""

    @property
    def formatted_distance(self) -> str:
        if not self.distance_claim_allowed or self.nearest_distance_m is None:
            return "Reported in broader area"
        if self.nearest_distance_m >= 1000.0:
            return f"About {self.nearest_distance_m / 1000.0:.1f} km from walk"
        return f"About {int(self.nearest_distance_m)}m from walk"


@dataclass(frozen=True, slots=True)
class RouteEvidenceSummary:
    """Complete Route Evidence Summary read model for a planned route option."""

    route_id: str
    generated_at: str
    recent_species_count: int
    historical_species_count: int
    total_checklist_coverage: int
    species_evidence: tuple[SpeciesRouteEvidence, ...]
    by_segment: dict[int, tuple[SpeciesRouteEvidence, ...]]
    limitations: tuple[str, ...]
    status: str = "ok"  # "ok", "no_recent_reports", "provider_unavailable", "sensitive_suppressed"

    @property
    def map_items(self) -> list[dict[str, Any]]:
        """Return list of map displayable evidence pins."""
        items = []
        for sp in self.species_evidence:
            if sp.nearest_displayable_report and sp.distance_claim_allowed:
                items.append(
                    {
                        "common_name": sp.common_name,
                        "lat": sp.nearest_displayable_report.latitude,
                        "lon": sp.nearest_displayable_report.longitude,
                        "dist": round(sp.nearest_distance_m, 1) if sp.nearest_distance_m else 0,
                        "source": ", ".join(sp.source_names),
                        "type": "exact",
                    }
                )
        return items

    def to_dict(self) -> dict[str, Any]:
        """Convert summary to JSON-serializable dictionary."""
        return {
            "route_id": self.route_id,
            "generated_at": self.generated_at,
            "recent_species_count": self.recent_species_count,
            "historical_species_count": self.historical_species_count,
            "total_checklist_coverage": self.total_checklist_coverage,
            "status": self.status,
            "species_count": len(self.species_evidence),
            "limitations": list(self.limitations),
            "map_items": self.map_items,
        }
