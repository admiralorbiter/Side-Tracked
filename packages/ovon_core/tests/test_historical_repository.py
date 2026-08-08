"""Unit tests for R6 Historical Checklist Repository (EBD/SED Querying)."""

from packages.ovon_core.evidence.historical_repository import HistoricalChecklistRepository


def test_historical_checklist_repository_complete_filter(tmp_path):
    repo = HistoricalChecklistRepository(data_dir=tmp_path)
    bbox = (39.00, -94.70, 39.20, -94.40)

    events = repo.query_sampling_events(bounding_box=bbox, complete_only=True)
    assert len(events) == 2
    assert "SED_KC_INC" not in [e.event_id for e in events]


def test_historical_checklist_repository_observations(tmp_path):
    repo = HistoricalChecklistRepository(data_dir=tmp_path)
    events = repo.query_sampling_events(complete_only=True)
    event_ids = [e.event_id for e in events]

    obs = repo.query_observations(
        event_ids=event_ids, concept_ids=["sidetrack_concept:northern_cardinal"]
    )
    assert len(obs) == 2
    assert obs[0].concept_id == "sidetrack_concept:northern_cardinal"
