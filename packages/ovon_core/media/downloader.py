"""Downloader utility for caching Creative Commons species media assets locally."""

import hashlib
import json
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class MediaDownloader:
    """Safely downloads and caches Creative Commons media assets with SHA256 integrity verification."""

    USER_AGENT = "SidetrackApp/1.0 (https://github.com/admiralorbiter/Side-Tracked; contact@sidetrack.app)"

    def __init__(self, manifest_path: Path | str, cache_dir: Path | str):
        self.manifest_path = Path(manifest_path)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def download_all_assets(self, max_retries: int = 3, timeout: float = 15.0) -> dict[str, Any]:
        """Download all assets from manifest into cache_dir and update checksums/cached_paths."""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {self.manifest_path}")

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        assets = manifest.get("assets", [])
        print(f"Starting download of {len(assets)} media assets to {self.cache_dir}...")

        downloaded_count = 0
        existing_count = 0
        failed_count = 0

        for idx, asset in enumerate(assets, start=1):
            asset_id = asset["asset_id"]
            url = asset["url"]
            media_type = asset.get("media_type", "photo")
            common_name = asset.get("common_name", "Unknown Species")

            # Determine extension
            ext = self._determine_extension(url, media_type)
            file_name = f"{asset_id}{ext}"
            file_path = self.cache_dir / file_name

            # Check if file already exists and is non-empty
            if file_path.exists() and file_path.stat().st_size > 0:
                existing_count += 1
                checksum = self._compute_sha256(file_path)
                asset["cached_path"] = f"media/cached/{file_name}"
                asset["sha256"] = checksum
                print(f"  [{idx}/{len(assets)}] [EXISTS] {common_name} ({asset_id}) -> {file_name}")
                continue

            print(f"  [{idx}/{len(assets)}] [DOWNLOADING] {common_name} ({asset_id})...", end="", flush=True)

            success = False
            for attempt in range(1, max_retries + 1):
                try:
                    req = Request(url, headers={"User-Agent": self.USER_AGENT})
                    with urlopen(req, timeout=timeout) as resp:
                        content = resp.read()
                        if not content:
                            raise ValueError("Received 0 bytes response")

                        # Write to file atomically via temp file
                        temp_path = file_path.with_suffix(f"{ext}.tmp")
                        with open(temp_path, "wb") as out:
                            out.write(content)
                        temp_path.replace(file_path)

                        checksum = self._compute_sha256(file_path)
                        asset["cached_path"] = f"media/cached/{file_name}"
                        asset["sha256"] = checksum
                        downloaded_count += 1
                        success = True
                        print(f" DONE ({len(content)} bytes)")
                        time.sleep(1.0)  # Throttling to respect Wikimedia rate limits
                        break
                except HTTPError as err:
                    if err.code == 429:
                        wait_time = 3.0 * (2 ** attempt)
                        print(f" [429 Rate Limit - Sleeping {wait_time:.1f}s]...", end="", flush=True)
                        time.sleep(wait_time)
                    elif attempt < max_retries:
                        time.sleep(1.0 * attempt)
                    else:
                        failed_count += 1
                        print(f" FAILED: {err}")
                except (URLError, TimeoutError, ValueError, Exception) as err:
                    if attempt < max_retries:
                        time.sleep(1.0 * attempt)
                    else:
                        failed_count += 1
                        print(f" FAILED: {err}")

            time.sleep(0.1)

        # Save updated manifest with cached_path and sha256 checksums
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        summary = {
            "total": len(assets),
            "downloaded": downloaded_count,
            "existing": existing_count,
            "failed": failed_count,
        }
        print(f"\nDownload summary: {summary['downloaded']} downloaded, {summary['existing']} pre-existing, {summary['failed']} failed out of {summary['total']} total assets.")
        return summary

    @staticmethod
    def _determine_extension(url: str, media_type: str) -> str:
        url_lower = url.lower().split("?")[0]
        if url_lower.endswith(".ogg"):
            return ".ogg"
        if url_lower.endswith(".mp3"):
            return ".mp3"
        if url_lower.endswith(".wav"):
            return ".wav"
        if url_lower.endswith(".png"):
            return ".png"
        if url_lower.endswith(".webp"):
            return ".webp"
        if url_lower.endswith(".jpg") or url_lower.endswith(".jpeg"):
            return ".jpg"

        return ".ogg" if media_type == "audio" else ".jpg"

    @staticmethod
    def _compute_sha256(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
