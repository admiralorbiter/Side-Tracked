"""CLI Media Ingestion Script for Species Media Foundation."""

import argparse
from pathlib import Path

from packages.ovon_core.domain import TaxonRef
from packages.ovon_core.media.repository import LocalMediaRepository
from packages.ovon_core.media.wikimedia import WikimediaProvider
from packages.ovon_core.media.xenocanto import XenoCantoProvider

# Starter Pack of Kansas City Birds for Sprint 3
STARTER_KC_BIRDS = [
    ("Red-headed Woodpecker", "Melanerpes erythrocephalus", "rehwoo"),
    ("American Robin", "Turdus migratorius", "amerob"),
    ("Northern Cardinal", "Cardinalis cardinalis", "norcar"),
    ("Blue Jay", "Cyanocitta cristata", "blujay"),
    ("Tufted Titmouse", "Baeolophus bicolor", "tuftit"),
    ("Carolina Wren", "Thryothorus ludovicianus", "carwre"),
    ("Cedar Waxwing", "Bombycilla cedrorum", "cedwax"),
]


def run_ingestion(manifest_output: Path) -> None:
    """Run automated media ingestion pipeline for target taxa."""
    repo = LocalMediaRepository()
    xc_provider = XenoCantoProvider()
    wm_provider = WikimediaProvider()

    print(f"Starting Media Ingestion Pipeline for {len(STARTER_KC_BIRDS)} species...")

    for common_name, sci_name, ebird_code in STARTER_KC_BIRDS:
        taxon = TaxonRef.create(common_name, sci_name, ebird_code)
        print(f"\nProcessing {common_name} ({sci_name})...")

        # Fetch audio from Xeno-Canto
        try:
            audio_assets = xc_provider.fetch_assets_for_taxon(taxon, max_results=2)
            for a in audio_assets:
                repo.register_asset(a)
                print(f"  [AUDIO] {a.asset_id}: {a.attribution_text}")
        except Exception as e:
            print(f"  [AUDIO ERROR] Failed fetching audio for {common_name}: {e}")

        # Fetch photo from Wikimedia Commons
        try:
            photo_assets = wm_provider.fetch_assets_for_taxon(taxon, max_results=2)
            for a in photo_assets:
                repo.register_asset(a)
                print(f"  [PHOTO] {a.asset_id}: {a.attribution_text}")
        except Exception as e:
            print(f"  [PHOTO ERROR] Failed fetching photo for {common_name}: {e}")

    # Save manifest
    repo.save_manifest(manifest_output)
    print(f"\n✅ Media Ingestion Pipeline Complete! Manifest saved to: {manifest_output}")


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
