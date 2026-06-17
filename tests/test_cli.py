from pathlib import Path
import json

from alvocas9.cli import main
from alvocas9.reporting.report_generator import CANDIDATE_COLUMNS


def test_cli_validate_valid_file(tmp_path: Path, capsys) -> None:
    fasta = tmp_path / "valid.fasta"
    fasta.write_text(">seq1\nACGTACGTACGTACGTACGT\n", encoding="utf-8")

    exit_code = main(["validate", "--input", str(fasta)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Valido: True" in captured.out


def test_cli_analyze_generates_expected_outputs(tmp_path: Path) -> None:
    fasta = tmp_path / "valid.fasta"
    output = tmp_path / "results"
    fasta.write_text(">seq1\n" + "A" * 20 + "AGG\n", encoding="utf-8")

    exit_code = main(["analyze", "--input", str(fasta), "--output", str(output)])

    assert exit_code == 0
    assert (output / "tables" / "sequences_summary.csv").exists()
    assert (output / "tables" / "candidates.csv").exists()
    assert (output / "tables" / "validation_summary.csv").exists()
    assert (output / "json" / "validation.json").exists()
    assert (output / "json" / "candidates.json").exists()
    assert (output / "json" / "run_config.json").exists()
    assert (output / "figures" / "candidates_per_sequence.png").exists()
    assert (output / "figures" / "gc_distribution_candidates.png").exists()
    assert (output / "figures" / "filter_status_summary.png").exists()
    assert (output / "reports" / "technical_report.html").exists()
    assert (output / "reports" / "technical_report.md").exists()
    assert (output / "logs" / "pipeline.log").exists()
    header = (output / "tables" / "candidates.csv").read_text(encoding="utf-8").splitlines()[0]
    assert header.split(",") == CANDIDATE_COLUMNS


def test_cli_analyze_accepts_config_options_and_warnings_continue(tmp_path: Path) -> None:
    fasta = tmp_path / "with_warning.fasta"
    output = tmp_path / "results"
    fasta.write_text(">seq1\n" + "A" * 20 + "AGG\n", encoding="utf-8")

    exit_code = main(
        [
            "analyze",
            "--input",
            str(fasta),
            "--output",
            str(output),
            "--pam",
            "NGG",
            "--target-length",
            "20",
            "--min-gc",
            "40",
            "--max-gc",
            "60",
            "--max-homopolymer",
            "4",
            "--min-sequence-length",
            "30",
        ]
    )

    assert exit_code == 0
    validation = json.loads((output / "json" / "validation.json").read_text(encoding="utf-8"))
    assert validation["valid"] is True
    assert validation["warnings"]
    html = (output / "reports" / "technical_report.html").read_text(encoding="utf-8")
    assert "Resumo da validação" in html
    assert "Sequencia curta" in html


def test_cli_analyze_with_critical_validation_error_writes_validation_and_log(
    tmp_path: Path,
    capsys,
) -> None:
    fasta = tmp_path / "invalid.fasta"
    output = tmp_path / "results"
    fasta.write_text(">seq1\nACGTXXXXACGTACGTACGT\n", encoding="utf-8")

    exit_code = main(["analyze", "--input", str(fasta), "--output", str(output)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "FASTA invalido" in captured.err
    assert (output / "json" / "validation.json").exists()
    assert (output / "logs" / "pipeline.log").exists()
    assert not (output / "tables" / "candidates.csv").exists()
    validation = json.loads((output / "json" / "validation.json").read_text(encoding="utf-8"))
    assert validation["valid"] is False
    log_text = (output / "logs" / "pipeline.log").read_text(encoding="utf-8")
    assert "Inicio da execucao" in log_text
    assert "Validacao critica falhou" in log_text
    assert "Fim da execucao com erro de validacao" in log_text
