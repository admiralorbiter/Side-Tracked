from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from packages.ovon_core.domain.errors import InvalidTimeBudgetError
from packages.ovon_core.domain.spatial import Coordinate


class JourneyIntent(str, Enum):
    """User journey intent types."""

    LOOP_FROM_HERE = "loop_from_here"
    ADD_NATURE_TO_TRIP = "add_nature_to_trip"
    FIND_SPECIES = "find_species"
    SURPRISE_ME = "surprise_me"


SUPPORTED_DURATIONS_MINUTES = {30, 45, 60, 90}


@dataclass(frozen=True, slots=True)
class LoopRequest:
    """Immutable User Loop Planning Request."""

    origin: Coordinate
    origin_name: str
    duration_minutes: int = 45
    intent: JourneyIntent = JourneyIntent.LOOP_FROM_HERE
    paved_only: bool = False
    quiet_mode: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.duration_minutes not in SUPPORTED_DURATIONS_MINUTES:
            raise InvalidTimeBudgetError(
                f"Duration {self.duration_minutes} min is unsupported. Choose from {sorted(SUPPORTED_DURATIONS_MINUTES)}."
            )
        if not self.origin_name.strip():
            raise ValueError("origin_name cannot be empty.")
