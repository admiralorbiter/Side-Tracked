"""iNaturalist API Adapter for Research Grade observation evidence."""

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


class INaturalistOccurrenceAdapter(BaseOccurrenceProvider):
    """Adapter for fetching Research Grade observation records from iNaturalist API v1."""

    def __init__(self, cache_dir: Path | str = "data/cache/inaturalist") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_occurrences(
        self,
        bounding_box: tuple[float, float, float, float],
        concept_ids: Sequence[str],
        days_window: int = 30,
    ) -> list[NormalizedOccurrenceEvidence]:
        """Fetch Research Grade iNaturalist observations within bounding box."""
        min_lat, min_lon, max_lat, max_lon = bounding_box

        cache_key = hashlib.sha256(
            f"inat_{min_lat:.2f}_{min_lon:.2f}_{max_lat:.2f}_{max_lon:.2f}".encode()
        ).hexdigest()[:12]
        cache_file = self.cache_dir / f"{cache_key}.json"

        raw_data = None
        if cache_file.exists():
            try:
                raw_data = json.loads(cache_file.read_text(encoding="utf-8"))
            except Exception:
                raw_data = None

        if raw_data is None:
            params = {
                "quality_grade": "research",
                "nelat": max_lat,
                "nelng": max_lon,
                "swlat": min_lat,
                "swlng": min_lon,
                "per_page": 50,
            }
            url = f"https://api.inaturalist.org/v1/observations?{urllib.parse.urlencode(params)}"
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
            taxon_info = item.get("taxon") or {}
            species_name = (
                taxon_info.get("preferred_common_name") or taxon_info.get("name") or "Organism"
            )
            c_id = f"sidetrack_concept:{species_name.lower().replace(' ', '_')}"

            if concept_ids and c_id not in concept_ids:
                continue

            geo_raw = item.get("geojson") or {}
            coords = geo_raw.get("coordinates") or [min_lon, min_lat]
            lon = float(coords[0])
            lat = float(coords[1])

            geoprivacy = "open"
            uncertainty_m = 50.0
            if item.get("geoprivacy") == "obscured" or item.get("taxon_geoprivacy") == "obscured":
                geoprivacy = "obscured"
                uncertainty_m = 2500.0

            loc_semantics = (
                EvidenceLocation.OBSCURED_PUBLIC_POINT
                if geoprivacy == "obscured"
                else EvidenceLocation.OBSERVATION_POINT
            )

            occurrences.append(
                NormalizedOccurrenceEvidence(
                    occurrence_id=f"inat_{item.get('id', 'id')}",
                    concept_id=c_id,
                    source_origin="inaturalist_research_grade",
                    source_occurrence_id=str(item.get("id")),
                    original_scientific_name=taxon_info.get("name", species_name),
                    taxonomy_authority="iNaturalist-2026",
                    observed_at=now,
                    latitude=lat,
                    longitude=lon,
                    location_semantics=loc_semantics,
                    geoprivacy=geoprivacy,
                    coordinate_uncertainty_m=uncertainty_m,
                    source_dataset_id="iNaturalist Research Grade v1",
                    raw_payload=item,
                )
            )

        return occurrences
