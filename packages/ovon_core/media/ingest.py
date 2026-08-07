"""CLI Media Ingestion Script for Species Media Foundation."""

import argparse
import time
from pathlib import Path

from packages.ovon_core.domain import MediaType
from packages.ovon_core.fixtures.kc_species_fixtures import ALL_KC_TAXA
from packages.ovon_core.media.repository import LocalMediaRepository
from packages.ovon_core.media.wikimedia import WikimediaProvider


def run_ingestion(manifest_output: Path) -> None:
    """Run automated media ingestion pipeline for target taxa."""
    repo = LocalMediaRepository(manifest_output)
    wm_provider = WikimediaProvider()

    print(f"Starting Media Ingestion Pipeline for {len(ALL_KC_TAXA)} species...")

    for taxon in ALL_KC_TAXA:
        print(f"\nProcessing {taxon.common_name} ({taxon.scientific_name})...")
        time.sleep(0.15)

        # Fetch photo from Wikimedia Commons
        try:
            photo_assets = wm_provider.fetch_assets_for_taxon(taxon, max_results=1, media_type=MediaType.PHOTO)
            for a in photo_assets:
                repo.register_asset(a)
                print(f"  [PHOTO] {a.asset_id}: {a.attribution_text}")
        except Exception as e:
            print(f"  [PHOTO ERROR] Failed fetching photo for {taxon.common_name}: {e}")

        # Fetch audio from Wikimedia Commons
        try:
            audio_assets = wm_provider.fetch_assets_for_taxon(taxon, max_results=1, media_type=MediaType.AUDIO)
            for a in audio_assets:
                repo.register_asset(a)
                print(f"  [AUDIO] {a.asset_id}: {a.attribution_text}")
        except Exception as e:
            print(f"  [AUDIO ERROR] Failed fetching audio for {taxon.common_name}: {e}")

    # Save manifest
    repo.save_manifest(manifest_output)
    print(f"\n[OK] Media Ingestion Pipeline Complete! Manifest saved to: {manifest_output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest species media assets for Sidetrack.")
    parser.add_argument(
        "--output",
        type=str,
        default="data/media_manifest.json",
        help="Output path for media manifest JSON.",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    run_ingestion(output_path)
