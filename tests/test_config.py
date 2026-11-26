from pathlib import Path

import pytest

from alvocas9.config import (
    PAM_POSITION_3_LINHA,
    PipelineConfig,
    validate_min_sequence_length,
)


def _config(**overrides: object) -> PipelineConfig:
    values: dict[str, object] = {
        "input_path": Path("entrada.fasta"),
        "output_dir": Path("resultados"),
    }
    values.update(overrides)
    return PipelineConfig(**values)  # type: ignore[arg-type]


def test_default_config_is_valid() -> None:
    config = _config()

    assert config.target_length == 20
    assert config.min_gc == 40.0
    assert config.max_gc == 60.0


def test_target_length_zero_is_rejected() -> None:
    with pytest.raises(ValueError, match="target_length"):
        _config(target_length=0)


def test_negative_target_length_is_rejected() -> None:
    with pytest.raises(ValueError, match="target_length"):
        _config(target_length=-5)


def test_inverted_gc_range_is_rejected() -> None:
    with pytest.raises(ValueError, match="min_gc nao pode ser maior que max_gc"):
        _config(min_gc=90.0, max_gc=10.0)


def test_min_gc_below_zero_is_rejected() -> None:
    with pytest.raises(ValueError, match="min_gc deve estar entre 0 e 100"):
        _config(min_gc=-1.0)


def test_max_gc_above_one_hundred_is_rejected() -> None:
    with pytest.raises(ValueError, match="max_gc deve estar entre 0 e 100"):
        _config(max_gc=101.0)


def test_max_homopolymer_below_one_is_rejected() -> None:
    with pytest.raises(ValueError, match="max_homopolymer"):
        _config(max_homopolymer=0)


def test_min_sequence_length_below_one_is_rejected() -> None:
    with pytest.raises(ValueError, match="min_sequence_length"):
        _config(min_sequence_length=0)


def test_all_problems_are_reported_together() -> None:
    with pytest.raises(ValueError) as exc_info:
        _config(target_length=0, max_homopolymer=0, min_sequence_length=0)

    message = str(exc_info.value)
    assert "target_length" in message
    assert "max_homopolymer" in message
    assert "min_sequence_length" in message


def test_validate_min_sequence_length_accepts_minimum() -> None:
    assert validate_min_sequence_length(1) is None


def test_default_pam_position_is_three_prime() -> None:
    assert _config().pam_position == PAM_POSITION_3_LINHA


def test_five_prime_pam_position_is_rejected_with_an_explanation() -> None:
    """A premissa de PAM a 3' precisa ser recusada de forma explicita.

    Sem isso, um padrao de sistema com PAM a 5', como o TTTV de Cas12a, produz
    saida silenciosamente sem sentido.
    """

    with pytest.raises(ValueError) as exc_info:
        _config(pam_position="5linha")

    mensagem = str(exc_info.value)
    assert "pam_position aceita apenas" in mensagem
    assert "Cas12a" in mensagem
