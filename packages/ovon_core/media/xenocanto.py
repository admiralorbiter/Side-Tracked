"""Xeno-Canto Audio Adapter for Bird Song & Call Recordings."""

import json
from typing import Sequence
from urllib.error import URLError
from urllib.request import Request, urlopen

from packages.ovon_core.domain import (
    MediaAsset,
    MediaType,
    MissingAttributionError,
    TaxonRef,
)
from packages.ovon_core.media.provider import MediaProvider, normalize_and_validate_license


class XenoCantoProvider(MediaProvider):
    """Adapter for Xeno-Canto bird audio recordings API."""

    BASE_API_URL = "https://xeno-canto.org/api/2/recordings"

    @property
    def source_name(self) -> str:
        return "Xeno-Canto"

    def fetch_assets_for_taxon(self, taxon: TaxonRef, max_results: int = 5) -> Sequence[MediaAsset]:
        """Fetch audio recordings for a taxon from Xeno-Canto API."""
        query = f"{taxon.scientific_name}"
        url = f"{self.BASE_API_URL}?query={query.replace(' ', '+')}"

        req = Request(url, headers={"User-Agent": "Sidetrack/1.0 (Ecological Navigation)"})

        try:
            with urlopen(req, timeout=5) as response:
                if response.status != 200:
                    return []
                data = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, json.JSONDecodeError):
            return []

        recordings = data.get("recordings", [])
        assets: list[MediaAsset] = []

        for rec in recordings:
            if len(assets) >= max_results:
                break

            # Filter by recording quality (prefer 'A' or 'B' rating)
            quality = rec.get("q", "C").upper()
            if quality not in ("A", "B"):
                continue

            raw_lic = rec.get("lic", "")
            if not raw_lic or not raw_lic.strip():
                continue  # Reject missing license

            lic_clean = raw_lic.split("/")[-2] if "/" in raw_lic else raw_lic
            try:
                license_type = normalize_and_validate_license(lic_clean)
            except MissingAttributionError:
                continue  # Skip unpermitted or invalid licenses

            creator = rec.get("rec", "").strip()
            if not creator:
                continue  # Reject missing creator

            rec_id = str(rec.get("id", ""))
            audio_url = rec.get("file", "")
            if not audio_url.startswith("http"):
                audio_url = (
                    f"https:{audio_url}"
                    if audio_url.startswith("//")
                    else f"https://xeno-canto.org/{rec_id}/download"
                )

            attribution = f"{creator} ({license_type.value} via Xeno-Canto #{rec_id})"

            asset = MediaAsset(
                asset_id=f"xc-{rec_id}",
                taxon_ref=taxon,
                media_type=MediaType.AUDIO,
                url=audio_url,
                creator=creator,
                license=license_type,
                attribution_text=attribution,
                source_name=self.source_name,
                alt_text=f"Song recording of {taxon.common_name} by {creator}",
            )
            assets.append(asset)

        return assets
