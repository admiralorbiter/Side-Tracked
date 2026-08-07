"""Evidence Boundary & Zero-Filling Guardrail Validation Engine."""

from enum import Enum


class EvidenceTier(str, Enum):
    """Supported evidence tiers for observation datasets."""

    USER_RECALL_ONLY = "user_recall_only"
    OPPORTUNISTIC_DETECTION = "opportunistic_detection"
    EBIRD_COMPLETE_CHECKLIST = "ebird_complete_checklist"


class EvidenceBoundaryError(Exception):
    """Raised when an illegal zero-filling or non-detection assertion violates evidence tier rules."""

    pass


class EvidenceBoundaryValidator:
    """Validates evidence tier bounds to prevent synthetic non-detection leakage into scientific models."""

    @classmethod
    def validate_non_detection(
        cls,
        evidence_tier: EvidenceTier | str,
        is_complete_checklist: bool = False,
        is_effort_valid: bool = False,
    ) -> bool:
        """Enforce strict non-detection boundary rule.
        
        Non-detections (zeros) can ONLY be generated when:
        is_complete_checklist == True AND is_effort_valid == True AND evidence_tier == EBIRD_COMPLETE_CHECKLIST.
        """
        tier_str = evidence_tier.value if isinstance(evidence_tier, EvidenceTier) else str(evidence_tier)

        if tier_str in (EvidenceTier.USER_RECALL_ONLY.value, EvidenceTier.OPPORTUNISTIC_DETECTION.value):
            raise EvidenceBoundaryError(
                f"Non-detection (zero-filling) is strictly forbidden for evidence tier '{tier_str}'. "
                "Personal recall and opportunistic presence observations cannot generate absent species evidence."
            )

        if not is_complete_checklist or not is_effort_valid:
            raise EvidenceBoundaryError(
                "Non-detection requires both is_complete_checklist=True and is_effort_valid=True."
            )

        return True
