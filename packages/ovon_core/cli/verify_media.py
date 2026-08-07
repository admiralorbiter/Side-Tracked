"""CLI Media Asset & Manifest Verification Script."""

import hashlib
import json
import sys
from pathlib import Path

from packages.ovon_core.media.provider import normalize_and_validate_license


def verify_media_manifest(manifest_path: Path | str = "data/media_manifest.json", cache_dir: Path | str = "media/cached") -> bool:
    manifest_path = Path(manifest_path)
    cache_dir = Path(cache_dir)

    print("=" * 60)
    print("      SIDETRACK SPECIES MEDIA & MANIFEST VERIFICATION")
    print("=" * 60)

    success = True

    if not manifest_path.exists():
        print(f"[FAIL] Manifest file {manifest_path} not found.")
        return False

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"[FAIL] Manifest file is invalid JSON: {e}")
        return False

    assets = manifest.get("assets", [])
    print(f"[OK] Manifest version: {manifest.get('version')} | Assets count: {len(assets)}")

    missing_attributions = 0
    invalid_licenses = 0
    missing_cached_files = 0
    checksum_mismatches = 0

    for asset in assets:
        asset_id = asset.get("asset_id", "")
        lic_str = asset.get("license", "")
        creator = asset.get("creator", "")
        attribution = asset.get("attribution_text", "")
        common_name = asset.get("common_name", "")

        # 1. License Check
        try:
            normalize_and_validate_license(lic_str)
        except Exception as e:
            print(f"[FAIL] {asset_id} ({common_name}): Invalid or disallowed license '{lic_str}': {e}")
            invalid_licenses += 1
            success = False

        # 2. Attribution & Creator Check
        if not creator or not attribution:
            print(f"[FAIL] {asset_id} ({common_name}): Missing creator or attribution text.")
            missing_attributions += 1
            success = False

        # 3. Cached binary file check
        cached_rel = asset.get("cached_path")
        if cached_rel:
            file_path = Path(cached_rel)
        else:
            # Check by asset_id in cache_dir
            matching = list(cache_dir.glob(f"{asset_id}.*"))
            file_path = matching[0] if matching else cache_dir / f"{asset_id}.jpg"

        if not file_path.exists() or file_path.stat().st_size == 0:
            print(f"[FAIL] {asset_id} ({common_name}): Cached media file {file_path} missing or empty.")
            missing_cached_files += 1
            success = False
        else:
            # Integrity check if sha256 in manifest
            expected_sha = asset.get("sha256")
            if expected_sha:
                h = hashlib.sha256()
                with open(file_path, "rb") as bf:
                    while chunk := bf.read(65536):
                        h.update(chunk)
                computed = h.hexdigest()
                if computed != expected_sha:
                    print(f"[FAIL] {asset_id} ({common_name}): SHA256 mismatch!")
                    checksum_mismatches += 1
                    success = False

    print("\n--- Media Verification Results ---")
    print(f"Total Assets Checked: {len(assets)}")
    print(f"Invalid Licenses: {invalid_licenses}")
    print(f"Missing Attributions: {missing_attributions}")
    print(f"Missing Cached Files: {missing_cached_files}")
    print(f"Checksum Mismatches: {checksum_mismatches}")

    print("=" * 60)
    if success:
        print("SUCCESS: ALL MEDIA MANIFEST AND CACHED FILE CHECKS PASSED!")
    else:
        print("FAILURE: MEDIA VERIFICATION CHECKS FAILED.")
    print("=" * 60)

    return success


if __name__ == "__main__":
    ok = verify_media_manifest()
    sys.exit(0 if ok else 1)
