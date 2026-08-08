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
from packages.ovon_core.evidence.providers import (
    BaseOccurrenceProvider,
    ProviderFetchResult,
)


from datetime import timedelta


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
        res = self.fetch_result(bounding_box, concept_ids, days_window=days_window)
        return list(res.records)

    def fetch_result(
        self,
        bounding_box: tuple[float, float, float, float],
        concept_ids: Sequence[str],
        days_window: int = 30,
        ttl_seconds: int = 604800,  # 7-day default TTL
    ) -> ProviderFetchResult:
        """Fetch structured ProviderFetchResult with TTL cache validation."""
        min_lat, min_lon, max_lat, max_lon = bounding_box
        now_dt = datetime.now(timezone.utc)

        cache_key = hashlib.sha256(
            f"gbif_{min_lat:.2f}_{min_lon:.2f}_{max_lat:.2f}_{max_lon:.2f}".encode()
        ).hexdigest()[:12]
        cache_file = self.cache_dir / f"{cache_key}.json"

        raw_data = None
        cache_age_sec = 0.0
        if cache_file.exists():
            try:
                cache_envelope = json.loads(cache_file.read_text(encoding="utf-8"))
                fetched_at_str = cache_envelope.get("fetched_at")
                expires_at_str = cache_envelope.get("expires_at")

                if expires_at_str:
                    exp_dt = datetime.fromisoformat(expires_at_str).replace(tzinfo=timezone.utc)
                    if now_dt <= exp_dt:
                        raw_data = cache_envelope.get("raw_data")
                        if fetched_at_str:
                            f_dt = datetime.fromisoformat(fetched_at_str).replace(
                                tzinfo=timezone.utc
                            )
                            cache_age_sec = (now_dt - f_dt).total_seconds()
                else:
                    # Legacy un-enveloped cache support
                    raw_data = cache_envelope
            except Exception:
                raw_data = None

        error_kind = None
        status_str = "ok"

        if raw_data is None:
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
                        exp_dt = now_dt + timedelta(seconds=ttl_seconds)
                        cache_envelope = {
                            "fetched_at": now_dt.isoformat(),
                            "expires_at": exp_dt.isoformat(),
                            "ttl_seconds": ttl_seconds,
                            "provider": "gbif_occurrence",
                            "raw_data": raw_data,
                        }
                        cache_file.write_text(
                            json.dumps(cache_envelope, indent=2), encoding="utf-8"
                        )
            except Exception as exc:
                raw_data = {"results": []}
                status_str = "error"
                error_kind = str(exc)

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

        return ProviderFetchResult(
            records=tuple(occurrences),
            status=status_str,
            cache_age_seconds=round(cache_age_sec, 1),
            error_kind=error_kind,
        )
