import hashlib
import json
import platform
import random
import re
from pathlib import Path

import pytest

import alvocas9

from alvocas9.analysis.features import add_candidate_features, build_sequence_summary
from alvocas9.analysis.filters import apply_filters, rank_candidates
from alvocas9.config import PipelineConfig
from alvocas9.core.scanner import scan_records
from alvocas9.io.fasta_reader import FastaRecord
from alvocas9.reporting.report_generator import (
    FORBIDDEN_REPORT_TERMS,
    LIMITATION_TEXT,
    REPORT_MAX_CANDIDATE_ROWS,
    REPORT_TITLE,
    _assert_report_language,
    _candidates_table_note,
    _format_generated_at,
    write_pipeline_outputs,
)
from alvocas9.validation.dna_validator import ValidationMessage, ValidationReport


def test_report_generator_writes_tables_json_figures_and_reports(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "input.fasta", output_dir=tmp_path / "out")
    records = [FastaRecord("seq1", "A" * 20 + "AGG")]
    validation = ValidationReport(str(config.input_path), True, records=records)
    scan_result = scan_records(records, config)
    candidates = apply_filters(add_candidate_features(scan_result.candidates), config)

    generated_files = write_pipeline_outputs(
        config=config,
        validation=validation,
        sequence_summary=build_sequence_summary(records),
        candidates=candidates,
        stats_by_sequence=scan_result.stats_by_sequence,
    )

    assert "reports/technical_report.html" in generated_files
    assert "reports/technical_report.md" in generated_files
    assert (config.output_dir / "figures" / "candidates_per_sequence.png").exists()
    assert (config.output_dir / "reports" / "technical_report.html").exists()
    assert (config.output_dir / "reports" / "technical_report.md").exists()
    candidates_json = json.loads((config.output_dir / "json" / "candidates.json").read_text(encoding="utf-8"))
    assert candidates_json[0]["pam_sequence_5to3"] == "AGG"


def test_technical_report_contains_required_sections_and_terms(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "input.fasta", output_dir=tmp_path / "out")
    records = [FastaRecord("seq1", "ACGT" * 6 + "AGG")]
    validation = ValidationReport(
        str(config.input_path),
        True,
        records=records,
        global_warnings=[ValidationMessage("warning", "Aviso didatico.")],
    )
    scan_result = scan_records(records, config)
    candidates = apply_filters(add_candidate_features(scan_result.candidates), config)

    write_pipeline_outputs(
        config=config,
        validation=validation,
        sequence_summary=build_sequence_summary(records),
        candidates=candidates,
        stats_by_sequence=scan_result.stats_by_sequence,
    )

    html = (config.output_dir / "reports" / "technical_report.html").read_text(encoding="utf-8")
    markdown = (config.output_dir / "reports" / "technical_report.md").read_text(encoding="utf-8")
    combined = html + "\n" + markdown

    assert REPORT_TITLE in combined
    assert "AlvoCas9" in combined
    assert "Arquivo analisado" in combined
    assert "Configurações" in combined
    assert "Resumo das sequências" in combined
    assert "Resumo da validação" in combined
    assert "CRISPR-Cas9" in combined
    assert "PAM" in combined
    assert "NGG" in combined
    assert "candidato in silico" in combined
    assert "triagem exploratória" in combined
    assert "Resumo dos candidatos" in combined
    assert "Candidatos por sequência" in combined
    assert "Candidatos por fita" in combined
    assert "Status dos filtros" in combined
    assert "Tabela de candidatos" in combined
    assert "Gráficos" in combined
    assert "Interpretação conservadora" in combined
    assert "Limitações técnicas, biológicas e éticas" in combined
    assert "Arquivos gerados" in combined
    assert LIMITATION_TEXT in combined
    assert "potencial sítio-alvo" in combined
    assert "filtros básicos" in combined
    assert "Aviso didatico." in combined


