import random

import pytest

from alvocas9.core.pam import (
    find_pam_positions,
    find_pam_positions_by_scan,
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


def test_pam_matches_rejects_fragment_of_wrong_length() -> None:
    assert pam_matches("AG", "NGG") is False
    assert pam_matches("AGGG", "NGG") is False


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


def test_empty_pam_pattern_raises() -> None:
    with pytest.raises(ValueError, match="nao pode ser vazio"):
        validate_pam_pattern("")


def test_find_pam_positions_accepts_lowercase_sequence() -> None:
    assert find_pam_positions("aagg", "NGG") == [1]
    assert find_pam_positions_by_scan("aagg", "NGG") == [1]


def test_scan_implementation_allows_overlap() -> None:
    assert find_pam_positions_by_scan("AGGG", "NGG") == [0, 1]


def test_find_pam_positions_handles_sequence_shorter_than_pattern() -> None:
    assert find_pam_positions("AG", "NGG") == []
    assert find_pam_positions_by_scan("AG", "NGG") == []


def test_find_pam_positions_with_invalid_pattern_raises() -> None:
    with pytest.raises(ValueError):
        find_pam_positions("ACGTAGG", "N?G")


def test_both_implementations_agree_on_random_sequences() -> None:
    """Teste de equivalencia entre a busca por regex e a varredura direta.

    A versao usada pelo pipeline e a com expressao regular. A varredura direta
    e a referencia legivel da regra. As duas precisam concordar em qualquer
    entrada, inclusive com bases desconhecidas e PAMs sobrepostos.
    """

    random.seed(20261116)
    patterns = ("NGG", "NG", "TTTV", "RGG", "NNGRRT")
    lengths = (0, 1, 3, 25, 400, 2000)

    for pattern in patterns:
        for length in lengths:
            sequence = "".join(random.choice("ACGTN") for _ in range(length))
            assert find_pam_positions(sequence, pattern) == find_pam_positions_by_scan(
                sequence, pattern
            ), f"divergencia com padrao {pattern} e sequencia de {length} bases"
