"""eBird Basic Dataset (EBD) & Sampling Event Data (SED) Ingestion & Group Deduplication Engine."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class SamplingEvent:
    """Normalized eBird Sampling Event (SED checklist metadata)."""

    sampling_event_id: str  # e.g., "S12345678"
    group_identifier: str | None  # e.g., "G123456"
    protocol_type: str  # e.g., "Traveling", "Stationary", "Area"
    all_species_reported: bool
    observation_date: str  # YYYY-MM-DD
    time_observations_started: str  # HH:MM:SS
    duration_minutes: float
    effort_distance_km: float | None
    effort_area_ha: float | None
    number_observers: int
    latitude: float
    longitude: float
    is_primary_group_checklist: bool = True


@dataclass(frozen=True, slots=True)
class SpeciesObservation:
    """Raw EBD species detection record."""

    sampling_event_id: str
    raw_species_code: str  # e.g., "amerob" or "myrwar"
    scientific_name: str
    common_name: str
    observation_count: str  # numeric or "X"
    is_subspecies: bool = False
    is_slash: bool = False


class EBDSamplingEventParser:
    """Parses and deduplicates eBird EBD and SED checklist events."""

    @classmethod
    def deduplicate_group_checklists(
        cls, events: list[SamplingEvent]
    ) -> list[SamplingEvent]:
        """Group checklist deduplication rule: Pick single primary checklist per GROUP IDENTIFIER (min SAMPLING EVENT IDENTIFIER)."""
        groups: dict[str, list[SamplingEvent]] = {}
        standalone: list[SamplingEvent] = []

        for ev in events:
            if ev.group_identifier:
                if ev.group_identifier not in groups:
                    groups[ev.group_identifier] = []
                groups[ev.group_identifier].append(ev)
            else:
                standalone.append(ev)

        deduplicated: list[SamplingEvent] = list(standalone)

        for gid, group_events in groups.items():
            # Pick checklist with min sampling_event_id as primary representative
            sorted_events = sorted(group_events, key=lambda e: e.sampling_event_id)
            primary = sorted_events[0]
            deduplicated.append(primary)

        return deduplicated
