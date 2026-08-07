"""Unit tests for EvidenceBoundaryValidator non-detection guardrails."""

import pytest
from packages.ovon_core.evidence.boundary import (
    EvidenceBoundaryError,
    EvidenceBoundaryValidator,
    EvidenceTier,
)


def test_complete_checklist_valid_non_detection():
    # Valid non-detection: eBird complete checklist + effort valid
    assert EvidenceBoundaryValidator.validate_non_detection(
        EvidenceTier.EBIRD_COMPLETE_CHECKLIST, is_complete_checklist=True, is_effort_valid=True
    ) is True


def test_user_recall_only_zero_filling_raises_error():
    # Forbidden non-detection on user recall data
    with pytest.raises(EvidenceBoundaryError, match="strictly forbidden for evidence tier"):
        EvidenceBoundaryValidator.validate_non_detection(
            EvidenceTier.USER_RECALL_ONLY, is_complete_checklist=True, is_effort_valid=True
        )


def test_opportunistic_detection_zero_filling_raises_error():
    # Forbidden non-detection on opportunistic presence data
    with pytest.raises(EvidenceBoundaryError, match="strictly forbidden for evidence tier"):
        EvidenceBoundaryValidator.validate_non_detection(
            EvidenceTier.OPPORTUNISTIC_DETECTION, is_complete_checklist=True, is_effort_valid=True
        )


def test_incomplete_checklist_raises_error():
    with pytest.raises(EvidenceBoundaryError, match="requires both is_complete_checklist=True"):
        EvidenceBoundaryValidator.validate_non_detection(
            EvidenceTier.EBIRD_COMPLETE_CHECKLIST, is_complete_checklist=False, is_effort_valid=True
        )
