"""Offline Verification CLI for Sidetrack Regional Pilot Package & Manifests."""

import json
from pathlib import Path
import sys

from packages.ovon_core.domain import Coordinate, TaxonRef
from packages.ovon_core.ecology import HabitatType, SpeciesProbabilitySurface
from packages.ovon_core.fixtures.kansas_city import KC_PARK_ENTRANCES
from packages.ovon_core.spatial import is_within_us_bounds, lat_lng_to_h3_cell


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

    # 2. Verify Kansas City Park Entrances & H3 Indexing
    print("\n--- Verifying Regional Park Entrances ---")
    if not KC_PARK_ENTRANCES:
        print("[FAIL] Park entrances catalog is empty.")
        success = False
    else:
        for entrance in KC_PARK_ENTRANCES:
            coord_valid = is_within_us_bounds(entrance.coordinate)
            h3_valid = "h3_res8" in entrance.cell.to_string()
            if coord_valid and h3_valid:
                print(f"[OK] {entrance.park_name} -> {entrance.name} [{entrance.cell.to_string()}]")
            else:
                print(f"[FAIL] Entrance: {entrance.name} bounds/H3 check failed.")
                success = False

    # 3. Verify Deterministic Species Probability Surface
    print("\n--- Verifying Ecological Determinism ---")
    surface = SpeciesProbabilitySurface()
    cardinal = TaxonRef.create("Northern Cardinal", "Cardinalis cardinalis", "norcar")
    cell = lat_lng_to_h3_cell(Coordinate(39.0347, -94.5906), resolution=8)

    p1 = surface.get_probability(cardinal, HabitatType.MATURE_CANOPY, cell)
    p2 = surface.get_probability(cardinal, HabitatType.MATURE_CANOPY, cell)

    if p1 == p2 and 0.0 <= p1 <= 1.0:
        print(
            f"[OK] Determinism Verified: P(Northern Cardinal | Canopy, {cell.to_string()}) = {p1:.3f} (100% reproducible)"
        )
    else:
        print(f"[FAIL] Species probability surface is not deterministic (p1={p1}, p2={p2})")
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
