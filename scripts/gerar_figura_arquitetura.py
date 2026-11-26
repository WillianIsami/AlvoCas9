"""Gera a figura de arquitetura do pipeline AlvoCas9.

A figura e produzida por script, e nao desenhada a mao, para que possa ser
regerada a qualquer momento a partir da estrutura real do projeto. O arquivo
resultante e usado na monografia e tem fonte declarada como elaborado pelo
autor.

Uso:

    python scripts/gerar_figura_arquitetura.py

Saida:

    docs/figuras/arquitetura_pipeline.png
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "docs" / "figuras" / "arquitetura_pipeline.png"

FONT_FAMILY = "Arial"
EDGE_COLOR = "#1a1a1a"
MODULE_COLOR = "#4d4d4d"
PROCESS_FILL = "#ffffff"
BOUNDARY_FILL = "#e6e6e6"
ERROR_FILL = "#f2f2f2"

# Cada etapa do fluxo principal, na ordem de execucao: rotulo, modulo e tipo.
# O tipo "limite" marca entrada e saida de dados; "etapa", o processamento.
MAIN_FLOW = [
    ("Arquivo FASTA de entrada", "", "limite"),
    (
        "Interface de linha de comando\ne configuração da execução",
        "cli.py e config.py",
        "etapa",
    ),
    ("Leitura dos registros FASTA", "io/fasta_reader.py", "etapa"),
    (
        "Validação computacional\nseparando erros de avisos",
        "validation/dna_validator.py",
        "etapa",
    ),
    (
        "Busca de PAM e extração de candidatos\nnas fitas + e −",
        "core/pam.py e core/scanner.py",
        "etapa",
    ),
    (
        "Cálculo das características\ndos candidatos",
        "analysis/features.py",
        "etapa",
    ),
    ("Filtros heurísticos e score", "analysis/filters.py", "etapa"),
    (
        "Tabelas CSV, arquivos JSON, gráficos PNG,\nrelatórios HTML e Markdown, log",
        "reporting/report_generator.py e visualization/plots.py",
        "limite",
    ),
]

VALIDATION_INDEX = 3

ERROR_BRANCH = (
    "Erro crítico:\ngrava validation.json,\nrun_config.json e log,\ne encerra a execução",
    "",
    "erro",
)

FILLS = {"limite": BOUNDARY_FILL, "etapa": PROCESS_FILL, "erro": ERROR_FILL}

BOX_HEIGHT = 0.085
BOX_GAP = 0.031
MAIN_LEFT = 0.03
MAIN_RIGHT = 0.63
BRANCH_LEFT = 0.68
BRANCH_RIGHT = 0.99


def _draw_box(
    ax: plt.Axes,
    left: float,
    right: float,
    y_center: float,
    label: str,
    module: str,
    kind: str,
) -> None:
    width = right - left
    ax.add_patch(
        FancyBboxPatch(
            (left, y_center - BOX_HEIGHT / 2),
            width,
            BOX_HEIGHT,
            boxstyle="round,pad=0,rounding_size=0.010",
            linewidth=1.1,
            edgecolor=EDGE_COLOR,
            facecolor=FILLS[kind],
            linestyle="--" if kind == "erro" else "-",
        )
    )

    x_center = (left + right) / 2
    if module:
        ax.text(
            x_center,
            y_center + 0.012,
            label,
            ha="center",
            va="center",
            fontsize=9.0,
            fontfamily=FONT_FAMILY,
            color=EDGE_COLOR,
            linespacing=1.4,
        )
        ax.text(
            x_center,
            y_center - 0.026,
            module,
            ha="center",
            va="center",
            fontsize=7.0,
            fontfamily=FONT_FAMILY,
            color=MODULE_COLOR,
            style="italic",
        )
    else:
        ax.text(
            x_center,
            y_center,
            label,
            ha="center",
            va="center",
            fontsize=9.0,
            fontfamily=FONT_FAMILY,
            color=EDGE_COLOR,
            linespacing=1.4,
        )


def _draw_arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=11,
            linewidth=1.1,
            color=EDGE_COLOR,
            shrinkA=0,
            shrinkB=0,
        )
    )


def build_figure() -> plt.Figure:
    figure, ax = plt.subplots(figsize=(6.5, 9.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    total_height = len(MAIN_FLOW) * BOX_HEIGHT + (len(MAIN_FLOW) - 1) * BOX_GAP
    top = 0.5 + total_height / 2

    centers: list[float] = []
    for index, (label, module, kind) in enumerate(MAIN_FLOW):
        y_center = top - BOX_HEIGHT / 2 - index * (BOX_HEIGHT + BOX_GAP)
        centers.append(y_center)
        _draw_box(ax, MAIN_LEFT, MAIN_RIGHT, y_center, label, module, kind)

    x_center = (MAIN_LEFT + MAIN_RIGHT) / 2
    for previous, following in zip(centers, centers[1:]):
        _draw_arrow(
            ax,
            (x_center, previous - BOX_HEIGHT / 2),
            (x_center, following + BOX_HEIGHT / 2),
        )

    branch_y = centers[VALIDATION_INDEX]
    _draw_box(ax, BRANCH_LEFT, BRANCH_RIGHT, branch_y, *ERROR_BRANCH)
    _draw_arrow(ax, (MAIN_RIGHT, branch_y), (BRANCH_LEFT, branch_y))

    return figure


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure = build_figure()
    figure.savefig(OUTPUT_PATH, dpi=300, facecolor="white", bbox_inches="tight", pad_inches=0.08)
    plt.close(figure)
    print(f"Figura gravada em: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
