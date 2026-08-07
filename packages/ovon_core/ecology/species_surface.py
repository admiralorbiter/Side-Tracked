"""Deterministic Provisional Species Surface Model for OVON Core."""

import hashlib
from dataclasses import dataclass, field

from packages.ovon_core.domain import SpatialCellId, TaxonRef
from packages.ovon_core.ecology.habitat import HabitatType

# Baseline provisional detectability scores relative to habitat type
BASELINE_PROVISIONAL_SCORES: dict[tuple[str, HabitatType], float] = {
    # American Robin (amerob)
    ("amerob", HabitatType.OPEN_PARKLAND): 0.85,
    ("amerob", HabitatType.MATURE_CANOPY): 0.45,
    ("amerob", HabitatType.POND_WATER_EDGE): 0.60,
    ("amerob", HabitatType.ORCHARD_EDGE): 0.70,
    # Northern Cardinal (norcar)
    ("norcar", HabitatType.OPEN_PARKLAND): 0.75,
    ("norcar", HabitatType.MATURE_CANOPY): 0.80,
    ("norcar", HabitatType.POND_WATER_EDGE): 0.90,
    ("norcar", HabitatType.ORCHARD_EDGE): 0.85,
    # Blue Jay (blujay)
    ("blujay", HabitatType.OPEN_PARKLAND): 0.65,
    ("blujay", HabitatType.MATURE_CANOPY): 0.75,
    ("blujay", HabitatType.POND_WATER_EDGE): 0.50,
    ("blujay", HabitatType.ORCHARD_EDGE): 0.70,
    # Red-headed Woodpecker (rehwoo)
    ("rehwoo", HabitatType.OPEN_PARKLAND): 0.20,
    ("rehwoo", HabitatType.MATURE_CANOPY): 0.85,
    ("rehwoo", HabitatType.POND_WATER_EDGE): 0.40,
    ("rehwoo", HabitatType.ORCHARD_EDGE): 0.65,
    # Tufted Titmouse (tuftit)
    ("tuftit", HabitatType.OPEN_PARKLAND): 0.40,
    ("tuftit", HabitatType.MATURE_CANOPY): 0.80,
    ("tuftit", HabitatType.POND_WATER_EDGE): 0.35,
    ("tuftit", HabitatType.ORCHARD_EDGE): 0.60,
    # Carolina Wren (carwre)
    ("carwre", HabitatType.OPEN_PARKLAND): 0.30,
    ("carwre", HabitatType.MATURE_CANOPY): 0.75,
    ("carwre", HabitatType.POND_WATER_EDGE): 0.55,
    ("carwre", HabitatType.ORCHARD_EDGE): 0.80,
    # Cedar Waxwing (cedwax)
    ("cedwax", HabitatType.OPEN_PARKLAND): 0.25,
    ("cedwax", HabitatType.MATURE_CANOPY): 0.45,
    ("cedwax", HabitatType.POND_WATER_EDGE): 0.30,
    ("cedwax", HabitatType.ORCHARD_EDGE): 0.90,
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
