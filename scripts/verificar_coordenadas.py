"""Verificacao independente das coordenadas reportadas pelo AlvoCas9.

Este script nao confia no scanner: ele recupera o trecho da sequencia ORIGINAL
usando as coordenadas 1-based que o pipeline reportou, aplica reverso
complementar quando a fita e ``-``, e confere se o resultado bate com o
protospacer e o PAM informados. Confere tambem a adjacencia entre protospacer e
PAM e a posicao do sitio de corte.

E uma verificacao de fora para dentro, diferente dos testes unitarios, que
verificam a mesma logica por dentro. O mapeamento de coordenadas da fita
reversa complementar e o ponto do projeto onde um erro passaria despercebido:
o candidato pareceria valido e estaria na posicao errada.

Este script deve ser executado depois de qualquer alteracao no scanner. O
resultado esperado e zero divergencia e codigo de saida 0.

Uso:

    python scripts/verificar_coordenadas.py
    python scripts/verificar_coordenadas.py --tamanho 5000 --semente 42
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

from alvocas9.core.scanner import CAS9_CUT_OFFSET_FROM_PAM, Candidate, ScanConfig, extract_candidates_from_both_strands
from alvocas9.core.sequence_utils import reverse_complement
from alvocas9.io.fasta_reader import read_fasta

ROOT = Path(__file__).resolve().parents[1]
EXEMPLOS = ROOT / "data" / "examples"


def conferir(sequencia: str, candidato: Candidate) -> list[str]:
    """Devolve a lista de problemas encontrados neste candidato."""

    problemas: list[str] = []
    tamanho = len(sequencia)

    trecho_protospacer = sequencia[
        candidato.protospacer_start_1based - 1 : candidato.protospacer_end_1based
    ]
    trecho_pam = sequencia[candidato.pam_start_1based - 1 : candidato.pam_end_1based]

    if candidato.strand == "+":
        esperado_protospacer = trecho_protospacer
        esperado_pam = trecho_pam
        adjacente = candidato.pam_start_1based == candidato.protospacer_end_1based + 1
        corte_esperado = candidato.pam_start_1based - CAS9_CUT_OFFSET_FROM_PAM - 1
    else:
        esperado_protospacer = reverse_complement(trecho_protospacer)
        esperado_pam = reverse_complement(trecho_pam)
        adjacente = candidato.protospacer_start_1based == candidato.pam_end_1based + 1
        corte_esperado = candidato.pam_end_1based + CAS9_CUT_OFFSET_FROM_PAM

    if esperado_protospacer != candidato.protospacer_sequence_5to3:
        problemas.append(
            f"protospacer divergente: reportado {candidato.protospacer_sequence_5to3}, "
            f"derivado da sequencia original {esperado_protospacer}"
        )
    if esperado_pam != candidato.pam_sequence_5to3:
        problemas.append(
            f"PAM divergente: reportado {candidato.pam_sequence_5to3}, "
            f"derivado da sequencia original {esperado_pam}"
        )
    if not adjacente:
        problemas.append("protospacer e PAM nao sao adjacentes")

    if not 1 <= corte_esperado <= tamanho - 1:
        corte_esperado = None
    if candidato.cut_site_1based != corte_esperado:
        problemas.append(
            f"sitio de corte divergente: reportado {candidato.cut_site_1based}, "
            f"esperado {corte_esperado}"
        )

    dentro = (
        1 <= candidato.protospacer_start_1based <= tamanho
        and 1 <= candidato.protospacer_end_1based <= tamanho
        and 1 <= candidato.pam_start_1based <= tamanho
        and 1 <= candidato.pam_end_1based <= tamanho
    )
    if not dentro:
        problemas.append("coordenadas fora dos limites da sequencia")
    if candidato.protospacer_start_1based > candidato.protospacer_end_1based:
        problemas.append("coordenadas do protospacer invertidas")

    return problemas


def verificar_sequencia(nome: str, sequencia: str, config: ScanConfig) -> tuple[int, int]:
    candidatos = extract_candidates_from_both_strands(nome, sequencia, config)
    divergencias = 0

    for candidato in candidatos:
        problemas = conferir(sequencia, candidato)
        if problemas:
            divergencias += 1
            print(f"  FALHA em {nome}, fita {candidato.strand}, "
                  f"protospacer [{candidato.protospacer_start_1based}, "
                  f"{candidato.protospacer_end_1based}]:")
            for problema in problemas:
                print(f"    - {problema}")

    mais = sum(1 for candidato in candidatos if candidato.strand == "+")
    print(
        f"  {nome}: {len(candidatos)} candidato(s) "
        f"({mais} na fita +, {len(candidatos) - mais} na fita -), "
        f"{divergencias} divergencia(s)"
    )
    return len(candidatos), divergencias


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verifica as coordenadas reportadas pelo scanner.")
    parser.add_argument("--tamanho", type=int, default=2000, help="Tamanho da sequencia aleatoria.")
    parser.add_argument("--semente", type=int, default=20261116, help="Semente do gerador.")
    argumentos = parser.parse_args(argv)

    config = ScanConfig()
    total_candidatos = 0
    total_divergencias = 0

    print("== Arquivos de exemplo do projeto")
    for caminho in sorted(EXEMPLOS.glob("*.fasta")):
        leitura = read_fasta(caminho)
        for registro in leitura.records:
            if not registro.sequence or not set(registro.sequence) <= set("ACGTN"):
                continue
            candidatos, divergencias = verificar_sequencia(
                f"{caminho.name}:{registro.sequence_id}", registro.sequence, config
            )
            total_candidatos += candidatos
            total_divergencias += divergencias

    print()
    print(f"== Sequencia aleatoria de {argumentos.tamanho} bases (semente {argumentos.semente})")
    gerador = random.Random(argumentos.semente)
    aleatoria = "".join(gerador.choice("ACGT") for _ in range(argumentos.tamanho))
    candidatos, divergencias = verificar_sequencia("aleatoria", aleatoria, config)
    total_candidatos += candidatos
    total_divergencias += divergencias

    print()
    print(f"TOTAL: {total_candidatos} candidato(s) conferido(s), "
          f"{total_divergencias} divergencia(s).")

    if total_divergencias:
        print("RESULTADO: FALHOU. As coordenadas reportadas nao conferem.")
        return 1
    print("RESULTADO: OK. Todas as coordenadas conferem com a sequencia original.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
