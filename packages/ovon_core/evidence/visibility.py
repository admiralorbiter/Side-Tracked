"""Evidence Visibility and Geoprivacy Policy Engine."""

from packages.ovon_core.domain.evidence import (
    EvidenceVisibility,
    NormalizedOccurrenceEvidence,
)


class EvidenceVisibilityPolicy:
    """Enforces geoprivacy rules, sensitive species protection, and exact distance claim permissions."""

    def evaluate_visibility(self, occurrence: NormalizedOccurrenceEvidence) -> EvidenceVisibility:
        """Determine display visibility for an occurrence record."""
        # 1. Private records are hidden from public display
        if occurrence.geoprivacy == "private":
            return EvidenceVisibility.HIDDEN

        # 2. Sensitive species suppress point locations and exact distance claims
        if occurrence.sensitive:
            return EvidenceVisibility.HIDDEN

        # 3. Obscured coordinates (e.g. iNaturalist 0.2° x 0.2° grid) allow coarse display only
        if occurrence.geoprivacy == "obscured":
            return EvidenceVisibility.UNCERTAINTY_DISPLAY_ONLY

        # 4. Open records with large coordinate uncertainty (> 500m) restrict exact distance claims
        if occurrence.coordinate_uncertainty_m and occurrence.coordinate_uncertainty_m > 500.0:
            return EvidenceVisibility.UNCERTAINTY_DISPLAY_ONLY

        # 5. Open precise records allow exact metric distance calculations
        return EvidenceVisibility.EXACT_DISPLAY_ALLOWED

    def is_distance_claim_allowed(self, occurrence: NormalizedOccurrenceEvidence) -> bool:
        """Return True if precise metric distance claims are allowed for this record."""
        vis = self.evaluate_visibility(occurrence)
        return vis == EvidenceVisibility.EXACT_DISPLAY_ALLOWED
