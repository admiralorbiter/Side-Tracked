"""Analytical Modeling Dataset Builder joining complete checklists, real environmental vectors, and H3 spatial blocks."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Sequence

import h3

from packages.ovon_core.domain.environmental_vector import SIDETRACK_ENV_SCHEMA_V1
from packages.ovon_core.spatial.real_environmental_extractor import (
    RealEnvironmentalFeatureExtractor,
)
from packages.ovon_core.spatial.solar import calculate_sun_altitude_degrees


@dataclass(frozen=True, slots=True)
class AnalyticalSamplingRow:
    """Single immutable analytical row joining checklist event, outcome, effort, timing, and environmental features."""

    event_id: str
    concept_id: str
    detected: int
    date: str
    latitude: float
    longitude: float
    spatial_block_id: str
    duration_minutes: float
    effort_distance_km: float
    number_observers: int
    solar_altitude_degrees: float
    canopy_cover_percent: float
    impervious_surface_percent: float
    water_edge_distance_m: float
    elevation_m: float
    slope_gradient_percent: float
    data_release_id: str

    def to_dict(self) -> dict:
        return asdict(self)


class AnalyticalDatasetBuilder:
    """Builder for constructing immutable analytical modeling tables from complete checklists."""

    def __init__(
        self,
        env_extractor: RealEnvironmentalFeatureExtractor | None = None,
        data_release_id: str = "EBD-2026.07_SED-2026.07",
    ) -> None:
        self.env_extractor = env_extractor or RealEnvironmentalFeatureExtractor()
        self.data_release_id = data_release_id

    def build_analytical_rows(
        self,
        sampling_events: Sequence[dict],
        observations: Sequence[dict],
        focal_concept_ids: Sequence[str],
        h3_resolution: int = 7,
    ) -> list[AnalyticalSamplingRow]:
        """Build immutable analytical rows with group deduplication, zero-filling, and environmental feature joining."""
        # 1. Group checklist deduplication
        deduped_events: dict[str, dict] = {}
        for ev in sampling_events:
            # Filter for complete checklists only (ALL SPECIES REPORTED = 1)
            if not ev.get("all_species_reported", True):
                continue

            lat = float(ev.get("latitude", 39.03))
            lon = float(ev.get("longitude", -94.59))
            date_str = str(ev.get("date", "2026-05-15"))
            key = f"{lat:.3f}_{lon:.3f}_{date_str}_{ev.get('time', '07:00')}"

            if key not in deduped_events:
                deduped_events[key] = ev

        # 2. Map detected concept IDs by event
        event_detections: dict[str, set[str]] = {}
        for obs in observations:
            e_id = obs.get("event_id", "")
            c_id = obs.get("concept_id", "")
            if e_id and c_id:
                event_detections.setdefault(e_id, set()).add(c_id)

        rows: list[AnalyticalSamplingRow] = []

        for key, ev in deduped_events.items():
            event_id = str(ev.get("event_id", f"S_{key}"))
            lat = float(ev.get("latitude", 39.0347))
            lon = float(ev.get("longitude", -94.5906))
            date_str = str(ev.get("date", "2026-05-15"))

            # H3 Spatial Cell Block ID for spatial holdout cross-validation
            try:
                spatial_block = h3.latlng_to_cell(lat, lon, h3_resolution)
            except Exception:
                spatial_block = f"h3_r7_{int(lat * 100)}_{int(lon * 100)}"

            # Extract continuous environmental vector
            env_vector = self.env_extractor.extract_feature_vector([(lat, lon)])

            # Compute astronomical solar altitude
            dt = datetime.now(timezone.utc)
            solar_alt = calculate_sun_altitude_degrees(lat, lon, dt)

            detected_set = event_detections.get(event_id, set())

            # Perform zero-filling for all focal concept IDs on complete checklist
            for c_id in focal_concept_ids:
                is_detected = 1 if c_id in detected_set else 0

                rows.append(
                    AnalyticalSamplingRow(
                        event_id=event_id,
                        concept_id=c_id,
                        detected=is_detected,
                        date=date_str,
                        latitude=lat,
                        longitude=lon,
                        spatial_block_id=spatial_block,
                        duration_minutes=float(ev.get("duration_minutes", 45.0)),
                        effort_distance_km=float(ev.get("effort_distance_km", 1.5)),
                        number_observers=int(ev.get("number_observers", 1)),
                        solar_altitude_degrees=round(solar_alt, 2),
                        canopy_cover_percent=env_vector.canopy_cover_percent,
                        impervious_surface_percent=env_vector.impervious_surface_percent,
                        water_edge_distance_m=env_vector.water_edge_distance_m,
                        elevation_m=env_vector.elevation_m,
                        slope_gradient_percent=env_vector.slope_gradient_percent,
                        data_release_id=self.data_release_id,
                    )
                )

        return rows
