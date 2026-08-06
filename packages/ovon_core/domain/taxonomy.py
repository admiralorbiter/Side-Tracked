from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class TaxonRef:
    """Canonical Bird Species Reference."""
    taxon_id: str
    common_name: str
    scientific_name: str
    ebird_code: str
    category: str = "Bird"
    taxonomy_version: str = "ebird_2023"

    def __post_init__(self) -> None:
        if not self.taxon_id:
            raise ValueError("taxon_id cannot be empty.")
        if not self.common_name:
            raise ValueError("common_name cannot be empty.")
        if not self.scientific_name:
            raise ValueError("scientific_name cannot be empty.")

    @classmethod
    def create(cls, common_name: str, scientific_name: str, ebird_code: str, category: str = "Bird") -> "TaxonRef":
        """Factory method to construct a canonical TaxonRef with deterministic taxon_id."""
        clean_code = ebird_code.strip().lower()
        canonical_id = f"species:ebird:{clean_code}"
        return cls(
            taxon_id=canonical_id,
            common_name=common_name.strip(),
            scientific_name=scientific_name.strip(),
            ebird_code=clean_code,
            category=category
        )
