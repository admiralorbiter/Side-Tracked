"""Habitat Radar Domain Read Models."""

from dataclasses import dataclass

from packages.ovon_core.domain.taxonomy import TaxonRef
from packages.ovon_core.ecology.ecology_profile import HabitatGuild


@dataclass(frozen=True, slots=True)
class RadarSpecies:
    """Evaluated species match in the habitat radar."""

    taxon: TaxonRef
    relative_score: float
    matched_segment_ids: tuple[int, ...]
    primary_guild: HabitatGuild
    support_tier: str = "Provisional Matrix"
    reason_codes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class HabitatRadar:
    """Habitat Radar read model providing segment and route species context."""

    focal: tuple[RadarSpecies, ...]
    nearby: tuple[RadarSpecies, ...]
    by_segment: dict[int, tuple[RadarSpecies, ...]]
    by_guild: dict[HabitatGuild, tuple[RadarSpecies, ...]]
    model_status: str = "Provisional Relative Index"
    catalog_version: str = "Clements-2025"
    total_catalog_matches: int = 0
