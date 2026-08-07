"""Wikimedia Commons Photo Adapter for Species Photography."""

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


class WikimediaProvider(MediaProvider):
    """Adapter for Wikimedia Commons species photography API."""

    BASE_API_URL = "https://commons.wikimedia.org/w/api.php"

    @property
    def source_name(self) -> str:
        return "Wikimedia Commons"

    def fetch_assets_for_taxon(self, taxon: TaxonRef, max_results: int = 5) -> Sequence[MediaAsset]:
        """Fetch open-licensed species photography from Wikimedia Commons."""
        params = (
            f"action=query&generator=search&gsrsearch={taxon.scientific_name.replace(' ', '+')}"
            f"&gsrnamespace=6&prop=imageinfo&iiprop=url|extmetadata&format=json"
        )
        url = f"{self.BASE_API_URL}?{params}"
        req = Request(url, headers={"User-Agent": "Sidetrack/1.0 (Ecological Navigation)"})

        try:
            with urlopen(req, timeout=5) as response:
                if response.status != 200:
                    return []
                data = json.loads(response.read().decode("utf-8"))
        except (URLError, TimeoutError, json.JSONDecodeError):
            return []

        pages = data.get("query", {}).get("pages", {})
        assets: list[MediaAsset] = []

        for page_id, page_info in pages.items():
            if len(assets) >= max_results:
                break

            image_infos = page_info.get("imageinfo", [])
            if not image_infos:
                continue

            info = image_infos[0]
            img_url = info.get("url", "")
            if not img_url:
                continue

            extmetadata = info.get("extmetadata", {})
            lic_short = extmetadata.get("LicenseShortName", {}).get("value", "").strip()
            if not lic_short:
                continue  # Reject missing license metadata

            artist_html = extmetadata.get("Artist", {}).get("value", "").strip()
            if not artist_html:
                continue  # Reject missing artist metadata

            # Clean HTML tags from artist string
            import re

            artist = re.sub(r"<[^>]+>", "", artist_html).strip()
            if not artist:
                continue

            try:
                license_type = normalize_and_validate_license(lic_short)
            except MissingAttributionError:
                continue  # Skip unpermitted licenses

            asset_id = f"wm-{page_id}"
            attribution = f"{artist} ({license_type.value} via Wikimedia Commons)"

            asset = MediaAsset(
                asset_id=asset_id,
                taxon_ref=taxon,
                media_type=MediaType.PHOTO,
                url=img_url,
                creator=artist,
                license=license_type,
                attribution_text=attribution,
                source_name=self.source_name,
                alt_text=f"Photograph of {taxon.common_name} by {artist}",
            )
            assets.append(asset)

        return assets
