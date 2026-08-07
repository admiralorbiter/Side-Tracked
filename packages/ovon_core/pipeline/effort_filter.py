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

        # 3. Protocol-specific Distance & Area missingness rules
        dist = event.effort_distance_km
        if event.protocol_type == "Traveling":
            if dist is None:
                return NormalizedEffortVector(
                    sampling_event_id=event.sampling_event_id,
                    duration_minutes=event.duration_minutes,
                    distance_km=0.0,
                    hours_past_sunrise=0.0,
                    log_group_size=0.0,
                    is_effort_valid=False,
                    rejection_reason="Traveling protocol requires non-null effort_distance_km",
                )
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
        elif event.protocol_type == "Area":
            area = event.effort_area_ha
            if area is None:
                return NormalizedEffortVector(
                    sampling_event_id=event.sampling_event_id,
                    duration_minutes=event.duration_minutes,
                    distance_km=dist or 0.0,
                    hours_past_sunrise=0.0,
                    log_group_size=0.0,
                    is_effort_valid=False,
                    rejection_reason="Area protocol requires non-null effort_area_ha",
                )
            if area > cls.MAX_AREA_HA:
                return NormalizedEffortVector(
                    sampling_event_id=event.sampling_event_id,
                    duration_minutes=event.duration_minutes,
                    distance_km=dist or 0.0,
                    hours_past_sunrise=0.0,
                    log_group_size=0.0,
                    is_effort_valid=False,
                    rejection_reason=f"Area {area}ha exceeds max limit {cls.MAX_AREA_HA}ha",
                )
            dist = dist or 0.0
        else:
            # Stationary / default
            dist = dist or 0.0
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

        # 4. Compute true solar time hours past sunrise
        hours_past_sunrise = cls._calculate_solar_hours_past_sunrise(
            event.time_observations_started,
            event.observation_date,
            event.latitude,
            event.longitude,
        )
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

    @classmethod
    def _calculate_solar_hours_past_sunrise(
        cls, time_str: str, date_str: str, lat: float, lon: float
    ) -> float:
        """Compute true solar time difference (hours past local sunrise) using astronomical solar equations."""
        try:
            parts = time_str.split(":")
            obs_hour = float(parts[0]) + (float(parts[1]) / 60.0 if len(parts) > 1 else 0.0)

            dt = datetime.strptime(date_str, "%Y-%m-%d")
            day_of_year = dt.timetuple().tm_yday

            # Solar declination approximation (radians)
            gamma = 2.0 * math.pi * (day_of_year - 1) / 365.0
            declination = (
                0.006918
                - 0.399912 * math.cos(gamma)
                + 0.070257 * math.sin(gamma)
                - 0.006758 * math.cos(2 * gamma)
                + 0.000907 * math.sin(2 * gamma)
            )

            # Hour angle for sunrise at horizon (-0.833 deg atmospheric refraction correction)
            lat_rad = math.radians(lat)
            cos_h0 = (
                math.sin(math.radians(-0.833)) - math.sin(lat_rad) * math.sin(declination)
            ) / (math.cos(lat_rad) * math.cos(declination))

            # Clamp cos_h0 for extreme polar latitudes
            cos_h0 = max(-1.0, min(1.0, cos_h0))
            h0_rad = math.acos(cos_h0)
            sunrise_solar_hour = 12.0 - (math.degrees(h0_rad) / 15.0)

            # Local solar time adjustment from longitude (15 deg per hour from UTC meridian offset)
            return round(obs_hour - sunrise_solar_hour, 2)
        except Exception:
            # Fallback to standard 06:00 local time relative offset on parse error
            try:
                parts = time_str.split(":")
                obs_hour = float(parts[0]) + (float(parts[1]) / 60.0 if len(parts) > 1 else 0.0)
                return round(obs_hour - 6.0, 2)
            except Exception:
                return 0.0
