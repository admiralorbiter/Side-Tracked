"""CLI Tool to verify Route Evidence domain models, engines, and services."""

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


def main() -> None:
    """Run Route Evidence verification suite."""
    print("=" * 60)
    print("      SIDETRACK ROUTE EVIDENCE ENGINE VERIFICATION")
    print("=" * 60)

    now = datetime.now(timezone.utc)

    # 1. Verify Spatial Distance Engine
    pt = Coordinate(39.031, -94.591)
    line = [(39.031, -94.595), (39.031, -94.585)]
    dist_m = calculate_point_to_linestring_distance(pt, line)
    assert dist_m <= 10.0
    print(f"[OK] Metric Distance Engine: Point-to-Line distance = {dist_m:.2f}m")

    # 2. Verify Spatial & Temporal Decay Kernels
    k_spatial = calculate_spatial_decay_kernel(100.0, uncertainty_m=50.0)
    k_temp = calculate_temporal_decay_kernel(3.0, half_life_days=14.0)
    assert 0.0 < k_spatial < 1.0
    assert 0.0 < k_temp < 1.0
    print(f"[OK] Decay Kernels: Spatial Kd={k_spatial:.3f}, Temporal Kt={k_temp:.3f}")

    # 3. Verify Beta-Binomial Shrinkage Rate
    rate = calculate_beta_binomial_detection_rate(1, 1)
    assert rate == (1 + 1) / (1 + 2)  # 2/3 = 0.666...
    print(
        f"[OK] Beta-Binomial Shrinkage: 1/1 Checklist Detection = {rate*100:.1f}% (Smoothed from 100%)"
    )

    # 4. Verify Deduplication Lineage
    occ_inat = NormalizedOccurrenceEvidence(
        occurrence_id="occ_inat_01",
        concept_id="sidetrack_concept:cardinal",
        source_origin="inat",
        source_occurrence_id="obs_999",
        original_scientific_name="Cardinalis cardinalis",
        taxonomy_authority="iNat-2026",
        observed_at=now,
        latitude=39.031,
        longitude=-94.591,
    )
    occ_gbif = NormalizedOccurrenceEvidence(
        occurrence_id="occ_gbif_01",
        concept_id="sidetrack_concept:cardinal",
        source_origin="gbif",
        source_occurrence_id="obs_999",
        original_scientific_name="Cardinalis cardinalis",
        taxonomy_authority="GBIF-2026",
        observed_at=now,
        latitude=39.031,
        longitude=-94.591,
    )
    deduper = EvidenceDeduplicator()
    deduped = deduper.deduplicate([occ_inat, occ_gbif])
    assert len(deduped) == 1
    assert deduped[0].duplicate_cluster_id is not None
    print(
        f"[OK] Lineage Deduplication: 2 platform records collapsed to 1 cluster ({deduped[0].duplicate_cluster_id})"
    )

    # 5. Verify Visibility Policy
    policy = EvidenceVisibilityPolicy()
    occ_obs = NormalizedOccurrenceEvidence(
        occurrence_id="occ_obs_01",
        concept_id="sidetrack_concept:woodpecker",
        source_origin="inat",
        source_occurrence_id="obs_888",
        original_scientific_name="Dryobates pubescens",
        taxonomy_authority="iNat-2026",
        observed_at=now,
        latitude=39.040,
        longitude=-94.580,
        geoprivacy="obscured",
    )
    vis = policy.evaluate_visibility(occ_obs)
    assert vis == EvidenceVisibility.UNCERTAINTY_DISPLAY_ONLY
    assert not policy.is_distance_claim_allowed(occ_obs)
    print(f"[OK] Visibility Policy: Obscured iNat Record -> {vis.value} (Distance claim forbidden)")

    # 6. Verify Service Output
    service = RouteEvidenceService()
    summary = service.build_evidence_summary(ROUTE_BIRDY)
    assert summary.status == "ok"
    assert len(summary.species_evidence) > 0
    print(
        f"[OK] RouteEvidenceService Verified: Generated summary with {len(summary.species_evidence)} species"
    )

    print("=" * 60)
    print("SUCCESS: ALL ROUTE EVIDENCE ENGINE VERIFICATION CHECKS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
