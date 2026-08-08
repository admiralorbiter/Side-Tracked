"""eBird Recent API Adapter for fetching real recent observation evidence."""

import hashlib
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from packages.ovon_core.domain.evidence import (
    EvidenceLocation,
    NormalizedOccurrenceEvidence,
)
from packages.ovon_core.evidence.providers import BaseOccurrenceProvider


class eBirdRecentAdapter(BaseOccurrenceProvider):
    """Adapter for fetching recent species observation evidence via eBird API v2."""

    def __init__(
        self,
        api_key: str | None = None,
        cache_dir: Path | str = "data/cache/ebird",
    ) -> None:
        self.api_key = api_key or os.environ.get("EBIRD_API_KEY")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_occurrences(
        self,
        bounding_box: tuple[float, float, float, float],
        concept_ids: Sequence[str],
        days_window: int = 30,
    ) -> list[NormalizedOccurrenceEvidence]:
        """Fetch recent occurrences within bounding box."""
        min_lat, min_lon, max_lat, max_lon = bounding_box
        lat = (min_lat + max_lat) / 2.0
        lon = (min_lon + max_lon) / 2.0

        # Check cache
        cache_key = hashlib.sha256(f"ebird_{lat:.3f}_{lon:.3f}_{days_window}".encode()).hexdigest()[
            :12
        ]
        cache_file = self.cache_dir / f"{cache_key}.json"

        raw_records = None
        if cache_file.exists():
            try:
                raw_records = json.loads(cache_file.read_text(encoding="utf-8"))
            except Exception:
                raw_records = None

        if raw_records is None and self.api_key:
            url = f"https://api.ebird.org/v2/data/obs/geo/recent?lat={lat:.4f}&lng={lon:.4f}&dist=5&back={days_window}"
            req = urllib.request.Request(url, headers={"X-eBirdToken": self.api_key})
            try:
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.status == 200:
                        raw_records = json.loads(resp.read().decode("utf-8"))
                        cache_file.write_text(json.dumps(raw_records), encoding="utf-8")
            except Exception:
                raw_records = []

        if not raw_records:
            return []

        occurrences: list[NormalizedOccurrenceEvidence] = []
        now = datetime.now(timezone.utc)

        for item in raw_records:
            species_name = item.get("comName", "Bird")
            c_id = f"sidetrack_concept:{species_name.lower().replace(' ', '_')}"

            if concept_ids and c_id not in concept_ids:
                continue

            obs_dt_str = item.get("obsDt")
            obs_dt = now
            if obs_dt_str:
                try:
                    obs_dt = datetime.fromisoformat(obs_dt_str).replace(tzinfo=timezone.utc)
                except Exception:
                    obs_dt = now

            occurrences.append(
                NormalizedOccurrenceEvidence(
                    occurrence_id=f"ebird_{item.get('subId', 'sub')}_{item.get('speciesCode', 'sp')}",
                    concept_id=c_id,
                    source_origin="ebird_recent",
                    source_occurrence_id=item.get("subId", "sub"),
                    original_scientific_name=item.get("sciName", species_name),
                    taxonomy_authority="eBird-2025",
                    observed_at=obs_dt,
                    latitude=float(item.get("lat", lat)),
                    longitude=float(item.get("lng", lon)),
                    location_semantics=EvidenceLocation.CHECKLIST_LOCATION,
                    geoprivacy="open",
                    coordinate_uncertainty_m=50.0,
                    source_dataset_id="eBird Recent API v2",
                    raw_payload=item,
                )
            )

        return occurrences
