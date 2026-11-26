from __future__ import annotations

import re
from functools import lru_cache

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
    """Converte um padrao PAM IUPAC para regex de correspondencia exata.

    API auxiliar, mantida para demonstrar a equivalencia entre a comparacao
    posicao a posicao e uma expressao regular. A busca do pipeline usa
    ``find_pam_positions``.
    """

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


@lru_cache(maxsize=32)
def _overlapping_pam_regex(pattern: str) -> re.Pattern[str]:
    """Compila o padrao PAM como regex capaz de encontrar PAMs sobrepostos.

    Cada codigo IUPAC vira uma classe de caracteres, e o conjunto e envolvido
    por um lookahead ``(?=...)``. O lookahead verifica a janela sem consumir
    caracteres, entao a varredura avanca uma posicao por vez e ocorrencias
    sobrepostas, como os dois ``NGG`` em ``CGGG``, sao todas encontradas.

    O resultado e memorizado porque o padrao nao muda durante uma execucao.
    """

    normalized = validate_pam_pattern(pattern)
    classes = "".join(f"[{''.join(sorted(IUPAC_CODES[code]))}]" for code in normalized)
    return re.compile(f"(?={classes})")


def find_pam_positions(sequence: str, pattern: str) -> list[int]:
    """Retorna indices 0-based de PAMs, permitindo sobreposicao.

    Implementacao usada pelo pipeline. O padrao e compilado uma unica vez e a
    varredura e feita pelo automato da biblioteca ``re``, percorrendo a
    sequencia uma vez. A complexidade continua sendo O(n * m), com n igual ao
    tamanho da sequencia e m ao tamanho do padrao, mas a constante e muito
    menor do que na comparacao posicao a posicao feita em Python.

    O resultado e identico ao de ``find_pam_positions_by_scan``, o que e
    verificado por teste de equivalencia.
    """

    return [match.start() for match in _overlapping_pam_regex(pattern).finditer(sequence.upper())]


def find_pam_positions_by_scan(sequence: str, pattern: str) -> list[int]:
    """Implementacao direta da busca de PAM, mantida como referencia.

    Expressa a regra de forma literal: para cada posicao da sequencia, compara
    a janela com o padrao, base por base. E usada pelo teste de equivalencia e
    pelo script de benchmark, e serve de referencia legivel do que a versao
    com expressao regular faz.
    """

    normalized_pattern = validate_pam_pattern(pattern)
    allowed_bases = [IUPAC_CODES[code] for code in normalized_pattern]
    pam_length = len(normalized_pattern)
    seq = sequence.upper()
    positions: list[int] = []
    for start in range(0, len(seq) - pam_length + 1):
        if all(seq[start + offset] in bases for offset, bases in enumerate(allowed_bases)):
            positions.append(start)
    return positions
