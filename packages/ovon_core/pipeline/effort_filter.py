"""Scientific Effort Normalization & Feature Vector Pipeline."""

import math
from dataclasses import dataclass
from packages.ovon_core.pipeline.ebd_ingest import SamplingEvent


@dataclass(frozen=True, slots=True)
class NormalizedEffortVector:
    """Normalized effort feature vector for calibrated occupancy modeling."""

    sampling_event_id: str
    duration_minutes: float
    distance_km: float
    hours_past_sunrise: float
    log_group_size: float
    is_effort_valid: bool
    rejection_reason: str | None = None


class EffortFilterPipeline:
    """Filters scientific protocols and builds normalized effort covariate vectors."""

    # Protocol & Effort bounds
    ALLOWED_PROTOCOLS = {"Stationary", "Traveling", "Area", "P21", "P22", "P23"}
    MIN_DURATION_MINUTES = 5.0
    MAX_DURATION_MINUTES = 180.0  # 3 hours
    MAX_DISTANCE_KM = 5.0
    MAX_AREA_HA = 100.0

    @classmethod
    def filter_and_normalize(cls, event: SamplingEvent) -> NormalizedEffortVector:
        """Validate checklist effort constraints and compute continuous effort covariates."""
        # 1. Protocol check
        if event.protocol_type not in cls.ALLOWED_PROTOCOLS:
            return NormalizedEffortVector(
                sampling_event_id=event.sampling_event_id,
                duration_minutes=event.duration_minutes,
                distance_km=event.effort_distance_km or 0.0,
                hours_past_sunrise=0.0,
                log_group_size=0.0,
                is_effort_valid=False,
                rejection_reason=f"Disallowed protocol type: '{event.protocol_type}'",
            )

        # 2. Duration check
        if not (cls.MIN_DURATION_MINUTES <= event.duration_minutes <= cls.MAX_DURATION_MINUTES):
            return NormalizedEffortVector(
                sampling_event_id=event.sampling_event_id,
                duration_minutes=event.duration_minutes,
                distance_km=event.effort_distance_km or 0.0,
                hours_past_sunrise=0.0,
                log_group_size=0.0,
                is_effort_valid=False,
                rejection_reason=f"Duration {event.duration_minutes}m out of bounds [{cls.MIN_DURATION_MINUTES}, {cls.MAX_DURATION_MINUTES}]",
            )

        # 3. Distance check
        dist = event.effort_distance_km or 0.0
        if dist > cls.MAX_DISTANCE_KM:
            return NormalizedEffortVector(
                sampling_event_id=event.sampling_event_id,
                duration_minutes=event.duration_minutes,
                distance_km=dist,
                hours_past_sunrise=0.0,
                log_group_size=0.0,
                is_effort_valid=False,
                rejection_reason=f"Distance {dist}km exceeds max limit {cls.MAX_DISTANCE_KM}km",
            )

        # 4. Compute hours_past_sunrise approximation (default 06:00 sunrise)
        hours_past_sunrise = cls._calculate_hours_past_sunrise(event.time_observations_started)
        log_group = math.log(max(1, event.number_observers))

        return NormalizedEffortVector(
            sampling_event_id=event.sampling_event_id,
            duration_minutes=event.duration_minutes,
            distance_km=dist,
            hours_past_sunrise=hours_past_sunrise,
            log_group_size=log_group,
            is_effort_valid=True,
            rejection_reason=None,
        )

    @staticmethod
    def _calculate_hours_past_sunrise(time_str: str) -> float:
        """Parse HH:MM:SS observation start time and return hours relative to 06:00 sunrise."""
        try:
            parts = time_str.split(":")
            hour = float(parts[0])
            minute = float(parts[1]) if len(parts) > 1 else 0.0
            decimal_time = hour + (minute / 60.0)
            return round(decimal_time - 6.0, 2)
        except Exception:
            return 0.0
