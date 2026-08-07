"""DiscoveryRecord domain model for personal species encounters and field decks."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class DiscoverySourceRole(str, Enum):
    """Source role of a discovery record."""

    USER_RECALL_ONLY = "user_recall_only"
    OPPORTUNISTIC_DETECTION = "opportunistic_detection"
    EBIRD_COMPLETE_CHECKLIST = "ebird_complete_checklist"
    IN_ROUTE_WALK = "in_route_walk"


class DetectionEvidenceType(str, Enum):
    """Detection channel for the encounter."""

    SEEN = "seen"
    HEARD = "heard"
    SEEN_AND_HEARD = "seen_and_heard"
    PHOTO_VERIFIED = "photo_verified"
    AUDIO_RECORDED = "audio_recorded"


class DiscoveryConfidence(str, Enum):
    """Discrete user confidence level."""

    CERTAIN = "certain"
    UNSURE = "unsure"


class PrivacyLevel(str, Enum):
    """Privacy level for location data."""

    PUBLIC_EXACT = "public_exact"
    PUBLIC_OBFUSCATED = "public_obfuscated"
    PRIVATE_ONLY = "private_only"


@dataclass(frozen=True, slots=True)
class DiscoveryRecord:
    """Personal species discovery record bound to Sidetrack concept_id."""

    discovery_id: UUID
    user_id: str
    concept_id: UUID
    taxonomic_version_at_discovery: str
    original_taxon_ref: str
    observed_at: datetime
    latitude: float
    longitude: float
    spatial_cell_id: str  # H3 Resolution 8 cell index
    source_role: DiscoverySourceRole
    evidence_type: DetectionEvidenceType
    confidence: DiscoveryConfidence = DiscoveryConfidence.CERTAIN
    count: int = 1
    associated_plan_id: str | None = None
    associated_route_id: str | None = None
    privacy_level: PrivacyLevel = PrivacyLevel.PUBLIC_EXACT
    is_sensitive: bool = False
    notes: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not (-90.0 <= self.latitude <= 90.0) or not (-180.0 <= self.longitude <= 180.0):
            raise ValueError(f"Invalid discovery coordinates: ({self.latitude}, {self.longitude})")
        if self.latitude == 0.0 and self.longitude == 0.0:
            raise ValueError("Coordinates cannot default to null island (0, 0)")
        if self.count < 1:
            raise ValueError("Discovery count must be at least 1")

    @classmethod
    def create(
        cls,
        user_id: str,
        concept_id: UUID,
        original_taxon_ref: str,
        latitude: float,
        longitude: float,
        spatial_cell_id: str,
        source_role: DiscoverySourceRole = DiscoverySourceRole.IN_ROUTE_WALK,
        evidence_type: DetectionEvidenceType = DetectionEvidenceType.SEEN,
        confidence: DiscoveryConfidence = DiscoveryConfidence.CERTAIN,
        count: int = 1,
        associated_plan_id: str | None = None,
        associated_route_id: str | None = None,
        notes: str | None = None,
    ) -> "DiscoveryRecord":
        """Factory method for instantiating a valid DiscoveryRecord."""
        now = datetime.now(timezone.utc)
        return cls(
            discovery_id=uuid4(),
            user_id=user_id,
            concept_id=concept_id,
            taxonomic_version_at_discovery="ST_TAXONOMY_2026_1",
            original_taxon_ref=original_taxon_ref,
            observed_at=now,
            latitude=latitude,
            longitude=longitude,
            spatial_cell_id=spatial_cell_id,
            source_role=source_role,
            evidence_type=evidence_type,
            confidence=confidence,
            count=count,
            associated_plan_id=associated_plan_id,
            associated_route_id=associated_route_id,
            privacy_level=PrivacyLevel.PUBLIC_EXACT,
            is_sensitive=False,
            notes=notes,
            created_at=now,
        )
