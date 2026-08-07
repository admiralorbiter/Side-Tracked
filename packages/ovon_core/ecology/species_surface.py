"""Deterministic Provisional Species Surface Model for OVON Core."""

import hashlib
from dataclasses import dataclass, field

from packages.ovon_core.domain.spatial import SpatialCellId
from packages.ovon_core.domain.taxonomy import TaxonRef
from packages.ovon_core.ecology.habitat import HabitatType

# Baseline provisional detectability scores relative to habitat type across 30 KC species
BASELINE_PROVISIONAL_SCORES: dict[tuple[str, HabitatType], float] = {
    # Woodland & Canopy
    ("dowwoo", HabitatType.OPEN_PARKLAND): 0.35, ("dowwoo", HabitatType.MATURE_CANOPY): 0.85, ("dowwoo", HabitatType.POND_WATER_EDGE): 0.40, ("dowwoo", HabitatType.ORCHARD_EDGE): 0.70,
    ("rebwoo", HabitatType.OPEN_PARKLAND): 0.40, ("rebwoo", HabitatType.MATURE_CANOPY): 0.90, ("rebwoo", HabitatType.POND_WATER_EDGE): 0.45, ("rebwoo", HabitatType.ORCHARD_EDGE): 0.75,
    ("wbnut", HabitatType.OPEN_PARKLAND): 0.30, ("wbnut", HabitatType.MATURE_CANOPY): 0.88, ("wbnut", HabitatType.POND_WATER_EDGE): 0.35, ("wbnut", HabitatType.ORCHARD_EDGE): 0.65,
    ("bkcchi", HabitatType.OPEN_PARKLAND): 0.60, ("bkcchi", HabitatType.MATURE_CANOPY): 0.85, ("bkcchi", HabitatType.POND_WATER_EDGE): 0.50, ("bkcchi", HabitatType.ORCHARD_EDGE): 0.80,
    ("tuftit", HabitatType.OPEN_PARKLAND): 0.40, ("tuftit", HabitatType.MATURE_CANOPY): 0.80, ("tuftit", HabitatType.POND_WATER_EDGE): 0.35, ("tuftit", HabitatType.ORCHARD_EDGE): 0.60,
    ("ghowl", HabitatType.OPEN_PARKLAND): 0.10, ("ghowl", HabitatType.MATURE_CANOPY): 0.65, ("ghowl", HabitatType.POND_WATER_EDGE): 0.30, ("ghowl", HabitatType.ORCHARD_EDGE): 0.20,
    ("coohaw", HabitatType.OPEN_PARKLAND): 0.25, ("coohaw", HabitatType.MATURE_CANOPY): 0.60, ("coohaw", HabitatType.POND_WATER_EDGE): 0.30, ("coohaw", HabitatType.ORCHARD_EDGE): 0.45,
    ("barowl", HabitatType.OPEN_PARKLAND): 0.05, ("barowl", HabitatType.MATURE_CANOPY): 0.70, ("barowl", HabitatType.POND_WATER_EDGE): 0.50, ("barowl", HabitatType.ORCHARD_EDGE): 0.15,

    # Parkland, Open & Edges
    ("amerob", HabitatType.OPEN_PARKLAND): 0.85, ("amerob", HabitatType.MATURE_CANOPY): 0.45, ("amerob", HabitatType.POND_WATER_EDGE): 0.60, ("amerob", HabitatType.ORCHARD_EDGE): 0.70,
    ("norcar", HabitatType.OPEN_PARKLAND): 0.75, ("norcar", HabitatType.MATURE_CANOPY): 0.80, ("norcar", HabitatType.POND_WATER_EDGE): 0.90, ("norcar", HabitatType.ORCHARD_EDGE): 0.85,
    ("blujay", HabitatType.OPEN_PARKLAND): 0.65, ("blujay", HabitatType.MATURE_CANOPY): 0.75, ("blujay", HabitatType.POND_WATER_EDGE): 0.50, ("blujay", HabitatType.ORCHARD_EDGE): 0.70,
    ("rehwoo", HabitatType.OPEN_PARKLAND): 0.20, ("rehwoo", HabitatType.MATURE_CANOPY): 0.85, ("rehwoo", HabitatType.POND_WATER_EDGE): 0.40, ("rehwoo", HabitatType.ORCHARD_EDGE): 0.65,
    ("easblu", HabitatType.OPEN_PARKLAND): 0.80, ("easblu", HabitatType.MATURE_CANOPY): 0.30, ("easblu", HabitatType.POND_WATER_EDGE): 0.45, ("easblu", HabitatType.ORCHARD_EDGE): 0.75,
    ("amegfi", HabitatType.OPEN_PARKLAND): 0.75, ("amegfi", HabitatType.MATURE_CANOPY): 0.35, ("amegfi", HabitatType.POND_WATER_EDGE): 0.50, ("amegfi", HabitatType.ORCHARD_EDGE): 0.85,
    ("sonspa", HabitatType.OPEN_PARKLAND): 0.70, ("sonspa", HabitatType.MATURE_CANOPY): 0.25, ("sonspa", HabitatType.POND_WATER_EDGE): 0.80, ("sonspa", HabitatType.ORCHARD_EDGE): 0.75,
    ("houwre", HabitatType.OPEN_PARKLAND): 0.65, ("houwre", HabitatType.MATURE_CANOPY): 0.40, ("houwre", HabitatType.POND_WATER_EDGE): 0.50, ("houwre", HabitatType.ORCHARD_EDGE): 0.80,
    ("moudov", HabitatType.OPEN_PARKLAND): 0.85, ("moudov", HabitatType.MATURE_CANOPY): 0.30, ("moudov", HabitatType.POND_WATER_EDGE): 0.40, ("moudov", HabitatType.ORCHARD_EDGE): 0.70,
    ("norfli", HabitatType.OPEN_PARKLAND): 0.70, ("norfli", HabitatType.MATURE_CANOPY): 0.60, ("norfli", HabitatType.POND_WATER_EDGE): 0.35, ("norfli", HabitatType.ORCHARD_EDGE): 0.65,

    # Water & Riparian Edge
    ("grbher", HabitatType.OPEN_PARKLAND): 0.15, ("grbher", HabitatType.MATURE_CANOPY): 0.20, ("grbher", HabitatType.POND_WATER_EDGE): 0.95, ("grbher", HabitatType.ORCHARD_EDGE): 0.10,
    ("belkin", HabitatType.OPEN_PARKLAND): 0.10, ("belkin", HabitatType.MATURE_CANOPY): 0.30, ("belkin", HabitatType.POND_WATER_EDGE): 0.92, ("belkin", HabitatType.ORCHARD_EDGE): 0.15,
    ("mallar3", HabitatType.OPEN_PARKLAND): 0.40, ("mallar3", HabitatType.MATURE_CANOPY): 0.10, ("mallar3", HabitatType.POND_WATER_EDGE): 0.98, ("mallar3", HabitatType.ORCHARD_EDGE): 0.20,
    ("wooduc", HabitatType.OPEN_PARKLAND): 0.10, ("wooduc", HabitatType.MATURE_CANOPY): 0.45, ("wooduc", HabitatType.POND_WATER_EDGE): 0.88, ("wooduc", HabitatType.ORCHARD_EDGE): 0.25,
    ("greher", HabitatType.OPEN_PARKLAND): 0.05, ("greher", HabitatType.MATURE_CANOPY): 0.25, ("greher", HabitatType.POND_WATER_EDGE): 0.85, ("greher", HabitatType.ORCHARD_EDGE): 0.10,
    ("sposand", HabitatType.OPEN_PARKLAND): 0.10, ("sposand", HabitatType.MATURE_CANOPY): 0.05, ("sposand", HabitatType.POND_WATER_EDGE): 0.82, ("sposand", HabitatType.ORCHARD_EDGE): 0.05,

    # Aerial & High Canopy
    ("cedwax", HabitatType.OPEN_PARKLAND): 0.25, ("cedwax", HabitatType.MATURE_CANOPY): 0.45, ("cedwax", HabitatType.POND_WATER_EDGE): 0.30, ("cedwax", HabitatType.ORCHARD_EDGE): 0.90,
    ("barswa", HabitatType.OPEN_PARKLAND): 0.80, ("barswa", HabitatType.MATURE_CANOPY): 0.15, ("barswa", HabitatType.POND_WATER_EDGE): 0.85, ("barswa", HabitatType.ORCHARD_EDGE): 0.60,
    ("chiswi", HabitatType.OPEN_PARKLAND): 0.85, ("chiswi", HabitatType.MATURE_CANOPY): 0.30, ("chiswi", HabitatType.POND_WATER_EDGE): 0.65, ("chiswi", HabitatType.ORCHARD_EDGE): 0.50,
    ("balori", HabitatType.OPEN_PARKLAND): 0.35, ("balori", HabitatType.MATURE_CANOPY): 0.85, ("balori", HabitatType.POND_WATER_EDGE): 0.60, ("balori", HabitatType.ORCHARD_EDGE): 0.80,
    ("rbgros", HabitatType.OPEN_PARKLAND): 0.30, ("rbgros", HabitatType.MATURE_CANOPY): 0.82, ("rbgros", HabitatType.POND_WATER_EDGE): 0.40, ("rbgros", HabitatType.ORCHARD_EDGE): 0.75,
    ("rethaw", HabitatType.OPEN_PARKLAND): 0.75, ("rethaw", HabitatType.MATURE_CANOPY): 0.50, ("rethaw", HabitatType.POND_WATER_EDGE): 0.30, ("rethaw", HabitatType.ORCHARD_EDGE): 0.60,
}


@dataclass(frozen=True, slots=True)
class ProvisionalSpeciesSurface:
    """Deterministic provisional species surface model evaluating relative score(species | habitat, H3 cell)."""

    taxonomy_version: str = "Clements-2025"
    custom_baseline: dict[tuple[str, HabitatType], float] = field(
        default_factory=lambda: dict(BASELINE_PROVISIONAL_SCORES)
    )

    def get_relative_score(
        self, taxon: TaxonRef, habitat: HabitatType, cell: SpatialCellId | None = None
    ) -> float:
        """Return deterministic relative score between 0.0 and 1.0."""
        key = (taxon.ebird_code.lower(), habitat)
        score = self.custom_baseline.get(key, 0.30)

        # Deterministic spatial cell modifier based on SHA256 digest (process-stable)
        if cell is not None:
            digest = hashlib.sha256(cell.to_string().encode("utf-8")).digest()
            cell_val = int.from_bytes(digest[:4], "big")
            modifier = (
                (cell_val % 101) - 50
            ) / 1000.0  # Modifies score by +/- 0.05 deterministically
            score = max(0.05, min(0.95, score + modifier))

        return round(score, 3)
