"""Mede o desempenho da busca de PAM e da extracao de candidatos.

O script compara tres implementacoes da busca de PAM, confirma que todas
produzem exatamente o mesmo resultado e imprime os tempos em formato de tabela
Markdown, pronta para ser transportada para a monografia.

As sequencias de teste sao geradas com semente fixa, entao a mesma execucao
pode ser repetida em outra maquina e comparada.

Uso:

    python scripts/benchmark_busca_pam.py
    python scripts/benchmark_busca_pam.py --saida docs/DESEMPENHO_MEDIDO.md
"""

from __future__ import annotations

import argparse
import platform
import random
import sys
import time
from pathlib import Path

from alvocas9.core.pam import (
    find_pam_positions,
    find_pam_positions_by_scan,
    pam_matches,
    validate_pam_pattern,
)
from alvocas9.core.scanner import ScanConfig, extract_candidates_from_both_strands

TAMANHOS = (1_000, 10_000, 50_000, 200_000)
REPETICOES = 3
SEMENTE = 20261116
PAM = "NGG"


def busca_versao_inicial(sequence: str, pattern: str) -> list[int]:
    """Reproduz a primeira versao do projeto, para efeito de comparacao.

    Essa versao chamava ``pam_matches`` a cada posicao, e ``pam_matches``
    revalidava o padrao PAM inteiro antes de cada comparacao. A revalidacao
    era redundante, porque o padrao nao muda durante a varredura.
    """

    normalized_pattern = validate_pam_pattern(pattern)
    pam_length = len(normalized_pattern)
    seq = sequence.upper()
    positions: list[int] = []
    for start in range(0, len(seq) - pam_length + 1):
        fragment = seq[start : start + pam_length]
        if pam_matches(fragment, normalized_pattern):
            positions.append(start)
    return positions


IMPLEMENTACOES = (
    ("Versao inicial (revalidando o padrao)", busca_versao_inicial),
    ("Varredura direta", find_pam_positions_by_scan),
    ("Expressao regular com lookahead", find_pam_positions),
)


def numero(valor: float, casas: int = 2) -> str:
    """Formata um numero no padrao brasileiro: ponto nos milhares, virgula nos decimais."""

    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def gerar_sequencia(tamanho: int, semente: int) -> str:
    gerador = random.Random(semente)
    return "".join(gerador.choice("ACGT") for _ in range(tamanho))


def medir(funcao, *argumentos) -> tuple[float, object]:
    """Executa a funcao algumas vezes e devolve o menor tempo, em segundos.

    O menor tempo e usado porque variacoes para cima vem de interferencia do
    sistema operacional, e nao do algoritmo.
    """

    melhor = float("inf")
    resultado = None
    for _ in range(REPETICOES):
        inicio = time.perf_counter()
        resultado = funcao(*argumentos)
        melhor = min(melhor, time.perf_counter() - inicio)
    return melhor, resultado


def tabela_busca_pam() -> tuple[list[str], dict[int, int]]:
    linhas = [
        "| Tamanho da sequência | Implementação | Tempo (ms) | Taxa (kb/s) |",
        "| --- | --- | --- | --- |",
    ]
    pams_por_tamanho: dict[int, int] = {}

    for tamanho in TAMANHOS:
        sequencia = gerar_sequencia(tamanho, SEMENTE + tamanho)
        referencia: list[int] | None = None

        for nome, funcao in IMPLEMENTACOES:
            segundos, posicoes = medir(funcao, sequencia, PAM)

            if referencia is None:
                referencia = list(posicoes)
                pams_por_tamanho[tamanho] = len(referencia)
            elif list(posicoes) != referencia:
                raise SystemExit(
                    f"Divergencia entre implementacoes no tamanho {tamanho}: "
                    f"{nome} encontrou {len(posicoes)} PAMs e a referencia {len(referencia)}."
                )

            taxa = (tamanho / 1000) / segundos if segundos else float("inf")
            linhas.append(
                f"| {numero(tamanho, 0)} bp | {nome} | {numero(segundos * 1000)} | {numero(taxa, 0)} |"
            )

    return linhas, pams_por_tamanho


def tabela_extracao_candidatos() -> list[str]:
    linhas = [
        "| Tamanho da sequência | Candidatos extraídos | Tempo (ms) | Taxa (kb/s) |",
        "| --- | --- | --- | --- |",
    ]
    configuracao = ScanConfig()

    for tamanho in TAMANHOS:
        sequencia = gerar_sequencia(tamanho, SEMENTE + tamanho)
        segundos, candidatos = medir(
            extract_candidates_from_both_strands, "benchmark", sequencia, configuracao
        )
        taxa = (tamanho / 1000) / segundos if segundos else float("inf")
        linhas.append(
            f"| {numero(tamanho, 0)} bp | {numero(len(candidatos), 0)} | "
            f"{numero(segundos * 1000)} | {numero(taxa, 0)} |"
        )

    return linhas


def ganho_medido() -> str:
    sequencia = gerar_sequencia(TAMANHOS[-1], SEMENTE + TAMANHOS[-1])
    inicial, _ = medir(busca_versao_inicial, sequencia, PAM)
    direta, _ = medir(find_pam_positions_by_scan, sequencia, PAM)
    regex, _ = medir(find_pam_positions, sequencia, PAM)
    return (
        f"Nesta execução, em {TAMANHOS[-1] // 1000} kb, a varredura direta foi "
        f"{numero(inicial / direta, 1)} vezes mais rápida que a versão inicial, e a expressão "
        f"regular foi {numero(inicial / regex, 1)} vezes mais rápida que a versão inicial e "
        f"{numero(direta / regex, 1)} vezes mais rápida que a varredura direta. As razões "
        "variam de uma execução para outra; a ordem de grandeza é o que se mantém."
    )


def montar_relatorio() -> str:
    linhas_busca, pams = tabela_busca_pam()
    linhas_extracao = tabela_extracao_candidatos()

    partes = [
        "# Desempenho medido da busca de PAM",
        "",
        f"- Python: {platform.python_version()}",
        f"- Sistema: {platform.system()} {platform.release()} (build {platform.version()})",
        f"- Processador: {platform.processor() or 'nao informado'}",
        f"- Padrão PAM: `{PAM}`",
        f"- Repetições por medição: {REPETICOES} (menor tempo)",
        f"- Semente das sequências: {SEMENTE}",
        "",
        "## Busca de PAM em uma fita",
        "",
        "As três implementações foram verificadas durante a execução e produziram",
        "exatamente as mesmas posições em todos os tamanhos testados.",
        "",
        *linhas_busca,
        "",
        "PAMs encontrados por tamanho: "
        + ", ".join(
            f"{numero(tamanho, 0)} bp = {numero(total, 0)}" for tamanho, total in pams.items()
        )
        + ".",
        "",
        ganho_medido(),
        "",
        "## Extração completa de candidatos nas duas fitas",
        "",
        "Inclui reverso complementar, busca nas duas fitas, extração dos",
        "protospacers e mapeamento das coordenadas.",
        "",
        *linhas_extracao,
        "",
    ]
    return "\n".join(partes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mede o desempenho da busca de PAM.")
    parser.add_argument("--saida", type=Path, help="Arquivo Markdown para gravar o relatório.")
    argumentos = parser.parse_args(argv)

    relatorio = montar_relatorio()
    print(relatorio)

    if argumentos.saida:
        argumentos.saida.parent.mkdir(parents=True, exist_ok=True)
        argumentos.saida.write_text(relatorio, encoding="utf-8")
        print(f"Relatório gravado em: {argumentos.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
