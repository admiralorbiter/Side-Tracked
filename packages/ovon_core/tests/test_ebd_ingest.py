"""Unit tests for EBDSamplingEventParser named-column reading, header validation, and EBD/SED joining."""

from packages.ovon_core.pipeline.ebd_ingest import EBDSamplingEventParser


def test_parse_sed_tsv_named_columns_and_permutation():
    # TSV fixture with non-standard column order
    tsv_shuffled = (
        "LATITUDE\tOBSERVATION DATE\tSAMPLING EVENT IDENTIFIER\tLONGITUDE\tPROTOCOL TYPE\tALL SPECIES REPORTED\tDURATION MINUTES\tEFFORT DISTANCE KM\n"
        "39.100\t2026-05-10\tS1001\t-94.580\tTraveling\t1\t45.0\t1.5\n"
        "38.950\t2026-05-11\tS1002\t-94.620\tStationary\t0\t20.0\t\n"
    )

    events, quarantine = EBDSamplingEventParser.parse_sed_tsv(tsv_shuffled)

    assert len(quarantine) == 0
    assert len(events) == 2

    assert events[0].sampling_event_id == "S1001"
    assert events[0].protocol_type == "Traveling"
    assert events[0].all_species_reported is True
    assert events[0].latitude == 39.100
    assert events[0].longitude == -94.580
    assert events[0].duration_minutes == 45.0
    assert events[0].effort_distance_km == 1.5

    assert events[1].sampling_event_id == "S1002"
    assert events[1].protocol_type == "Stationary"
    assert events[1].all_species_reported is False
    assert events[1].effort_distance_km is None


def test_parse_ebd_tsv_named_columns():
    tsv_ebd = (
        "COMMON NAME\tSAMPLING EVENT IDENTIFIER\tSPECIES CODE\tSCIENTIFIC NAME\tOBSERVATION COUNT\tCATEGORY\n"
        "American Robin\tS1001\tamerob\tTurdus migratorius\t4\tspecies\n"
        "Downy/Hairy Woodpecker\tS1001\tdowwoo/haiwoo\tPicoides sp.\t1\tslash\n"
    )

    obs, quarantine = EBDSamplingEventParser.parse_ebd_tsv(tsv_ebd)

    assert len(quarantine) == 0
    assert len(obs) == 2

    assert obs[0].sampling_event_id == "S1001"
    assert obs[0].raw_species_code == "amerob"
    assert obs[0].is_slash is False

    assert obs[1].sampling_event_id == "S1001"
    assert obs[1].raw_species_code == "dowwoo/haiwoo"
    assert obs[1].is_slash is True


def test_ebd_sed_join():
    tsv_sed = (
        "SAMPLING EVENT IDENTIFIER\tPROTOCOL TYPE\tALL SPECIES REPORTED\tOBSERVATION DATE\tLATITUDE\tLONGITUDE\n"
        "S1001\tTraveling\t1\t2026-05-10\t39.1\t-94.5\n"
    )
    tsv_ebd = (
        "SAMPLING EVENT IDENTIFIER\tSPECIES CODE\tSCIENTIFIC NAME\tCOMMON NAME\n"
        "S1001\tamerob\tTurdus migratorius\tAmerican Robin\n"
    )

    events, _ = EBDSamplingEventParser.parse_sed_tsv(tsv_sed)
    obs, _ = EBDSamplingEventParser.parse_ebd_tsv(tsv_ebd)

    joined = EBDSamplingEventParser.join_ebd_sed(events, obs)

    assert "S1001" in joined
    assert len(joined["S1001"]) == 1
    assert joined["S1001"][0].raw_species_code == "amerob"
