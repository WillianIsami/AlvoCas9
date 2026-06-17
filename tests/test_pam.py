import pytest

from alvocas9.core.pam import (
    find_pam_positions,
    iupac_pam_to_regex,
    pam_matches,
    validate_pam_pattern,
)


def test_pam_ngg_matches_expected_fragments() -> None:
    assert pam_matches("AGG", "NGG") is True
    assert pam_matches("TGG", "NGG") is True
    assert pam_matches("CGG", "NGG") is True
    assert pam_matches("GGG", "NGG") is True
    assert pam_matches("AGA", "NGG") is False
    assert pam_matches("TGT", "NGG") is False


def test_pam_ngg_does_not_match_unknown_n_in_sequence() -> None:
    assert pam_matches("NGG", "NGG") is False
    assert pam_matches("NGA", "NGG") is False
    assert pam_matches("NGT", "NGG") is False


def test_find_pam_positions_allows_overlap() -> None:
    assert find_pam_positions("AGGG", "NGG") == [0, 1]


def test_iupac_codes_include_common_ambiguity() -> None:
    assert pam_matches("AGG", "RGG") is True
    assert pam_matches("GGG", "RGG") is True
    assert pam_matches("CGG", "RGG") is False


def test_iupac_pam_to_regex_matches_exact_pam() -> None:
    regex = iupac_pam_to_regex("NGG")

    assert regex.fullmatch("AGG")
    assert regex.fullmatch("TGG")
    assert not regex.fullmatch("NAGG")
    assert not regex.fullmatch("NGG")


def test_invalid_pam_pattern_raises() -> None:
    with pytest.raises(ValueError):
        validate_pam_pattern("N?G")
