"""Habitat Types for OVON Domain Models."""

from enum import Enum


class HabitatType(str, Enum):
    """Supported habitat types for species detectability models."""

    OPEN_PARKLAND = "Open Parkland"
    MATURE_CANOPY = "Mature Hardwood Forest"
    POND_WATER_EDGE = "Pond & Water Edge"
    ORCHARD_EDGE = "Overgrown Orchard Edge"
