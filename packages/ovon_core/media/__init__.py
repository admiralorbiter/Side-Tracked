"""Species media asset and field cue schemas."""

from packages.ovon_core.media.provider import (
    NORMALIZED_LICENSE_MAP,
    MediaProvider,
    MediaRepository,
    normalize_and_validate_license,
)
from packages.ovon_core.media.repository import LocalMediaRepository
from packages.ovon_core.media.wikimedia import WikimediaProvider
from packages.ovon_core.media.xenocanto import XenoCantoProvider

__all__ = [
    "MediaProvider",
    "MediaRepository",
    "normalize_and_validate_license",
    "NORMALIZED_LICENSE_MAP",
    "XenoCantoProvider",
    "WikimediaProvider",
    "LocalMediaRepository",
]
