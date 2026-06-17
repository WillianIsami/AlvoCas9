import json
from pathlib import Path

from alvocas9.analysis.features import add_candidate_features, build_sequence_summary
from alvocas9.analysis.filters import apply_filters
from alvocas9.config import PipelineConfig
from alvocas9.core.scanner import scan_records
from alvocas9.io.fasta_reader import FastaRecord
from alvocas9.reporting.report_generator import (
    FORBIDDEN_REPORT_TERMS,
    LIMITATION_TEXT,
    REPORT_TITLE,
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
