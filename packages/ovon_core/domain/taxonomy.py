from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TaxonRef:
    """Canonical Bird Species Reference."""

    taxon_id: str
    common_name: str
    scientific_name: str
    ebird_code: str
    category: str = "Bird"
    taxonomy_version: str = "Clements-2025"

    def __post_init__(self) -> None:
        if not self.taxon_id:
            raise ValueError("taxon_id cannot be empty.")
        if not self.common_name:
            raise ValueError("common_name cannot be empty.")
        if not self.scientific_name:
            raise ValueError("scientific_name cannot be empty.")

    @classmethod
    def create(
        cls, common_name: str, scientific_name: str, ebird_code: str, category: str = "Bird"
    ) -> "TaxonRef":
        """Factory method to construct a canonical TaxonRef with deterministic taxon_id."""
        clean_code = ebird_code.strip().lower()
        canonical_id = f"species:ebird:{clean_code}"
        return cls(
            taxon_id=canonical_id,
            common_name=common_name.strip(),
            scientific_name=scientific_name.strip(),
            ebird_code=clean_code,
            category=category,
        )


@dataclass(frozen=True, slots=True)
class TaxonSupport:
    """Scientific support record decoupling ecological model support from media completeness."""

    taxonomy_known: bool = True
    occurrence_data_available: bool = False
    effort_model_available: bool = False
    calibrated_model_available: bool = False
    field_cue_reviewed: bool = False
    photo_available: bool = False
    song_available: bool = False
    call_available: bool = False
    audio_available: bool = False
    sensitive: bool = False


@dataclass(frozen=True, slots=True)
class FieldCueProfile:
    """Region and season aware field cue profile for a species."""

    taxon_id: str
    region_scope: str = "US-MO-KC"
    season_scope: str = "all_year"
    weeks_range: tuple[int, int] = (1, 52)
    audience: str = "beginner"
    look_for: tuple[str, ...] = ()
    where_to_look: str = ""
    listen_for: str = ""
    where_to_listen: str = ""
    confusion_taxa: tuple[str, ...] = ()
    ethics_note: str | None = None
    source: str = "Sidetrack Field Team"
    reviewer: str = "Lead Ornithologist"
    version: str = "v1.0"

