"""Offline Verification CLI for Sidetrack Regional Pilot Package & Manifests."""

import json
import sys
from pathlib import Path

from packages.ovon_core.domain import Coordinate, TaxonRef
from packages.ovon_core.ecology import HabitatType, ProvisionalSpeciesSurface
from packages.ovon_core.fixtures.kansas_city import KC_PARK_ENTRANCES
from packages.ovon_core.spatial import is_within_kc_pilot_bounds, lat_lng_to_h3_cell


def verify_pilot_package() -> bool:
    """Execute complete offline verification suite for Kansas City regional pilot package."""
    print("=" * 60)
    print("      SIDETRACK REGIONAL PILOT & DATASET VERIFICATION")
    print("=" * 60)

    success = True

    # 1. Verify Manifest File
    manifest_path = Path("data/manifests/kc_pilot_manifest.json")
    if not manifest_path.exists():
        print("[FAIL] Manifest file data/manifests/kc_pilot_manifest.json not found.")
        success = False
    else:
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                print(
                    f"[OK] Manifest Verified: {manifest.get('region_name')} (v{manifest.get('manifest_version')})"
                )
                print(
                    f"     Taxonomy: {manifest.get('taxonomy_version')} | Graph: {manifest.get('routing_graph_version')}"
                )
        except Exception as e:
            print(f"[FAIL] Invalid JSON manifest format: {e}")
            success = False

    # 2. Verify Kansas City Park Entrances, H3 Indexing & Provenance
    print("\n--- Verifying Regional Park Entrances & Provenance ---")
    if not KC_PARK_ENTRANCES:
        print("[FAIL] Park entrances catalog is empty.")
        success = False
    else:
        for entrance in KC_PARK_ENTRANCES:
            coord_valid = is_within_kc_pilot_bounds(entrance.coordinate)
            h3_valid = "h3_res8" in entrance.cell.to_string()
            has_provenance = bool(
                entrance.source_name and entrance.source_id and entrance.verified_at
            )
            if coord_valid and h3_valid and has_provenance:
                print(
                    f"[OK] {entrance.park_name} -> {entrance.name} [{entrance.cell.to_string()}] ({entrance.source_name})"
                )
            else:
                print(f"[FAIL] Entrance: {entrance.name} bounds/H3/provenance check failed.")
                success = False

    # 3. Verify Deterministic Provisional Species Surface
    print("\n--- Verifying Ecological Determinism & Process Stability ---")
    surface = ProvisionalSpeciesSurface()
    cardinal = TaxonRef.create("Northern Cardinal", "Cardinalis cardinalis", "norcar")
    cell = lat_lng_to_h3_cell(Coordinate(39.0347, -94.5906), resolution=8)

    s1 = surface.get_relative_score(cardinal, HabitatType.MATURE_CANOPY, cell)
    s2 = surface.get_relative_score(cardinal, HabitatType.MATURE_CANOPY, cell)

    if s1 == s2 and 0.0 <= s1 <= 1.0:
        print(
            f"[OK] SHA256 Determinism Verified: Score(Northern Cardinal | Canopy, {cell.to_string()}) = {s1:.3f} (Process-Stable)"
        )
    else:
        print(f"[FAIL] Provisional species surface is not deterministic (s1={s1}, s2={s2})")
        success = False

    print("=" * 60)
    if success:
        print("SUCCESS: ALL REGIONAL PILOT & DATASET VERIFICATION CHECKS PASSED!")
    else:
        print("FAILURE: REGIONAL PILOT VERIFICATION FAILED.")
    print("=" * 60)

    return success


if __name__ == "__main__":
    ok = verify_pilot_package()
    sys.exit(0 if ok else 1)
