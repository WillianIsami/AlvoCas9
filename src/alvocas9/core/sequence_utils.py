from __future__ import annotations


_COMPLEMENT = str.maketrans("ACGTNacgtn", "TGCANtgcan")


def reverse_complement(sequence: str) -> str:
    """Retorna o reverso complementar preservando N."""

    return sequence.translate(_COMPLEMENT)[::-1].upper()


def gc_percent(sequence: str) -> float:
    """Calcula GC% usando o tamanho total da sequencia como denominador."""

    if not sequence:
        return 0.0
    seq = sequence.upper()
    gc_count = seq.count("G") + seq.count("C")
    return round(gc_count / len(seq) * 100, 2)


def max_homopolymer_run(sequence: str) -> int:
    """Calcula o maior trecho consecutivo da mesma base."""

    if not sequence:
        return 0
    max_run = 1
    current_run = 1
    previous = sequence[0]
    for base in sequence[1:]:
        if base == previous:
            current_run += 1
        else:
            max_run = max(max_run, current_run)
            current_run = 1
            previous = base
    return max(max_run, current_run)
