from pathlib import Path

from alvocas9.analysis.filters import (
    APPROVED,
    CAUTION,
    FAILED,
    FilterConfig,
    apply_filters,
    rank_candidates,
)
from alvocas9.config import PipelineConfig


def test_filters_approve_candidate_without_warnings(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "x.fasta", output_dir=tmp_path / "out")
    candidate = _candidate(gc_percent=50, has_n=False, max_homopolymer_run=2, duplicate_count=1)

    row = apply_filters([candidate], config)[0]

    assert row["filter_status"] == APPROVED
    assert row["heuristic_score"] == 100
    assert row["warnings"] == []


def test_filters_gc_outside_range_requires_caution(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "x.fasta", output_dir=tmp_path / "out")
    candidate = _candidate(gc_percent=20, has_n=False, max_homopolymer_run=2, duplicate_count=1)

    row = apply_filters([candidate], config)[0]

    assert row["filter_status"] == CAUTION
    assert row["heuristic_score"] == 80
    assert "GC fora da faixa configurada" in row["warnings"]


def test_filters_fail_gc_and_n(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "x.fasta", output_dir=tmp_path / "out")
    candidate = _candidate(gc_percent=20, has_n=True, max_homopolymer_run=2, duplicate_count=1)

    row = apply_filters([candidate], config)[0]

    assert row["filter_status"] == FAILED
    assert row["heuristic_score"] == 55


def test_filters_warn_duplicate_and_homopolymer(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "x.fasta", output_dir=tmp_path / "out")
    candidate = _candidate(gc_percent=50, has_n=False, max_homopolymer_run=5, duplicate_count=2)

    row = apply_filters([candidate], config)[0]

    assert row["filter_status"] == CAUTION
    assert row["heuristic_score"] == 70


def test_filters_candidate_with_n_is_critical_by_default() -> None:
    candidate = _candidate(gc_percent=50, has_n=True, max_homopolymer_run=2, duplicate_count=1)

    row = apply_filters([candidate])[0]

    assert row["filter_status"] == FAILED
    assert row["heuristic_score"] == 75


def test_filters_candidate_with_n_can_be_moderate_when_allowed() -> None:
    candidate = _candidate(gc_percent=50, has_n=True, max_homopolymer_run=2, duplicate_count=1)

    row = apply_filters([candidate], FilterConfig(allow_n=True))[0]

    assert row["filter_status"] == CAUTION
    assert row["heuristic_score"] == 75


def test_filters_long_homopolymer_requires_caution() -> None:
    candidate = _candidate(gc_percent=50, has_n=False, max_homopolymer_run=5, duplicate_count=1)

    row = apply_filters([candidate])[0]

    assert row["filter_status"] == CAUTION
    assert row["heuristic_score"] == 90
    assert "Homopolimero acima do limite configurado" in row["warnings"]


def test_filters_duplicate_requires_caution() -> None:
    candidate = _candidate(gc_percent=50, has_n=False, max_homopolymer_run=2, duplicate_count=2)

    row = apply_filters([candidate])[0]

    assert row["filter_status"] == CAUTION
    assert row["heuristic_score"] == 80
    assert "Protospacer duplicado exatamente no conjunto de entrada" in row["warnings"]


def test_filters_score_minimum_is_not_negative() -> None:
    candidate = _candidate(gc_percent=0, has_n=True, max_homopolymer_run=99, duplicate_count=99)

    row = apply_filters([candidate])[0]

    assert row["heuristic_score"] == 25
    assert row["heuristic_score"] >= 0
    assert row["filter_status"] == FAILED


def test_filters_score_maximum_is_100() -> None:
    candidate = _candidate(gc_percent=50, has_n=False, max_homopolymer_run=1, duplicate_count=1)

    row = apply_filters([candidate])[0]

    assert row["heuristic_score"] == 100
    assert row["heuristic_score"] <= 100
    assert row["filter_status"] == APPROVED


def test_filters_status_failed_when_score_below_50_with_allowed_n() -> None:
    candidate = _candidate(gc_percent=0, has_n=True, max_homopolymer_run=99, duplicate_count=99)

    row = apply_filters([candidate], FilterConfig(allow_n=True))[0]

    assert row["heuristic_score"] == 25
    assert row["filter_status"] == FAILED


def test_rank_candidates_sorts_by_score_descending() -> None:
    candidates = [
        _ranked(70, "seq1", "+", 1),
        _ranked(100, "seq1", "+", 5),
        _ranked(85, "seq1", "+", 3),
    ]

    assert [row["heuristic_score"] for row in rank_candidates(candidates)] == [100, 85, 70]


def test_rank_candidates_breaks_ties_deterministically() -> None:
    candidates = [
        _ranked(100, "seq2", "+", 10),
        _ranked(100, "seq1", "-", 50),
        _ranked(100, "seq1", "+", 90),
        _ranked(100, "seq1", "+", 20),
    ]

    ordenados = [
        (row["sequence_id"], row["strand"], row["full_candidate_start_1based"])
        for row in rank_candidates(candidates)
    ]

    assert ordenados == [
        ("seq1", "+", 20),
        ("seq1", "+", 90),
        ("seq1", "-", 50),
        ("seq2", "+", 10),
    ]


def test_rank_candidates_keeps_the_original_list_untouched() -> None:
    candidates = [_ranked(50, "seq1", "+", 1), _ranked(100, "seq1", "+", 2)]

    rank_candidates(candidates)

    assert [row["heuristic_score"] for row in candidates] == [50, 100]


def _ranked(score: int, sequence_id: str, strand: str, start: int) -> dict[str, object]:
    return {
        "heuristic_score": score,
        "sequence_id": sequence_id,
        "strand": strand,
        "full_candidate_start_1based": start,
    }


def _candidate(gc_percent: float, has_n: bool, max_homopolymer_run: int, duplicate_count: int) -> dict[str, object]:
    return {
        "gc_percent": gc_percent,
        "has_n": has_n,
        "max_homopolymer_run": max_homopolymer_run,
        "duplicate_exact_count_within_input": duplicate_count,
    }
