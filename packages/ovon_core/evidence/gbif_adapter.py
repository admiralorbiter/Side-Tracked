"""GBIF Occurrence API Adapter for presence-only evidence with coordinate uncertainty metadata."""

import hashlib
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from packages.ovon_core.domain.evidence import (
    EvidenceLocation,
    NormalizedOccurrenceEvidence,
)
from packages.ovon_core.evidence.providers import BaseOccurrenceProvider


class GBIFOccurrenceAdapter(BaseOccurrenceProvider):
    """Adapter for fetching presence-only occurrence records from GBIF API v1."""

    def __init__(self, cache_dir: Path | str = "data/cache/gbif") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_occurrences(
        self,
        bounding_box: tuple[float, float, float, float],
        concept_ids: Sequence[str],
        days_window: int = 30,
    ) -> list[NormalizedOccurrenceEvidence]:
        """Fetch presence-only GBIF occurrences within bounding box."""
        min_lat, min_lon, max_lat, max_lon = bounding_box

        cache_key = hashlib.sha256(
            f"gbif_{min_lat:.2f}_{min_lon:.2f}_{max_lat:.2f}_{max_lon:.2f}".encode()
        ).hexdigest()[:12]
        cache_file = self.cache_dir / f"{cache_key}.json"

        raw_data = None
        if cache_file.exists():
            try:
                raw_data = json.loads(cache_file.read_text(encoding="utf-8"))
            except Exception:
                raw_data = None

        if raw_data is None:
            # Query GBIF occurrence search API
            params = {
                "decimalLatitude": f"{min_lat},{max_lat}",
                "decimalLongitude": f"{min_lon},{max_lon}",
                "hasCoordinate": "true",
                "hasGeospatialIssue": "false",
                "limit": 50,
            }
            url = f"https://api.gbif.org/v1/occurrence/search?{urllib.parse.urlencode(params)}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Sidetrack/1.0"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.status == 200:
                        raw_data = json.loads(resp.read().decode("utf-8"))
                        cache_file.write_text(json.dumps(raw_data), encoding="utf-8")
            except Exception:
                raw_data = {"results": []}

        results = raw_data.get("results", []) if raw_data else []
        occurrences: list[NormalizedOccurrenceEvidence] = []
        now = datetime.now(timezone.utc)

        for item in results:
            obs_date_raw = item.get("eventDate") or item.get("dateIdentified")
            obs_dt = now
            if obs_date_raw:
                try:
                    obs_dt = datetime.fromisoformat(obs_date_raw.replace("Z", "+00:00")).replace(
                        tzinfo=timezone.utc
                    )
                except Exception:
                    continue  # Skip records with unparseable dates for recent window queries
            else:
                continue  # Require valid date for recent occurrence evidence

            days_old = (now - obs_dt).total_seconds() / 86400.0
            if days_old > days_window or days_old < 0:
                continue  # Enforce days_window filter strictly

            species_name = (
                item.get("vernacularName")
                or item.get("species")
                or item.get("scientificName")
                or "Organism"
            )
            c_id = f"sidetrack_concept:{species_name.lower().replace(' ', '_')}"

            if concept_ids and c_id not in concept_ids:
                continue

            lat = float(item.get("decimalLatitude", 0.0))
            lon = float(item.get("decimalLongitude", 0.0))
            uncertainty_m = float(item.get("coordinateUncertaintyInMeters", 100.0))

            publisher = item.get("publisherTitle", "GBIF Network")
            dataset_title = item.get("datasetName", "GBIF Occurrence Download")

            occurrences.append(
                NormalizedOccurrenceEvidence(
                    occurrence_id=f"gbif_{item.get('key', 'key')}",
                    concept_id=c_id,
                    source_origin="gbif_occurrence",
                    source_occurrence_id=str(item.get("key")),
                    original_scientific_name=item.get("scientificName", species_name),
                    taxonomy_authority="GBIF-2026",
                    observed_at=obs_dt,
                    latitude=lat,
                    longitude=lon,
                    location_semantics=EvidenceLocation.OBSERVATION_POINT,
                    geoprivacy="open",
                    coordinate_uncertainty_m=uncertainty_m,
                    source_dataset_id=f"{publisher} - {dataset_title}",
                    raw_payload=item,
                )
            )

        return occurrences
