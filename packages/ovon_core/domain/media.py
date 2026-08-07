from dataclasses import dataclass
from enum import Enum

from packages.ovon_core.domain.errors import MissingAttributionError
from packages.ovon_core.domain.taxonomy import TaxonRef


class LicenseType(str, Enum):
    """Supported Creative Commons and Open Media Licenses."""

    CC_BY_2_0 = "CC BY 2.0"
    CC_BY_2_5 = "CC BY 2.5"
    CC_BY_3_0 = "CC BY 3.0"
    CC_BY_4_0 = "CC BY 4.0"
    CC_BY_NC_3_0 = "CC BY-NC 3.0"
    CC_BY_NC_4_0 = "CC BY-NC 4.0"
    CC_BY_SA_2_5 = "CC BY-SA 2.5"
    CC_BY_SA_3_0 = "CC BY-SA 3.0"
    CC_BY_SA_4_0 = "CC BY-SA 4.0"
    CC0_1_0 = "CC0 1.0"
    PUBLIC_DOMAIN = "Public Domain"


class MediaType(str, Enum):
    """Supported Species Media Asset Types."""

    PHOTO = "photo"
    AUDIO = "audio"


class MediaVerificationStatus(str, Enum):
    """Workflow verification status for media assets."""

    APPROVED_PRIMARY = "approved_primary"
    APPROVED_ALTERNATE = "approved_alternate"
    PROTOTYPE_ONLY = "prototype_only"
    CANDIDATE = "candidate"
    REJECTED = "rejected"


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
    verification_status: MediaVerificationStatus = MediaVerificationStatus.APPROVED_PRIMARY
    license_url: str | None = None
    retrieved_at: str | None = None
    cached_path: str | None = None

    def __post_init__(self) -> None:
        if not self.asset_id or not self.asset_id.strip():
            raise MissingAttributionError("MediaAsset requires a non-empty asset_id.")
        if not self.url or not self.url.strip():
            raise MissingAttributionError("MediaAsset requires a non-empty url.")
        if not self.creator or not self.creator.strip():
            raise MissingAttributionError("MediaAsset requires a non-empty creator.")
        if not self.attribution_text or not self.attribution_text.strip():
            raise MissingAttributionError("MediaAsset requires non-empty attribution_text.")

    @property
    def resolved_url(self) -> str:
        """Return local cached URL endpoint if file exists on disk, otherwise external URL."""
        from pathlib import Path

        if self.cached_path:
            p = Path(self.cached_path)
            if p.exists() and p.stat().st_size > 0:
                clean = self.cached_path.replace("\\", "/")
                return f"/{clean}" if not clean.startswith("/") else clean
        if self.url:
            clean_url = self.url.lstrip("/")
            if clean_url.startswith("media/cached"):
                p = Path(clean_url)
                if p.exists() and p.stat().st_size > 0:
                    return f"/{clean_url}"
        return self.url

    @property
    def mime_type(self) -> str:
        """Derive correct HTTP MIME type for audio and photo assets."""
        url_lower = self.resolved_url.lower()
        if ".ogg" in url_lower:
            return "audio/ogg"
        if ".mp3" in url_lower:
            return "audio/mpeg"
        if ".wav" in url_lower:
            return "audio/wav"
        if ".png" in url_lower:
            return "image/png"
        if ".webp" in url_lower:
            return "image/webp"
        if ".jpg" in url_lower or ".jpeg" in url_lower:
            return "image/jpeg"

        return "audio/mpeg" if self.media_type == MediaType.AUDIO else "image/jpeg"


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
