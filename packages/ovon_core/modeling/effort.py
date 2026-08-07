"""Observer Effort and Survey Protocol Models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True, slots=True)
class EffortProtocolVector:
    """Quantified observer survey effort and protocol parameters."""

    survey_duration_minutes: float = 45.0  # Duration in minutes
    walking_speed_kmh: float = 2.5  # Observer walking pace (km/h)
    distance_traveled_m: float = 1800.0  # Route distance in meters
    departure_datetime: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sun_altitude_degrees: float = 15.0  # Solar elevation angle in degrees above horizon
    observer_experience_level: str = "intermediate"  # "novice", "intermediate", "expert"
    protocol_type: str = "Traveling"  # "Traveling", "Stationary"

    def calculate_effort_scaling_factor(self, baseline_minutes: float = 45.0) -> float:
        """Calculate non-linear effort detectability multiplier p_effort = 1 - (1 - p0)^(t / t0)."""
        t_ratio = max(0.1, self.survey_duration_minutes / baseline_minutes)
        # Diminishing returns scaling
        return 1.0 - (0.5**t_ratio)
