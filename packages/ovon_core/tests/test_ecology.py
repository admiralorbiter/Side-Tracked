"""Unit and integration tests for deterministic ecological models and pilot catalog (Sprint 6)."""

import json
from pathlib import Path

import pytest
from packages.ovon_core.domain import Coordinate, TaxonRef
from packages.ovon_core.ecology import HabitatType, SpeciesProbabilitySurface
from packages.ovon_core.fixtures.kansas_city import KC_PARK_ENTRANCES
from packages.ovon_core.spatial import is_within_us_bounds, lat_lng_to_h3_cell


def test_park_entrances_catalog():
    assert len(KC_PARK_ENTRANCES) >= 5
    for entrance in KC_PARK_ENTRANCES:
        assert is_within_us_bounds(entrance.coordinate)
        assert "h3_res8" in entrance.cell.to_string()
        assert entrance.access_status == "open_public"


def test_species_probability_surface_determinism():
    surface = SpeciesProbabilitySurface()
    cardinal = TaxonRef.create("Northern Cardinal", "Cardinalis cardinalis", "norcar")
    cell = lat_lng_to_h3_cell(Coordinate(39.0347, -94.5906), resolution=8)

    # 100% Reproducible: Same parameters return exact same probability
    p1 = surface.get_probability(cardinal, HabitatType.MATURE_CANOPY, cell)
    p2 = surface.get_probability(cardinal, HabitatType.MATURE_CANOPY, cell)

    assert p1 == p2
    assert 0.0 <= p1 <= 1.0


def test_kc_pilot_manifest_file():
    manifest_path = Path("data/manifests/kc_pilot_manifest.json")
    assert manifest_path.exists()

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["manifest_version"] == "0.2-kc-pilot"
    assert data["taxonomy_version"] == "Clements-2025"
    assert "amerob" in data["species_frequencies"]
