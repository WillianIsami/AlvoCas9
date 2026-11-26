from __future__ import annotations

from collections import Counter
from pathlib import Path


def create_plots(candidates: list[dict[str, object]], output_dir: str | Path) -> list[Path]:
    """Gera graficos PNG do conjunto de candidatos.

    Devolve os caminhos dos arquivos gravados, para que o pipeline possa
    informar no log o que realmente foi gerado.
    """

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figures_dir = Path(output_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    gerados: list[Path] = []

    gerados.append(
        _bar_plot(
            plt,
            Counter(str(candidate["sequence_id"]) for candidate in candidates),
            figures_dir / "candidates_per_sequence.png",
            "Candidatos por sequencia",
            "Sequencia",
            "Quantidade de candidatos",
        )
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
    gc_path = figures_dir / "gc_distribution_candidates.png"
    plt.savefig(gc_path, dpi=160)
    plt.close()
    gerados.append(gc_path)

    gerados.append(
        _bar_plot(
            plt,
            Counter(str(candidate["filter_status"]) for candidate in candidates),
            figures_dir / "filter_status_summary.png",
            "Resumo dos filtros",
            "Status",
            "Quantidade",
        )
    )

    gerados.append(_density_plot(plt, candidates, figures_dir / "candidate_density.png"))

    return gerados


def _density_plot(plt, candidates: list[dict[str, object]], path: Path) -> Path:
    """Distribuicao dos candidatos ao longo da sequencia.

    Usa a posicao relativa em porcentagem, e nao a posicao absoluta, para que o
    grafico continue legivel quando a entrada tem varias sequencias de tamanhos
    diferentes.
    """

    posicoes = [
        float(candidate["relative_position_percent"])
        for candidate in candidates
        if candidate.get("relative_position_percent") is not None
    ]

    plt.figure(figsize=(7, 4))
    if posicoes:
        plt.hist(posicoes, bins=20, range=(0, 100), color="#B07AA1", edgecolor="black")
    else:
        plt.text(0.5, 0.5, "Sem candidatos", ha="center", va="center")
        plt.xlim(0, 1)
        plt.ylim(0, 1)
    plt.title("Distribuicao dos candidatos ao longo da sequencia")
    plt.xlabel("Posicao relativa na sequencia (%)")
    plt.ylabel("Quantidade de candidatos")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
    return path


def _bar_plot(plt, counter: Counter[str], path: Path, title: str, xlabel: str, ylabel: str) -> Path:
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
    return path
