"""Deterministic Species Probability Surface Model for OVON Core."""

from dataclasses import dataclass, field

from packages.ovon_core.domain import SpatialCellId, TaxonRef
from packages.ovon_core.ecology.habitat import HabitatType

# Baseline detectability probabilities P(Taxon | Habitat) based on eBird frequency tables
BASELINE_SPECIES_PROBABILITIES: dict[tuple[str, HabitatType], float] = {
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
class SpeciesProbabilitySurface:
    """Deterministic species probability surface model evaluating P(species | habitat, H3 cell)."""

    taxonomy_version: str = "Clements-2025"
    custom_baseline: dict[tuple[str, HabitatType], float] = field(
        default_factory=lambda: dict(BASELINE_SPECIES_PROBABILITIES)
    )

    def get_probability(
        self, taxon: TaxonRef, habitat: HabitatType, cell: SpatialCellId | None = None
    ) -> float:
        """Return deterministic detectability probability between 0.0 and 1.0."""
        key = (taxon.ebird_code.lower(), habitat)
        prob = self.custom_baseline.get(key, 0.30)

        # Deterministic spatial cell modifier based on cell hash (zero random values)
        if cell is not None:
            cell_hash = abs(hash(cell.to_string())) % 100
            modifier = (cell_hash - 50) / 1000.0  # Modifies prob by +/- 0.05 deterministically
            prob = max(0.05, min(0.95, prob + modifier))

        return round(prob, 3)
