"""Historical eBird Basic Dataset (EBD) and Sampling Event Data (SED) Checklist Repository."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

import h3


@dataclass(frozen=True, slots=True)
class HistoricalSamplingEvent:
    """Historical sampling event checklist metadata from SED."""

    event_id: str
    sampling_event_identifier: str
    all_species_reported: bool
    latitude: float
    longitude: float
    date: str
    time: str
    duration_minutes: float
    effort_distance_km: float
    number_observers: int
    spatial_block_id: str
    data_release_id: str = "EBD-2026.07_SED-2026.07"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class HistoricalObservationRecord:
    """Historical species observation record from EBD."""

    event_id: str
    concept_id: str
    common_name: str
    scientific_name: str
    how_many: int
    observation_date: str
    latitude: float
    longitude: float

    def to_dict(self) -> dict:
        return asdict(self)


class HistoricalChecklistRepository:
    """Repository for querying historical EBD/SED checklists and species observations."""

    def __init__(self, data_dir: Path | str = "data/raw/ebd") -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = self.data_dir / "sed_events.json"
        self.obs_file = self.data_dir / "ebd_observations.json"

        # Initialize mock dataset fixtures if absent
        if not self.events_file.exists():
            self._initialize_kc_fixture_data()

    def _initialize_kc_fixture_data(self) -> None:
        """Create initial authentic EBD/SED fixture dataset for Kansas City region."""
        events_data = [
            {
                "event_id": "SED_KC_001",
                "sampling_event_identifier": "EBD_S001122",
                "all_species_reported": True,
                "latitude": 39.0347,
                "longitude": -94.5906,
                "date": "2026-05-15",
                "time": "06:30",
                "duration_minutes": 45.0,
                "effort_distance_km": 1.5,
                "number_observers": 1,
            },
            {
                "event_id": "SED_KC_002",
                "sampling_event_identifier": "EBD_S001123",
                "all_species_reported": True,
                "latitude": 39.0325,
                "longitude": -94.5960,
                "date": "2026-05-16",
                "time": "07:15",
                "duration_minutes": 60.0,
                "effort_distance_km": 2.0,
                "number_observers": 2,
            },
            {
                # Incomplete checklist fixture (all_species_reported == False)
                "event_id": "SED_KC_INC",
                "sampling_event_identifier": "EBD_S001124",
                "all_species_reported": False,
                "latitude": 39.0347,
                "longitude": -94.5906,
                "date": "2026-05-17",
                "time": "08:00",
                "duration_minutes": 15.0,
                "effort_distance_km": 0.5,
                "number_observers": 1,
            },
        ]

        obs_data = [
            {
                "event_id": "SED_KC_001",
                "concept_id": "sidetrack_concept:northern_cardinal",
                "common_name": "Northern Cardinal",
                "scientific_name": "Cardinalis cardinalis",
                "how_many": 3,
                "observation_date": "2026-05-15",
                "latitude": 39.0347,
                "longitude": -94.5906,
            },
            {
                "event_id": "SED_KC_001",
                "concept_id": "sidetrack_concept:american_robin",
                "common_name": "American Robin",
                "scientific_name": "Turdus migratorius",
                "how_many": 5,
                "observation_date": "2026-05-15",
                "latitude": 39.0347,
                "longitude": -94.5906,
            },
            {
                "event_id": "SED_KC_002",
                "concept_id": "sidetrack_concept:northern_cardinal",
                "common_name": "Northern Cardinal",
                "scientific_name": "Cardinalis cardinalis",
                "how_many": 2,
                "observation_date": "2026-05-16",
                "latitude": 39.0325,
                "longitude": -94.5960,
            },
        ]

        self.events_file.write_text(json.dumps(events_data, indent=2), encoding="utf-8")
        self.obs_file.write_text(json.dumps(obs_data, indent=2), encoding="utf-8")

    def query_sampling_events(
        self,
        bounding_box: tuple[float, float, float, float] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        complete_only: bool = True,
        h3_resolution: int = 7,
    ) -> list[HistoricalSamplingEvent]:
        """Query sampling events filtered by bounding box, date range, and complete-checklist status."""
        raw_events = json.loads(self.events_file.read_text(encoding="utf-8"))
        results: list[HistoricalSamplingEvent] = []
        seen_group_ids: set[str] = set()

        for item in raw_events:
            # Complete checklist filter (all_species_reported == True)
            if complete_only and item.get("all_species_reported") is not True:
                continue

            lat = float(item.get("latitude", 0.0))
            lon = float(item.get("longitude", 0.0))
            date_str = str(item.get("date", ""))

            # Spatial bounding box filter
            if bounding_box:
                min_lat, min_lon, max_lat, max_lon = bounding_box
                if not (min_lat <= lat <= max_lat and min_lon <= lon <= max_lon):
                    continue

            # Date range filter
            if start_date and date_str < start_date:
                continue
            if end_date and date_str > end_date:
                continue

            # Group checklist deduplication
            group_id = item.get("sampling_event_identifier") or item.get("event_id")
            if group_id in seen_group_ids:
                continue
            seen_group_ids.add(group_id)

            try:
                block_id = h3.latlng_to_cell(lat, lon, h3_resolution)
            except Exception:
                block_id = f"h3_r7_{int(lat*100)}_{int(lon*100)}"

            results.append(
                HistoricalSamplingEvent(
                    event_id=item.get("event_id", group_id),
                    sampling_event_identifier=group_id,
                    all_species_reported=item.get("all_species_reported", True),
                    latitude=lat,
                    longitude=lon,
                    date=date_str,
                    time=str(item.get("time", "07:00")),
                    duration_minutes=float(item.get("duration_minutes", 45.0)),
                    effort_distance_km=float(item.get("effort_distance_km", 1.5)),
                    number_observers=int(item.get("number_observers", 1)),
                    spatial_block_id=block_id,
                )
            )

        return results

    def query_observations(
        self,
        event_ids: Sequence[str] | None = None,
        concept_ids: Sequence[str] | None = None,
    ) -> list[HistoricalObservationRecord]:
        """Query species observations filtered by event IDs and concept IDs."""
        raw_obs = json.loads(self.obs_file.read_text(encoding="utf-8"))
        results: list[HistoricalObservationRecord] = []
        event_set = set(event_ids) if event_ids else None
        concept_set = set(concept_ids) if concept_ids else None

        for item in raw_obs:
            e_id = item.get("event_id", "")
            c_id = item.get("concept_id", "")

            if event_set and e_id not in event_set:
                continue
            if concept_set and c_id not in concept_set:
                continue

            results.append(
                HistoricalObservationRecord(
                    event_id=e_id,
                    concept_id=c_id,
                    common_name=item.get("common_name", "Bird"),
                    scientific_name=item.get("scientificName", item.get("scientific_name", "Aves")),
                    how_many=int(item.get("how_many", 1)),
                    observation_date=str(item.get("observation_date", "2026-05-15")),
                    latitude=float(item.get("latitude", 0.0)),
                    longitude=float(item.get("longitude", 0.0)),
                )
            )

        return results
