from pathlib import Path

from alvocas9.config import PipelineConfig
from alvocas9.core.scanner import (
    ScanConfig,
    extract_candidates_from_both_strands,
    scan_record,
    scan_sequence_for_pam,
)
from alvocas9.io.fasta_reader import FastaRecord


def test_short_sequence_has_no_candidate() -> None:
    candidates = extract_candidates_from_both_strands("seq1", "AGG", ScanConfig())

    assert candidates == []


def test_scan_sequence_for_pam_returns_pam_hits() -> None:
    hits = scan_sequence_for_pam("AAGG", sequence_id="seq1", config=ScanConfig())

    assert len(hits) == 1
    assert hits[0].pam_sequence_5to3 == "AGG"
    assert hits[0].pam_start_0based == 1
    assert hits[0].pam_end_0based == 4
    assert hits[0].pam_start_1based == 2
    assert hits[0].pam_end_1based == 4


def test_plus_strand_coordinates_are_1based_inclusive(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "x.fasta", output_dir=tmp_path / "out")
    record = FastaRecord("seq1", "A" * 20 + "AGG")

    candidates, stats = scan_record(record, config)

    assert stats.pams_found_plus == 1
    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate["strand"] == "+"
    assert candidate["protospacer_sequence_5to3"] == "A" * 20
    assert candidate["pam_sequence_5to3"] == "AGG"
    assert candidate["protospacer_start_1based"] == 1
    assert candidate["protospacer_end_1based"] == 20
    assert candidate["pam_start_1based"] == 21
    assert candidate["pam_end_1based"] == 23
    assert candidate["full_candidate_start_1based"] == 1
    assert candidate["full_candidate_end_1based"] == 23


def test_extract_candidates_from_both_strands_returns_candidate_dataclass() -> None:
    candidates = extract_candidates_from_both_strands("seq1", "A" * 20 + "TGG", ScanConfig())

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.sequence_id == "seq1"
    assert candidate.strand == "+"
    assert candidate.protospacer_sequence_5to3 == "A" * 20
    assert candidate.pam_sequence_5to3 == "TGG"
    assert candidate.protospacer_start_1based == 1
    assert candidate.protospacer_end_1based == 20
    assert candidate.pam_start_1based == 21
    assert candidate.pam_end_1based == 23


def test_plus_strand_skips_pam_without_upstream_bases(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "x.fasta", output_dir=tmp_path / "out")
    record = FastaRecord("seq1", "AGG" + "A" * 20)

    candidates, stats = scan_record(record, config)

    assert candidates == []
    assert stats.pams_skipped_insufficient_upstream_plus == 1


def test_unknown_n_in_pam_does_not_create_candidate() -> None:
    candidates = extract_candidates_from_both_strands("seq1", "A" * 20 + "NGG", ScanConfig())

    assert candidates == []
