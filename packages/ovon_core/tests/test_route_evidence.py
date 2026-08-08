"""Unit tests for Route Evidence domain models, engines, and services."""

from datetime import datetime, timezone

from packages.ovon_core.domain.evidence import (
    EvidenceVisibility,
    NormalizedOccurrenceEvidence,
)
from packages.ovon_core.domain.spatial import Coordinate
from packages.ovon_core.evidence.deduplicator import EvidenceDeduplicator
from packages.ovon_core.evidence.service import RouteEvidenceService
from packages.ovon_core.evidence.spatial_engine import (
    calculate_beta_binomial_detection_rate,
    calculate_point_to_linestring_distance,
    calculate_spatial_decay_kernel,
    calculate_temporal_decay_kernel,
)
from packages.ovon_core.evidence.visibility import EvidenceVisibilityPolicy
from packages.ovon_core.fixtures import ROUTE_BIRDY


def test_spatial_distance_and_decay_kernels():
    pt = Coordinate(39.031, -94.591)
    line = [(39.031, -94.595), (39.031, -94.585)]
    dist = calculate_point_to_linestring_distance(pt, line)
    assert dist <= 10.0

    k_spatial = calculate_spatial_decay_kernel(100.0, uncertainty_m=30.0)
    assert 0.0 < k_spatial < 1.0

    k_temporal = calculate_temporal_decay_kernel(5.0)
    assert 0.0 < k_temporal < 1.0


def test_beta_binomial_shrinkage():
    rate_1_of_1 = calculate_beta_binomial_detection_rate(1, 1)
    assert rate_1_of_1 == 2.0 / 3.0  # 66.7%

    rate_10_of_20 = calculate_beta_binomial_detection_rate(10, 20)
    assert rate_10_of_20 == 11.0 / 22.0  # 50.0%


def test_evidence_deduplicator():
    now = datetime.now(timezone.utc)
    o1 = NormalizedOccurrenceEvidence(
        occurrence_id="o1",
        concept_id="c1",
        source_origin="inat",
        source_occurrence_id="i1",
        original_scientific_name="Turdus migratorius",
        taxonomy_authority="iNat",
        observed_at=now,
        latitude=39.031,
        longitude=-94.591,
    )
    o2 = NormalizedOccurrenceEvidence(
        occurrence_id="o2",
        concept_id="c1",
        source_origin="gbif",
        source_occurrence_id="i1",
        original_scientific_name="Turdus migratorius",
        taxonomy_authority="GBIF",
        observed_at=now,
        latitude=39.031,
        longitude=-94.591,
    )
    deduper = EvidenceDeduplicator()
    res = deduper.deduplicate([o1, o2])
    assert len(res) == 1
    assert res[0].source_origin == "inat"
    assert res[0].duplicate_cluster_id is not None


def test_visibility_policy():
    policy = EvidenceVisibilityPolicy()
    now = datetime.now(timezone.utc)

    open_occ = NormalizedOccurrenceEvidence(
        occurrence_id="open1",
        concept_id="c1",
        source_origin="ebird",
        source_occurrence_id="e1",
        original_scientific_name="Cardinalis cardinalis",
        taxonomy_authority="eBird",
        observed_at=now,
        latitude=39.031,
        longitude=-94.591,
        geoprivacy="open",
    )
    assert policy.evaluate_visibility(open_occ) == EvidenceVisibility.EXACT_DISPLAY_ALLOWED
    assert policy.is_distance_claim_allowed(open_occ)

    obs_occ = NormalizedOccurrenceEvidence(
        occurrence_id="obs1",
        concept_id="c1",
        source_origin="inat",
        source_occurrence_id="i1",
        original_scientific_name="Cardinalis cardinalis",
        taxonomy_authority="iNat",
        observed_at=now,
        latitude=39.031,
        longitude=-94.591,
        geoprivacy="obscured",
    )
    assert policy.evaluate_visibility(obs_occ) == EvidenceVisibility.UNCERTAINTY_DISPLAY_ONLY
    assert not policy.is_distance_claim_allowed(obs_occ)


from packages.ovon_core.evidence.providers import MockRecentOccurrenceProvider


def test_route_evidence_service():
    # 1. Test production default provider (NoConfiguredEvidenceProvider) fails closed cleanly
    service_default = RouteEvidenceService()
    summary_default = service_default.build_evidence_summary(ROUTE_BIRDY)
    assert summary_default.status == "ok"
    assert len(summary_default.species_evidence) > 0
    assert summary_default.recent_species_count == 0
    assert (
        summary_default.species_evidence[0].evidence_score_status
        == "no_configured_evidence_provider"
    )

    # 2. Test explicit MockRecentOccurrenceProvider for test/demo mode
    service_mock = RouteEvidenceService(provider=MockRecentOccurrenceProvider())
    summary_mock = service_mock.build_evidence_summary(ROUTE_BIRDY)
    assert summary_mock.status == "ok"
    assert summary_mock.recent_species_count > 0
