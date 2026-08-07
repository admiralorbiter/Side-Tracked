"""File and Memory Backed Media Repository Implementation."""

import json
from pathlib import Path
from typing import Sequence

from packages.ovon_core.domain import (
    MediaAsset,
    MediaType,
    MissingAttributionError,
    TaxonRef,
)
from packages.ovon_core.media.provider import MediaRepository, normalize_and_validate_license


class LocalMediaRepository(MediaRepository):
    """File and Memory Backed Media Repository with JSON manifest persistence."""

    def __init__(self, manifest_path: Path | str | None = None):
        self._assets: dict[str, list[MediaAsset]] = {}  # taxon_id -> list of MediaAsset
        self.manifest_path = Path(manifest_path) if manifest_path else None
        if self.manifest_path and self.manifest_path.exists():
            self.load_manifest(self.manifest_path)

    def register_asset(self, asset: MediaAsset) -> None:
        """Register a media asset with mandatory attribution validation."""
        if not asset.attribution_text:
            raise MissingAttributionError(
                f"Asset {asset.asset_id} missing mandatory attribution text."
            )

        t_id = asset.taxon_ref.taxon_id
        if t_id not in self._assets:
            self._assets[t_id] = []

        # Avoid duplicate asset IDs
        if not any(a.asset_id == asset.asset_id for a in self._assets[t_id]):
            self._assets[t_id].append(asset)

    def get_assets_for_taxon(
        self, taxon: TaxonRef, media_type: MediaType | None = None
    ) -> Sequence[MediaAsset]:
        """Retrieve cached media assets for a taxon."""
        assets = self._assets.get(taxon.taxon_id, [])
        if media_type:
            return [a for a in assets if a.media_type == media_type]
        return tuple(assets)

    def load_manifest(self, path: Path) -> None:
        """Load media assets from a JSON manifest file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data.get("assets", []):
            taxon = TaxonRef.create(
                common_name=item["common_name"],
                scientific_name=item["scientific_name"],
                ebird_code=item["ebird_code"],
            )
            media_type = MediaType(item["media_type"])
            license_type = normalize_and_validate_license(item["license"])

            asset = MediaAsset(
                asset_id=item["asset_id"],
                taxon_ref=taxon,
                media_type=media_type,
                url=item["url"],
                creator=item["creator"],
                license=license_type,
                attribution_text=item["attribution_text"],
                source_name=item.get("source_name", "Xeno-Canto / Wikimedia"),
                alt_text=item.get("alt_text", ""),
            )
            self.register_asset(asset)

    def save_manifest(self, path: Path) -> None:
        """Save media assets to a versioned JSON manifest file."""
        assets_list: list[dict] = []

        for asset_group in self._assets.values():
            for a in asset_group:
                assets_list.append(
                    {
                        "asset_id": a.asset_id,
                        "ebird_code": a.taxon_ref.ebird_code,
                        "common_name": a.taxon_ref.common_name,
                        "scientific_name": a.taxon_ref.scientific_name,
                        "media_type": a.media_type.value,
                        "url": a.url,
                        "creator": a.creator,
                        "license": a.license.value,
                        "attribution_text": a.attribution_text,
                        "source_name": a.source_name,
                    }
                )

        manifest_data = {
            "version": "1.0",
            "assets_count": len(assets_list),
            "assets": assets_list,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)
