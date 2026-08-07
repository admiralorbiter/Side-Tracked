"""Unit and integration tests for deterministic ecological models and pilot catalog (Sprint 7)."""

import json
from pathlib import Path

from packages.ovon_core.cli.verify_pilot import verify_pilot_package
from packages.ovon_core.domain import Coordinate, TaxonRef
from packages.ovon_core.ecology import HabitatType, ProvisionalSpeciesSurface
from packages.ovon_core.fixtures.kansas_city import KC_PARK_ENTRANCES
from packages.ovon_core.spatial import (
    is_within_kc_pilot_bounds,
    lat_lng_to_h3_cell,
    polyline_to_h3_cells,
)


def test_park_entrances_catalog():
    assert len(KC_PARK_ENTRANCES) >= 5
    for entrance in KC_PARK_ENTRANCES:
        assert is_within_kc_pilot_bounds(entrance.coordinate)
        assert "h3_res8" in entrance.cell.to_string()
        assert entrance.access_status == "verified_public"
        assert entrance.parking_status == "verified"
        assert entrance.source_name == "KC Parks & Rec Catalog"


def test_provisional_species_surface_determinism():
    surface = ProvisionalSpeciesSurface()
    cardinal = TaxonRef.create("Northern Cardinal", "Cardinalis cardinalis", "norcar")
    cell = lat_lng_to_h3_cell(Coordinate(39.0347, -94.5906), resolution=8)

    # 100% Reproducible: Same parameters return exact same relative score
    s1 = surface.get_relative_score(cardinal, HabitatType.MATURE_CANOPY, cell)
    s2 = surface.get_relative_score(cardinal, HabitatType.MATURE_CANOPY, cell)

    assert s1 == s2
    assert 0.0 <= s1 <= 1.0


def test_polyline_to_h3_cells_traversal():
    geom = {
        "type": "LineString",
        "coordinates": [
            [-94.5906, 39.0347],
            [-94.5910, 39.0350],
            [-94.5915, 39.0355],
        ],
    }
    cells = polyline_to_h3_cells(geom, resolution=8)
    assert len(cells) > 0
    for c in cells:
        assert "h3_res8" in c.to_string()


def test_verify_pilot_cli_integration():
    assert verify_pilot_package() is True


def test_kc_pilot_manifest_file():
    manifest_path = Path("data/manifests/kc_pilot_manifest.json")
    assert manifest_path.exists()

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["manifest_version"] == "0.2-kc-pilot"
    assert data["taxonomy_version"] == "Clements-2025"
    assert "amerob" in data["species_frequencies"]
