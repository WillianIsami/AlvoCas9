"""Testes sobre a sequencia biologica real versionada no projeto.

Estes testes protegem os numeros citados em
``docs/RESULTADO_SEQUENCIA_REAL.md`` e, futuramente, na monografia. Se uma
alteracao no scanner ou nos filtros mudar qualquer um deles, estes testes
falham e obrigam a atualizar os documentos junto com o codigo.
"""

from __future__ import annotations

import collections
import hashlib
from pathlib import Path

from alvocas9.analysis.features import add_candidate_features
from alvocas9.analysis.filters import APPROVED, CAUTION, FAILED, apply_filters
from alvocas9.config import PipelineConfig
from alvocas9.core.scanner import scan_records
from alvocas9.validation.dna_validator import validate_fasta

ADE2 = Path(__file__).resolve().parents[1] / "data" / "real" / "ADE2_scerevisiae.fasta"


def test_real_sequence_file_is_intact() -> None:
    """Confere a sequencia pelo hash registrado em data/real/README.md."""

    registros = validate_fasta(ADE2).records
    sequencia = registros[0].sequence

    assert len(sequencia) == 1716
    assert set(sequencia) <= set("ACGT")
    assert (
        hashlib.sha256(sequencia.encode()).hexdigest()
        == "e8a7e4e218061b7b19f7d3551a5b411817e21f0fb3bc1c7e1c35fee27c68ba34"
    )


def test_real_sequence_is_a_complete_coding_sequence() -> None:
    """Verificacao biologica: fase, inicio, fim e ausencia de parada interna."""

    sequencia = validate_fasta(ADE2).records[0].sequence

    assert len(sequencia) % 3 == 0
    assert sequencia[:3] == "ATG"
    assert sequencia[-3:] == "TAA"

    paradas_internas = [
        posicao
        for posicao in range(0, len(sequencia) - 3, 3)
        if sequencia[posicao : posicao + 3] in ("TAA", "TAG", "TGA")
    ]
    assert paradas_internas == []


def test_real_sequence_validates_without_errors_or_warnings() -> None:
    report = validate_fasta(ADE2)

    assert report.valid is True
    assert report.errors == []
    assert report.warnings == []
    assert report.records[0].sequence_id == "ADE2_YOR128C"


def test_real_sequence_produces_the_documented_counts(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=ADE2, output_dir=tmp_path / "out")
    report = validate_fasta(ADE2)

    scan_result = scan_records(report.records, config)
    stats = scan_result.stats_by_sequence["ADE2_YOR128C"]
    candidates = apply_filters(add_candidate_features(scan_result.candidates), config)

    assert stats.pams_found_plus == 80
    assert stats.pams_found_minus == 62
    assert stats.pams_found_total == 142
    assert stats.pams_skipped_insufficient_upstream_total == 2

    assert len(candidates) == 140
    assert collections.Counter(row["strand"] for row in candidates) == {"+": 78, "-": 62}

    status = collections.Counter(row["filter_status"] for row in candidates)
    assert status[APPROVED] == 80
    assert status[CAUTION] == 60
    assert status[FAILED] == 0


def test_real_sequence_pam_counts_match_the_base_composition_model() -> None:
    """O numero de PAMs deve bater com o previsto pela composicao de bases.

    Para o padrao NGG, a chance de uma posicao iniciar um PAM e ``f(G)**2`` na
    fita direta. Na fita reversa complementar, um GG corresponde a um CC na
    sequencia original, entao a chance e ``f(C)**2``. A tolerancia de 15% cobre
    a variacao estatistica de uma sequencia unica.
    """

    sequencia = validate_fasta(ADE2).records[0].sequence
    tamanho = len(sequencia)
    frequencia_g = sequencia.count("G") / tamanho
    frequencia_c = sequencia.count("C") / tamanho

    previsto_mais = tamanho * frequencia_g**2
    previsto_menos = tamanho * frequencia_c**2

    assert abs(80 - previsto_mais) / previsto_mais < 0.15
    assert abs(62 - previsto_menos) / previsto_menos < 0.15