def test_technical_report_avoids_forbidden_terms(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "input.fasta", output_dir=tmp_path / "out")
    records = [FastaRecord("seq1", "A" * 20 + "TGG")]
    validation = ValidationReport(str(config.input_path), True, records=records)
    scan_result = scan_records(records, config)
    candidates = apply_filters(add_candidate_features(scan_result.candidates), config)

    write_pipeline_outputs(
        config=config,
        validation=validation,
        sequence_summary=build_sequence_summary(records),
        candidates=candidates,
        stats_by_sequence=scan_result.stats_by_sequence,
    )

    html = (config.output_dir / "reports" / "technical_report.html").read_text(encoding="utf-8")
    markdown = (config.output_dir / "reports" / "technical_report.md").read_text(encoding="utf-8")
    lowered = (html + "\n" + markdown).lower()

    for forbidden in FORBIDDEN_REPORT_TERMS:
        assert forbidden not in lowered


def test_run_config_records_what_is_needed_to_reproduce(tmp_path: Path) -> None:
    """O run_config precisa identificar versao, ambiente e dado de entrada."""

    entrada = tmp_path / "input.fasta"
    conteudo = ">seq1\n" + "A" * 20 + "AGG\n"
    entrada.write_text(conteudo, encoding="utf-8")

    config = PipelineConfig(input_path=entrada, output_dir=tmp_path / "out")
    records = [FastaRecord("seq1", "A" * 20 + "AGG")]
    validation = ValidationReport(str(config.input_path), True, records=records)
    scan_result = scan_records(records, config)
    candidates = apply_filters(add_candidate_features(scan_result.candidates), config)

    write_pipeline_outputs(
        config=config,
        validation=validation,
        sequence_summary=build_sequence_summary(records),
        candidates=candidates,
        stats_by_sequence=scan_result.stats_by_sequence,
    )

    run_config = json.loads(
        (config.output_dir / "json" / "run_config.json").read_text(encoding="utf-8")
    )

    assert run_config["alvocas9_version"] == alvocas9.__version__
    assert run_config["python_version"] == platform.python_version()
    assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", run_config["executed_at"])
    assert (
        run_config["input_sha256"]
        == hashlib.sha256(entrada.read_bytes()).hexdigest()
    )
    # Os parametros continuam presentes, lado a lado com os metadados.
    assert run_config["pam"] == "NGG"
    assert run_config["target_length"] == 20


def test_run_config_tolerates_an_unreadable_input(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "nao_existe.fasta", output_dir=tmp_path / "out")
    records = [FastaRecord("seq1", "A" * 20 + "AGG")]
    validation = ValidationReport(str(config.input_path), True, records=records)
    scan_result = scan_records(records, config)
    candidates = apply_filters(add_candidate_features(scan_result.candidates), config)

    write_pipeline_outputs(
        config=config,
        validation=validation,
        sequence_summary=build_sequence_summary(records),
        candidates=candidates,
        stats_by_sequence=scan_result.stats_by_sequence,
    )

    run_config = json.loads(
        (config.output_dir / "json" / "run_config.json").read_text(encoding="utf-8")
    )
    assert run_config["input_sha256"] is None


def test_bed_export_converts_the_coordinate_system(tmp_path: Path) -> None:
    """O BED usa coordenadas 0-based semiabertas; o projeto usa 1-based inclusivas.

    Cada linha precisa ter seis colunas separadas por tabulacao, com o inicio
    deslocado em uma base e o fim inalterado.
    """

    config = PipelineConfig(input_path=tmp_path / "input.fasta", output_dir=tmp_path / "out")
    # A primeira sequencia gera candidato na fita +, a segunda na fita -.
    records = [FastaRecord("seq1", "A" * 20 + "AGG"), FastaRecord("seq2", "CCT" + "T" * 20)]
    validation = ValidationReport(str(config.input_path), True, records=records)
    scan_result = scan_records(records, config)
    candidates = rank_candidates(
        apply_filters(add_candidate_features(scan_result.candidates), config)
    )

    write_pipeline_outputs(
        config=config,
        validation=validation,
        sequence_summary=build_sequence_summary(records),
        candidates=candidates,
        stats_by_sequence=scan_result.stats_by_sequence,
    )

    linhas = (config.output_dir / "tables" / "candidates.bed").read_text(
        encoding="utf-8"
    ).splitlines()
    assert len(linhas) == len(candidates)

    for linha, candidato in zip(linhas, candidates):
        colunas = linha.split("\t")
        assert len(colunas) == 6
        chrom, inicio, fim, nome, score, strand = colunas
        assert chrom == candidato["sequence_id"]
        assert int(inicio) == int(candidato["full_candidate_start_1based"]) - 1
        assert int(fim) == int(candidato["full_candidate_end_1based"])
        assert int(score) == int(candidato["heuristic_score"]) * 10
        assert strand == candidato["strand"]
        assert nome.startswith(str(candidato["sequence_id"]))

    # O intervalo em BED tem o mesmo comprimento do intervalo 1-based inclusivo.
    primeiro = linhas[0].split("\t")
    candidato = candidates[0]
    comprimento_bed = int(primeiro[2]) - int(primeiro[1])
    comprimento_1based = (
        int(candidato["full_candidate_end_1based"])
        - int(candidato["full_candidate_start_1based"])
        + 1
    )
    assert comprimento_bed == comprimento_1based

    assert "-" in {linha.split("\t")[5] for linha in linhas}


