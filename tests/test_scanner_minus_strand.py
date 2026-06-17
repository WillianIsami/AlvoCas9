from pathlib import Path

from alvocas9.config import PipelineConfig
from alvocas9.core.scanner import ScanConfig, extract_candidates_from_both_strands, scan_record
from alvocas9.io.fasta_reader import FastaRecord


def test_minus_strand_coordinates_map_to_original_sequence(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "x.fasta", output_dir=tmp_path / "out")
    record = FastaRecord("seq1", "CCT" + "T" * 20)

    candidates, stats = scan_record(record, config)

    minus_candidates = [candidate for candidate in candidates if candidate["strand"] == "-"]
    assert stats.pams_found_minus == 1
    assert len(minus_candidates) == 1

    candidate = minus_candidates[0]
    assert candidate["protospacer_sequence_5to3"] == "A" * 20
    assert candidate["pam_sequence_5to3"] == "AGG"
    assert candidate["pam_start_1based"] == 1
    assert candidate["pam_end_1based"] == 3
    assert candidate["protospacer_start_1based"] == 4
    assert candidate["protospacer_end_1based"] == 23
    assert candidate["full_candidate_start_1based"] == 1
    assert candidate["full_candidate_end_1based"] == 23


def test_minus_strand_candidate_dataclass_maps_coordinates() -> None:
    candidates = extract_candidates_from_both_strands("seq1", "CCT" + "T" * 20, ScanConfig())

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.strand == "-"
    assert candidate.protospacer_sequence_5to3 == "A" * 20
    assert candidate.pam_sequence_5to3 == "AGG"
    assert candidate.pam_start_1based == 1
    assert candidate.pam_end_1based == 3
    assert candidate.protospacer_start_1based == 4
    assert candidate.protospacer_end_1based == 23


def test_minus_strand_coordinates_with_short_target_length() -> None:
    candidates = extract_candidates_from_both_strands(
        "seq1",
        "CCT" + "T" * 5,
        ScanConfig(target_length=5),
    )

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.strand == "-"
    assert candidate.protospacer_sequence_5to3 == "A" * 5
    assert candidate.pam_sequence_5to3 == "AGG"
    assert candidate.pam_start_1based == 1
    assert candidate.pam_end_1based == 3
    assert candidate.protospacer_start_1based == 4
    assert candidate.protospacer_end_1based == 8
    assert candidate.full_candidate_start_1based == 1
    assert candidate.full_candidate_end_1based == 8
