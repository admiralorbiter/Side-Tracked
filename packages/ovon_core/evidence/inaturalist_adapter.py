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
from packages.ovon_core.evidence.providers import (
    BaseOccurrenceProvider,
    ProviderFetchResult,
)


from datetime import timedelta


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
            f"inat_{min_lat:.2f}_{min_lon:.2f}_{max_lat:.2f}_{max_lon:.2f}".encode()
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
                        exp_dt = now_dt + timedelta(seconds=ttl_seconds)
                        cache_envelope = {
                            "fetched_at": now_dt.isoformat(),
                            "expires_at": exp_dt.isoformat(),
                            "ttl_seconds": ttl_seconds,
                            "provider": "inaturalist_research_grade",
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
            geo_raw = item.get("geojson") or {}
            coords = geo_raw.get("coordinates")
            if not coords or len(coords) < 2:
                continue  # Exclude records without valid coordinates

            lon = float(coords[0])
            lat = float(coords[1])

            obs_date_raw = item.get("time_observed_at") or item.get("observed_on_string")
            obs_dt = now
            if obs_date_raw:
                try:
                    obs_dt = datetime.fromisoformat(obs_date_raw.replace("Z", "+00:00")).replace(
                        tzinfo=timezone.utc
                    )
                except Exception:
                    continue  # Require valid parseable observation date
            else:
                continue

            days_old = (now - obs_dt).total_seconds() / 86400.0
            if days_old > days_window or days_old < 0:
                continue  # Enforce days_window strictly

            taxon_info = item.get("taxon") or {}
            species_name = (
                taxon_info.get("preferred_common_name") or taxon_info.get("name") or "Organism"
            )
            c_id = f"sidetrack_concept:{species_name.lower().replace(' ', '_')}"

            if concept_ids and c_id not in concept_ids:
                continue

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
                    observed_at=obs_dt,
                    latitude=lat,
                    longitude=lon,
                    location_semantics=loc_semantics,
                    geoprivacy=geoprivacy,
                    coordinate_uncertainty_m=uncertainty_m,
                    source_dataset_id="iNaturalist Research Grade v1",
                    raw_payload=item,
                )
            )

        return ProviderFetchResult(
            records=tuple(occurrences),
            status=status_str,
            cache_age_seconds=round(cache_age_sec, 1),
            error_kind=error_kind,
        )