def test_density_figure_is_generated(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "input.fasta", output_dir=tmp_path / "out")
    records = [FastaRecord("seq1", "ACGT" * 6 + "AGG")]
    validation = ValidationReport(str(config.input_path), True, records=records)
    scan_result = scan_records(records, config)
    candidates = apply_filters(add_candidate_features(scan_result.candidates), config)

    gerados = write_pipeline_outputs(
        config=config,
        validation=validation,
        sequence_summary=build_sequence_summary(records),
        candidates=candidates,
        stats_by_sequence=scan_result.stats_by_sequence,
    )

    assert "figures/candidate_density.png" in gerados
    assert (config.output_dir / "figures" / "candidate_density.png").is_file()


def test_generated_files_list_matches_what_is_on_disk(tmp_path: Path) -> None:
    """A lista devolvida precisa ser conferida em disco, e nao fixa no codigo."""

    config = PipelineConfig(input_path=tmp_path / "input.fasta", output_dir=tmp_path / "out")
    records = [FastaRecord("seq1", "A" * 20 + "AGG")]
    validation = ValidationReport(str(config.input_path), True, records=records)
    scan_result = scan_records(records, config)
    candidates = apply_filters(add_candidate_features(scan_result.candidates), config)

    gerados = write_pipeline_outputs(
        config=config,
        validation=validation,
        sequence_summary=build_sequence_summary(records),
        candidates=candidates,
        stats_by_sequence=scan_result.stats_by_sequence,
    )

    em_disco = {
        caminho.relative_to(config.output_dir).as_posix()
        for caminho in config.output_dir.rglob("*")
        if caminho.is_file()
    }
    assert set(gerados) == em_disco

    # O log nao existe aqui, porque quem o cria e a CLI. A lista precisa
    # refleti-lo: nada de afirmar arquivo que nao foi gravado.
    assert "logs/pipeline.log" not in gerados


def test_validation_json_does_not_duplicate_the_input_sequence(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "input.fasta", output_dir=tmp_path / "out")
    sequencia = "ACGT" * 6 + "AGG"
    records = [FastaRecord("seq1", sequencia)]
    validation = ValidationReport(str(config.input_path), True, records=records)
    scan_result = scan_records(records, config)
    candidates = apply_filters(add_candidate_features(scan_result.candidates), config)

    write_pipeline_outputs(
        config=config,
        validation=validation,
        sequence_summary=build_sequence_summary(records),
        candidates=candidates,
        stats_by_sequence=scan_result.stats_by_sequence,
    )

    bruto = (config.output_dir / "json" / "validation.json").read_text(encoding="utf-8")
    registro = json.loads(bruto)["records"][0]

    assert sequencia not in bruto
    assert registro["length"] == len(sequencia)
    assert registro["sequence_sha256"] == hashlib.sha256(sequencia.encode()).hexdigest()


