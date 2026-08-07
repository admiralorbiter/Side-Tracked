"""Structured Habitat Guilds and Ecological Profiles for Sidetrack Taxa."""

from dataclasses import dataclass
from enum import Enum
from typing import Literal

from packages.ovon_core.fixtures.kc_species_fixtures import ALL_KC_TAXA


class HabitatGuild(str, Enum):
    """Primary ecological habitat guilds for grouping species presentation."""

    WOODLAND = "woodland"
    OPEN_EDGE = "open_edge"
    WATER_RIPARIAN = "water_riparian"
    AERIAL = "aerial"

    @property
    def display_name(self) -> str:
        names = {
            HabitatGuild.WOODLAND: "🌲 Check the Canopy & Trunks",
            HabitatGuild.OPEN_EDGE: "🌻 Check the Lawn & Edge",
            HabitatGuild.WATER_RIPARIAN: "🌊 Watch the Creek & Shore",
            HabitatGuild.AERIAL: "🪁 Look Up Overhead",
        }
        return names.get(self, "🌿 Habitat Matches")


@dataclass(frozen=True, slots=True)
class TaxonEcologyProfile:
    """Ecological profile for a species including guilds and seasonal activity."""

    taxon_id: str
    primary_guild: HabitatGuild
    secondary_guilds: tuple[HabitatGuild, ...] = ()
    active_weeks: tuple[int, int] = (1, 52)
    activity_period: Literal["day", "night", "crepuscular", "variable"] = "day"


# Map 30 Kansas City species to their canonical HabitatGuild and profile
_GUILD_MAPPING: dict[str, tuple[HabitatGuild, tuple[HabitatGuild, ...]]] = {
    # Woodland & Canopy
    "dowwoo": (HabitatGuild.WOODLAND, ()),
    "rebwoo": (HabitatGuild.WOODLAND, ()),
    "wbnut": (HabitatGuild.WOODLAND, ()),
    "bkcchi": (HabitatGuild.WOODLAND, (HabitatGuild.OPEN_EDGE,)),
    "tuftit": (HabitatGuild.WOODLAND, ()),
    "ghowl": (HabitatGuild.WOODLAND, ()),
    "coohaw": (HabitatGuild.WOODLAND, (HabitatGuild.OPEN_EDGE,)),
    "barowl": (HabitatGuild.WOODLAND, (HabitatGuild.WATER_RIPARIAN,)),

    # Parkland, Open & Edges
    "amerob": (HabitatGuild.OPEN_EDGE, (HabitatGuild.WOODLAND,)),
    "norcar": (HabitatGuild.OPEN_EDGE, (HabitatGuild.WOODLAND,)),
    "blujay": (HabitatGuild.OPEN_EDGE, (HabitatGuild.WOODLAND,)),
    "rehwoo": (HabitatGuild.OPEN_EDGE, (HabitatGuild.WOODLAND,)),
    "easblu": (HabitatGuild.OPEN_EDGE, ()),
    "amegfi": (HabitatGuild.OPEN_EDGE, ()),
    "sonspa": (HabitatGuild.OPEN_EDGE, (HabitatGuild.WATER_RIPARIAN,)),
    "houwre": (HabitatGuild.OPEN_EDGE, (HabitatGuild.WOODLAND,)),
    "moudov": (HabitatGuild.OPEN_EDGE, ()),
    "norfli": (HabitatGuild.OPEN_EDGE, (HabitatGuild.WOODLAND,)),

    # Water & Riparian Edge
    "grbher": (HabitatGuild.WATER_RIPARIAN, ()),
    "belkin": (HabitatGuild.WATER_RIPARIAN, ()),
    "mallar3": (HabitatGuild.WATER_RIPARIAN, (HabitatGuild.OPEN_EDGE,)),
    "wooduc": (HabitatGuild.WATER_RIPARIAN, (HabitatGuild.WOODLAND,)),
    "greher": (HabitatGuild.WATER_RIPARIAN, ()),
    "sposand": (HabitatGuild.WATER_RIPARIAN, ()),

    # Aerial & High Canopy
    "cedwax": (HabitatGuild.AERIAL, (HabitatGuild.WOODLAND,)),
    "barswa": (HabitatGuild.AERIAL, (HabitatGuild.WATER_RIPARIAN,)),
    "chiswi": (HabitatGuild.AERIAL, ()),
    "balori": (HabitatGuild.AERIAL, (HabitatGuild.WOODLAND,)),
    "rbgros": (HabitatGuild.AERIAL, (HabitatGuild.WOODLAND,)),
    "rethaw": (HabitatGuild.AERIAL, (HabitatGuild.OPEN_EDGE,)),
}

KC_TAXON_ECOLOGY_PROFILES: dict[str, TaxonEcologyProfile] = {}
for _taxon in ALL_KC_TAXA:
    _primary, _secondary = _GUILD_MAPPING.get(_taxon.ebird_code, (HabitatGuild.OPEN_EDGE, ()))
    KC_TAXON_ECOLOGY_PROFILES[_taxon.ebird_code] = TaxonEcologyProfile(
        taxon_id=_taxon.taxon_id,
        primary_guild=_primary,
        secondary_guilds=_secondary,
    )
