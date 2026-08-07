import csv
import io
from dataclasses import dataclass


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


@dataclass
class IngestionQuarantineRecord:
    """Quarantined malformed TSV row log."""

    row_index: int
    raw_line: str
    reason: str


class EBDSamplingEventParser:
    """Parses and deduplicates eBird EBD and SED checklist events with named-column schema validation."""

    REQUIRED_SED_COLUMNS = {
        "SAMPLING EVENT IDENTIFIER",
        "PROTOCOL TYPE",
        "ALL SPECIES REPORTED",
        "OBSERVATION DATE",
        "LATITUDE",
        "LONGITUDE",
    }

    REQUIRED_EBD_COLUMNS = {
        "SAMPLING EVENT IDENTIFIER",
        "SPECIES CODE",
        "SCIENTIFIC NAME",
        "COMMON NAME",
    }

    @classmethod
    def parse_sed_tsv(
        cls, tsv_data: str
    ) -> tuple[list[SamplingEvent], list[IngestionQuarantineRecord]]:
        """Parse Sampling Event Data (SED) TSV string using named-column mapping."""
        events: list[SamplingEvent] = []
        quarantine: list[IngestionQuarantineRecord] = []

        reader = csv.DictReader(io.StringIO(tsv_data), delimiter="\t")
        if not reader.fieldnames:
            raise ValueError("Empty or headerless SED TSV content")

        header_set = {f.strip().upper() for f in reader.fieldnames if f}
        missing = cls.REQUIRED_SED_COLUMNS - header_set
        if missing:
            raise ValueError(f"SED TSV header missing required named columns: {missing}")

        # Build case-insensitive header lookup map
        norm_map = {f.strip().upper(): f for f in reader.fieldnames if f}

        for idx, row in enumerate(reader, start=2):
            try:
                sid = row[norm_map["SAMPLING EVENT IDENTIFIER"]].strip()
                gid_raw = row.get(norm_map.get("GROUP IDENTIFIER", ""), "")
                gid = gid_raw.strip() if gid_raw and gid_raw.strip() else None

                protocol = row[norm_map["PROTOCOL TYPE"]].strip()
                all_rep_str = row[norm_map["ALL SPECIES REPORTED"]].strip()
                all_reported = all_rep_str in ("1", "true", "True", "TRUE")

                obs_date = row[norm_map["OBSERVATION DATE"]].strip()
                obs_time = (
                    row.get(norm_map.get("TIME OBSERVATIONS STARTED", ""), "00:00:00").strip()
                    or "00:00:00"
                )

                dur_str = row.get(norm_map.get("DURATION MINUTES", ""), "0").strip()
                duration = float(dur_str) if dur_str else 0.0

                dist_str = row.get(norm_map.get("EFFORT DISTANCE KM", ""), "").strip()
                dist = float(dist_str) if dist_str else None

                area_str = row.get(norm_map.get("EFFORT AREA HA", ""), "").strip()
                area = float(area_str) if area_str else None

                obs_num_str = row.get(norm_map.get("NUMBER OBSERVERS", ""), "1").strip()
                observers = int(obs_num_str) if obs_num_str else 1

                lat = float(row[norm_map["LATITUDE"]].strip())
                lon = float(row[norm_map["LONGITUDE"]].strip())

                events.append(
                    SamplingEvent(
                        sampling_event_id=sid,
                        group_identifier=gid,
                        protocol_type=protocol,
                        all_species_reported=all_reported,
                        observation_date=obs_date,
                        time_observations_started=obs_time,
                        duration_minutes=duration,
                        effort_distance_km=dist,
                        effort_area_ha=area,
                        number_observers=observers,
                        latitude=lat,
                        longitude=lon,
                    )
                )
            except Exception as exc:
                quarantine.append(
                    IngestionQuarantineRecord(
                        row_index=idx,
                        raw_line=str(row),
                        reason=f"Failed parsing row: {exc}",
                    )
                )

        return events, quarantine

    @classmethod
    def parse_ebd_tsv(
        cls, tsv_data: str
    ) -> tuple[list[SpeciesObservation], list[IngestionQuarantineRecord]]:
        """Parse eBird Basic Dataset (EBD) observation TSV string using named-column mapping."""
        observations: list[SpeciesObservation] = []
        quarantine: list[IngestionQuarantineRecord] = []

        reader = csv.DictReader(io.StringIO(tsv_data), delimiter="\t")
        if not reader.fieldnames:
            raise ValueError("Empty or headerless EBD TSV content")

        header_set = {f.strip().upper() for f in reader.fieldnames if f}
        missing = cls.REQUIRED_EBD_COLUMNS - header_set
        if missing:
            raise ValueError(f"EBD TSV header missing required named columns: {missing}")

        norm_map = {f.strip().upper(): f for f in reader.fieldnames if f}

        for idx, row in enumerate(reader, start=2):
            try:
                sid = row[norm_map["SAMPLING EVENT IDENTIFIER"]].strip()
                code = row[norm_map["SPECIES CODE"]].strip()
                sci_name = row[norm_map["SCIENTIFIC NAME"]].strip()
                common_name = row[norm_map["COMMON NAME"]].strip()
                count_str = row.get(norm_map.get("OBSERVATION COUNT", ""), "1").strip() or "1"

                category = row.get(norm_map.get("CATEGORY", ""), "").strip().lower()
                is_slash = category == "slash" or ("/" in code)
                is_subspecies = category in ("issf", "subspecies")

                observations.append(
                    SpeciesObservation(
                        sampling_event_id=sid,
                        raw_species_code=code,
                        scientific_name=sci_name,
                        common_name=common_name,
                        observation_count=count_str,
                        is_subspecies=is_subspecies,
                        is_slash=is_slash,
                    )
                )
            except Exception as exc:
                quarantine.append(
                    IngestionQuarantineRecord(
                        row_index=idx,
                        raw_line=str(row),
                        reason=f"Failed parsing row: {exc}",
                    )
                )

        return observations, quarantine

    @classmethod
    def join_ebd_sed(
        cls, events: list[SamplingEvent], observations: list[SpeciesObservation]
    ) -> dict[str, list[SpeciesObservation]]:
        """Join EBD observation detections to deduplicated SED sampling events."""
        event_ids = {e.sampling_event_id for e in events}
        joined: dict[str, list[SpeciesObservation]] = {e.sampling_event_id: [] for e in events}

        for obs in observations:
            if obs.sampling_event_id in event_ids:
                joined[obs.sampling_event_id].append(obs)

        return joined

    @classmethod
    def deduplicate_group_checklists(cls, events: list[SamplingEvent]) -> list[SamplingEvent]:
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
            sorted_events = sorted(group_events, key=lambda e: e.sampling_event_id)
            primary = sorted_events[0]
            deduplicated.append(primary)

        return deduplicated
