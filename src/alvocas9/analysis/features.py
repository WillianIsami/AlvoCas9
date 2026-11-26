from __future__ import annotations

from collections import Counter

from alvocas9.analysis.filters import apply_filters
from alvocas9.core.sequence_utils import gc_percent, max_homopolymer_run
from alvocas9.io.fasta_reader import FastaRecord


def build_sequence_summary(records: list[FastaRecord]) -> list[dict[str, object]]:
    """Gera resumo basico por sequencia de entrada."""

    rows: list[dict[str, object]] = []
    for record in records:
        n_count = record.sequence.count("N")
        rows.append(
            {
                "sequence_id": record.sequence_id,
                "length": len(record.sequence),
                "gc_percent": gc_percent(record.sequence),
                "n_count": n_count,
                "n_percent": round((n_count / len(record.sequence) * 100) if record.sequence else 0.0, 2),
            }
        )
    return rows


def add_candidate_features(candidates: list[dict[str, object]]) -> list[dict[str, object]]:
    """Adiciona caracteristicas calculadas aos candidatos."""

    duplicate_counts = Counter(
        str(candidate["protospacer_sequence_5to3"]) for candidate in candidates
    )
    enriched: list[dict[str, object]] = []
    for candidate in candidates:
        row = dict(candidate)
        protospacer = str(row["protospacer_sequence_5to3"])
        n_count = protospacer.count("N")
        row["gc_percent"] = gc_percent(protospacer)
        row["n_count"] = n_count
        row["has_n"] = n_count > 0
        row["max_homopolymer_run"] = max_homopolymer_run(protospacer)
        row["duplicate_exact_count_within_input"] = duplicate_counts[protospacer]
        enriched.append(row)
    return enriched


def characterize_candidates(
    candidates: list[dict[str, object]],
    config: object | None = None,
) -> list[dict[str, object]]:
    """Calcula features, warnings, score e status em uma unica chamada.

    API auxiliar de conveniencia. O pipeline chama ``add_candidate_features``
    e ``filters.apply_filters`` em sequencia, para registrar no log o estado
    intermediario.
    """

    return apply_filters(add_candidate_features(candidates), config)
