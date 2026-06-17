from alvocas9.analysis.features import (
    add_candidate_features,
    build_sequence_summary,
    characterize_candidates,
)
from alvocas9.analysis.filters import APPROVED
from alvocas9.io.fasta_reader import FastaRecord


def test_build_sequence_summary() -> None:
    rows = build_sequence_summary([FastaRecord("seq1", "ACGTNN")])

    assert rows[0]["length"] == 6
    assert rows[0]["gc_percent"] == 33.33
    assert rows[0]["n_count"] == 2


def test_add_candidate_features_counts_duplicates() -> None:
    candidates = [
        {"protospacer_sequence_5to3": "ACGTACGTACGTACGTACGT"},
        {"protospacer_sequence_5to3": "ACGTACGTACGTACGTACGT"},
    ]

    rows = add_candidate_features(candidates)

    assert rows[0]["duplicate_exact_count_within_input"] == 2
    assert rows[0]["gc_percent"] == 50.0
    assert rows[0]["max_homopolymer_run"] == 1


def test_add_candidate_features_calculates_n_fields_and_homopolymer() -> None:
    candidates = [
        {"protospacer_sequence_5to3": "AAAANCGTACGTACGTACGT"},
    ]

    row = add_candidate_features(candidates)[0]

    assert row["n_count"] == 1
    assert row["has_n"] is True
    assert row["max_homopolymer_run"] == 4


def test_characterize_candidates_returns_all_requested_fields() -> None:
    candidates = [
        {"protospacer_sequence_5to3": "ACGTACGTACGTACGTACGT"},
    ]

    row = characterize_candidates(candidates)[0]

    assert row["gc_percent"] == 50.0
    assert row["n_count"] == 0
    assert row["has_n"] is False
    assert row["max_homopolymer_run"] == 1
    assert row["duplicate_exact_count_within_input"] == 1
    assert row["warnings"] == []
    assert row["heuristic_score"] == 100
    assert row["filter_status"] == APPROVED
