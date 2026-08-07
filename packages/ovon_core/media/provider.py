"""Media Provider and Repository Interfaces for Species Media."""

from abc import ABC, abstractmethod
from typing import Sequence

from packages.ovon_core.domain import (
    LicenseType,
    MediaAsset,
    MediaType,
    MissingAttributionError,
    TaxonRef,
)

# Exact alias lookup dictionary (all keys lowercase with no spaces or hyphens)
EXACT_LICENSE_MAP = {
    "ccby2.0": LicenseType.CC_BY_2_0,
    "ccby3.0": LicenseType.CC_BY_3_0,
    "ccby4.0": LicenseType.CC_BY_4_0,
    "ccbync3.0": LicenseType.CC_BY_NC_3_0,
    "ccbync4.0": LicenseType.CC_BY_NC_4_0,
    "ccbysa3.0": LicenseType.CC_BY_SA_3_0,
    "ccbysa4.0": LicenseType.CC_BY_SA_4_0,
    "cc0": LicenseType.CC0_1_0,
    "cc01.0": LicenseType.CC0_1_0,
    "publicdomain": LicenseType.PUBLIC_DOMAIN,
    "pd": LicenseType.PUBLIC_DOMAIN,
}

NORMALIZED_LICENSE_MAP = EXACT_LICENSE_MAP


def normalize_and_validate_license(license_raw: str) -> LicenseType:
    """Validate a raw license string against exact open license allowlist.

    Preserves exact license versions. Raises MissingAttributionError if the license is not on the allowlist.
    """
    if not license_raw or not license_raw.strip():
        raise MissingAttributionError("MediaAsset requires a non-empty license string.")

    clean_key = license_raw.strip().lower().replace("-", "").replace(" ", "")

    if clean_key in EXACT_LICENSE_MAP:
        return EXACT_LICENSE_MAP[clean_key]

    raise MissingAttributionError(
        f"License '{license_raw}' is missing, ambiguous, or not on the open allowlist."
    )


class MediaProvider(ABC):
    """Abstract interface for external media source providers."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of the media provider source."""
        pass

    @abstractmethod
    def fetch_assets_for_taxon(self, taxon: TaxonRef, max_results: int = 5) -> Sequence[MediaAsset]:
        """Fetch media assets for a taxon from the provider."""
        pass


class MediaRepository(ABC):
    """Interface for managing local and cached species media assets."""

    @abstractmethod
    def get_assets_for_taxon(
        self, taxon: TaxonRef, media_type: MediaType | None = None
    ) -> Sequence[MediaAsset]:
        """Retrieve cached media assets for a taxon."""
        pass

    @abstractmethod
    def register_asset(self, asset: MediaAsset) -> None:
        """Register a new media asset with attribution validation."""
        pass
