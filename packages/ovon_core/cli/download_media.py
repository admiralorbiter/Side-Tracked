"""CLI script to download Creative Commons species media assets locally."""

import argparse
import sys
from pathlib import Path

from packages.ovon_core.media.downloader import MediaDownloader


def main() -> int:
    parser = argparse.ArgumentParser(description="Download Creative Commons species media assets for Sidetrack.")
    parser.add_argument(
        "--manifest",
        type=str,
        default="data/media_manifest.json",
        help="Path to media manifest JSON.",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default="media/cached",
        help="Target directory for cached media files.",
    )
    args = parser.parse_args()

    downloader = MediaDownloader(manifest_path=Path(args.manifest), cache_dir=Path(args.cache_dir))
    summary = downloader.download_all_assets()

    if summary["failed"] > 0:
        print(f"\n[WARNING] {summary['failed']} media downloads failed.")
        return 1

    print("\n[OK] All Creative Commons media assets successfully downloaded and cached!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
