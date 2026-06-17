from __future__ import annotations

from collections import Counter
from pathlib import Path


def create_plots(candidates: list[dict[str, object]], output_dir: str | Path) -> None:
    """Gera graficos PNG do conjunto de candidatos."""

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figures_dir = Path(output_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    _bar_plot(
        plt,
        Counter(str(candidate["sequence_id"]) for candidate in candidates),
        figures_dir / "candidates_per_sequence.png",
        "Candidatos por sequencia",
        "Sequencia",
        "Quantidade de candidatos",
    )

    gc_values = [float(candidate["gc_percent"]) for candidate in candidates]
    plt.figure(figsize=(7, 4))
    if gc_values:
        plt.hist(gc_values, bins=10, color="#4C78A8", edgecolor="black")
    else:
        plt.text(0.5, 0.5, "Sem candidatos", ha="center", va="center")
        plt.xlim(0, 1)
        plt.ylim(0, 1)
    plt.title("Distribuicao de GC% nos candidatos")
    plt.xlabel("GC%")
    plt.ylabel("Quantidade")
    plt.tight_layout()
    plt.savefig(figures_dir / "gc_distribution_candidates.png", dpi=160)
    plt.close()

    _bar_plot(
        plt,
        Counter(str(candidate["filter_status"]) for candidate in candidates),
        figures_dir / "filter_status_summary.png",
        "Resumo dos filtros",
        "Status",
        "Quantidade",
    )


def _bar_plot(plt, counter: Counter[str], path: Path, title: str, xlabel: str, ylabel: str) -> None:
    plt.figure(figsize=(7, 4))
    if counter:
        labels = list(counter.keys())
        values = [counter[label] for label in labels]
        plt.bar(labels, values, color="#59A14F")
        plt.xticks(rotation=25, ha="right")
    else:
        plt.text(0.5, 0.5, "Sem dados", ha="center", va="center")
        plt.xlim(0, 1)
        plt.ylim(0, 1)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
