from dataclasses import dataclass
from enum import Enum

from packages.ovon_core.domain.errors import MissingAttributionError
from packages.ovon_core.domain.taxonomy import TaxonRef


class LicenseType(str, Enum):
    """Supported Creative Commons and Open Media Licenses."""

    CC_BY_4_0 = "CC BY 4.0"
    CC_BY_NC_4_0 = "CC BY-NC 4.0"
    CC_BY_SA_4_0 = "CC BY-SA 4.0"
    CC0_1_0 = "CC0 1.0"
    PUBLIC_DOMAIN = "Public Domain"


class MediaType(str, Enum):
    """Supported Species Media Asset Types."""

    PHOTO = "photo"
    AUDIO = "audio"


@dataclass(frozen=True, slots=True)
class MediaAsset:
    """Immutable Species Media Asset with mandatory licensing & attribution."""

    asset_id: str
    taxon_ref: TaxonRef
    media_type: MediaType
    url: str
    creator: str
    license: LicenseType
    attribution_text: str
    source_name: str = "Xeno-Canto / Wikimedia"
    alt_text: str = ""

    def __post_init__(self) -> None:
        if not self.asset_id or not self.asset_id.strip():
            raise MissingAttributionError("MediaAsset requires a non-empty asset_id.")
        if not self.url or not self.url.strip():
            raise MissingAttributionError("MediaAsset requires a non-empty url.")
        if not self.creator or not self.creator.strip():
            raise MissingAttributionError("MediaAsset requires a non-empty creator.")
        if not self.attribution_text or not self.attribution_text.strip():
            raise MissingAttributionError("MediaAsset requires non-empty attribution_text.")


@dataclass(frozen=True, slots=True)
class FieldCue:
    """Structured observation cue for species detection in the field."""

    taxon_ref: TaxonRef
    where_to_look: str
    what_to_listen_for: str
    look_alikes: str = ""


@dataclass(frozen=True, slots=True)
class RouteFieldPack:
    """Combined field guide package for a route."""

    route_id: str
    focal_species: tuple[TaxonRef, ...]
    field_cues: tuple[FieldCue, ...]
    media_assets: tuple[MediaAsset, ...]
