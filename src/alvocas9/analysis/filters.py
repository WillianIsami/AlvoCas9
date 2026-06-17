from __future__ import annotations

from dataclasses import dataclass


APPROVED = "aprovado nos filtros básicos"
CAUTION = "requer cautela"
FAILED = "reprovado nos filtros básicos"


@dataclass(frozen=True, slots=True)
class FilterConfig:
    min_gc: float = 40.0
    max_gc: float = 60.0
    max_homopolymer: int = 4
    allow_n: bool = False

    @classmethod
    def from_object(cls, config: object) -> "FilterConfig":
        return cls(
            min_gc=float(getattr(config, "min_gc", 40.0)),
            max_gc=float(getattr(config, "max_gc", 60.0)),
            max_homopolymer=int(getattr(config, "max_homopolymer", 4)),
            allow_n=bool(getattr(config, "allow_n", False)),
        )


def apply_filters(candidates: list[dict[str, object]], config: object | None = None) -> list[dict[str, object]]:
    """Aplica filtros e score heuristico simples."""

    filter_config = FilterConfig.from_object(config) if config is not None else FilterConfig()
    filtered: list[dict[str, object]] = []

    for candidate in candidates:
        row = dict(candidate)
        warnings: list[str] = []
        critical_alert = False
        moderate_alert = False
        score = 100

        gc_value = float(row["gc_percent"])
        if gc_value < filter_config.min_gc or gc_value > filter_config.max_gc:
            warnings.append("GC fora da faixa configurada")
            score -= 20
            moderate_alert = True

        if bool(row["has_n"]):
            warnings.append("Contem N no protospacer")
            score -= 25
            if filter_config.allow_n:
                moderate_alert = True
            else:
                critical_alert = True

        if int(row["max_homopolymer_run"]) > filter_config.max_homopolymer:
            warnings.append("Homopolimero acima do limite configurado")
            score -= 10
            moderate_alert = True

        if int(row["duplicate_exact_count_within_input"]) > 1:
            warnings.append("Protospacer duplicado exatamente no conjunto de entrada")
            score -= 20
            moderate_alert = True

        row["warnings"] = warnings
        row["heuristic_score"] = max(0, min(100, score))
        if row["heuristic_score"] < 50 or critical_alert:
            row["filter_status"] = FAILED
        elif row["heuristic_score"] < 80 or moderate_alert:
            row["filter_status"] = CAUTION
        else:
            row["filter_status"] = APPROVED
        filtered.append(row)

    return filtered
