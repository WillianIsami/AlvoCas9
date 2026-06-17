from alvocas9.core.sequence_utils import gc_percent, max_homopolymer_run, reverse_complement


def test_reverse_complement_preserves_n() -> None:
    assert reverse_complement("ACGTN") == "NACGT"


def test_reverse_complement_standard_bases() -> None:
    assert reverse_complement("AAGCT") == "AGCTT"


def test_gc_percent_uses_total_length() -> None:
    assert gc_percent("GGCCAAAA") == 50.0
    assert gc_percent("GGNN") == 50.0


def test_max_homopolymer_run() -> None:
    assert max_homopolymer_run("AAACGGGGTT") == 4
    assert max_homopolymer_run("") == 0
