from __future__ import annotations

import re

IUPAC_CODES: dict[str, set[str]] = {
    "A": {"A"},
    "C": {"C"},
    "G": {"G"},
    "T": {"T"},
    "N": {"A", "C", "G", "T"},
    "R": {"A", "G"},
    "Y": {"C", "T"},
    "S": {"G", "C"},
    "W": {"A", "T"},
    "K": {"G", "T"},
    "M": {"A", "C"},
    "B": {"C", "G", "T"},
    "D": {"A", "G", "T"},
    "H": {"A", "C", "T"},
    "V": {"A", "C", "G"},
}


def iupac_pam_to_regex(pattern: str) -> re.Pattern[str]:
    """Converte um padrao PAM IUPAC para regex de correspondencia exata."""

    normalized = validate_pam_pattern(pattern)
    parts = []
    for code in normalized:
        bases = "".join(sorted(IUPAC_CODES[code]))
        parts.append(f"[{bases}]")
    return re.compile("^" + "".join(parts) + "$")


def validate_pam_pattern(pattern: str) -> str:
    """Normaliza e valida um padrao PAM com codigos IUPAC simples."""

    normalized = pattern.upper()
    invalid = sorted({char for char in normalized if char not in IUPAC_CODES})
    if invalid:
        joined = ", ".join(invalid)
        raise ValueError(f"Padrao PAM contem codigo(s) IUPAC nao suportado(s): {joined}.")
    if not normalized:
        raise ValueError("Padrao PAM nao pode ser vazio.")
    return normalized


def pam_matches(sequence_fragment: str, pattern: str) -> bool:
    """Verifica se um fragmento de sequencia corresponde ao padrao PAM."""

    normalized_pattern = validate_pam_pattern(pattern)
    fragment = sequence_fragment.upper()
    if len(fragment) != len(normalized_pattern):
        return False
    return all(base in IUPAC_CODES[pam_code] for base, pam_code in zip(fragment, normalized_pattern))


def find_pam_positions(sequence: str, pattern: str) -> list[int]:
    """Retorna indices 0-based de PAMs, permitindo sobreposicao."""

    normalized_pattern = validate_pam_pattern(pattern)
    pam_length = len(normalized_pattern)
    seq = sequence.upper()
    positions: list[int] = []
    for start in range(0, len(seq) - pam_length + 1):
        fragment = seq[start : start + pam_length]
        if pam_matches(fragment, normalized_pattern):
            positions.append(start)
    return positions