def test_report_truncates_the_candidate_table_and_explains_it(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "input.fasta", output_dir=tmp_path / "out")
    gerador = random.Random(7)
    sequencia = "".join(gerador.choice("ACGT") for _ in range(1000))
    records = [FastaRecord("seq1", sequencia)]
    validation = ValidationReport(str(config.input_path), True, records=records)
    scan_result = scan_records(records, config)
    candidates = rank_candidates(
        apply_filters(add_candidate_features(scan_result.candidates), config)
    )

    write_pipeline_outputs(
        config=config,
        validation=validation,
        sequence_summary=build_sequence_summary(records),
        candidates=candidates,
        stats_by_sequence=scan_result.stats_by_sequence,
    )

    assert len(candidates) > REPORT_MAX_CANDIDATE_ROWS

    markdown = (config.output_dir / "reports" / "technical_report.md").read_text(encoding="utf-8")
    assert f"os {REPORT_MAX_CANDIDATE_ROWS} candidatos de maior score" in markdown
    assert f"de um total de {len(candidates)}" in markdown
    assert str(candidates[0]["protospacer_sequence_5to3"]) in markdown

    csv_lines = (config.output_dir / "tables" / "candidates.csv").read_text(
        encoding="utf-8"
    ).splitlines()
    assert len(csv_lines) == len(candidates) + 1

    candidates_json = json.loads(
        (config.output_dir / "json" / "candidates.json").read_text(encoding="utf-8")
    )
    assert len(candidates_json) == len(candidates)


def test_report_has_no_truncation_note_when_the_table_fits(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "input.fasta", output_dir=tmp_path / "out")
    records = [FastaRecord("seq1", "A" * 20 + "AGG")]
    validation = ValidationReport(str(config.input_path), True, records=records)
    scan_result = scan_records(records, config)
    candidates = rank_candidates(
        apply_filters(add_candidate_features(scan_result.candidates), config)
    )

    write_pipeline_outputs(
        config=config,
        validation=validation,
        sequence_summary=build_sequence_summary(records),
        candidates=candidates,
        stats_by_sequence=scan_result.stats_by_sequence,
    )

    markdown = (config.output_dir / "reports" / "technical_report.md").read_text(encoding="utf-8")
    assert "de um total de" not in markdown


def test_candidates_table_note_is_empty_without_truncation() -> None:
    assert _candidates_table_note(10, 10) == ""
    assert _candidates_table_note(3, 50) == ""
    assert "de um total de 120" in _candidates_table_note(120, 50)


def test_report_includes_the_cut_site_column(tmp_path: Path) -> None:
    config = PipelineConfig(input_path=tmp_path / "input.fasta", output_dir=tmp_path / "out")
    records = [FastaRecord("seq1", "A" * 20 + "AGG")]
    validation = ValidationReport(str(config.input_path), True, records=records)
    scan_result = scan_records(records, config)
    candidates = apply_filters(add_candidate_features(scan_result.candidates), config)

    write_pipeline_outputs(
        config=config,
        validation=validation,
        sequence_summary=build_sequence_summary(records),
        candidates=candidates,
        stats_by_sequence=scan_result.stats_by_sequence,
    )

    candidates_json = json.loads(
        (config.output_dir / "json" / "candidates.json").read_text(encoding="utf-8")
    )
    assert candidates_json[0]["cut_site_1based"] == 17

    markdown = (config.output_dir / "reports" / "technical_report.md").read_text(encoding="utf-8")
    assert "cut_site_1based" in markdown
    assert "premissa do modelo para SpCas9" in markdown

    html = (config.output_dir / "reports" / "technical_report.html").read_text(encoding="utf-8")
    assert "cut_site_1based" in html


def test_language_check_actually_refuses_a_forbidden_phrase() -> None:
    """O controle de linguagem precisa falhar quando deve falhar.

    Este e o unico mecanismo do projeto que impede, em codigo, a publicacao de
    um relatorio com afirmacao indevida sobre os candidatos. Ate aqui ele nunca
    tinha sido exercitado: todos os testes verificavam apenas que relatorios
    legitimos passam.
    """

    texto_legitimo = "Os candidatos sao candidatos in silico, sem recomendacao."
    _assert_report_language(texto_legitimo)

    for frase in FORBIDDEN_REPORT_TERMS:
        with pytest.raises(ValueError, match="termo proibido"):
            _assert_report_language(f"Resultado da triagem: {frase} para uso.")


def test_generated_at_uses_configured_timezone() -> None:
    assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \S+$", _format_generated_at())


def test_generated_at_falls_back_without_timezone_database() -> None:
    carimbo = _format_generated_at("Fuso/Inexistente")

    assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4}$", carimbo)
