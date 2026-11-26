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


def test_cli_validate_prints_errors_and_warnings(tmp_path: Path, capsys) -> None:
    fasta = tmp_path / "invalid.fasta"
    fasta.write_text(">seq1\nACGTXXXXACGTACGTACGT\n>seq2\nACGT\n", encoding="utf-8")

    exit_code = main(["validate", "--input", str(fasta)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Valido: False" in captured.out
    assert "ERRO: [seq1] Sequencia contem caracteres nao permitidos: X." in captured.out
    assert "AVISO: [seq2] Sequencia curta" in captured.out


def test_cli_analyze_generates_expected_outputs(tmp_path: Path) -> None:
    fasta = tmp_path / "valid.fasta"
    output = tmp_path / "results"
    fasta.write_text(">seq1\n" + "A" * 20 + "AGG\n", encoding="utf-8")

    exit_code = main(["analyze", "--input", str(fasta), "--output", str(output)])

    assert exit_code == 0
    assert (output / "tables" / "sequences_summary.csv").exists()
    assert (output / "tables" / "candidates.csv").exists()
    assert (output / "tables" / "candidates.bed").exists()
    assert (output / "tables" / "validation_summary.csv").exists()
    assert (output / "json" / "validation.json").exists()
    assert (output / "json" / "candidates.json").exists()
    assert (output / "json" / "run_config.json").exists()
    assert (output / "figures" / "candidates_per_sequence.png").exists()
    assert (output / "figures" / "gc_distribution_candidates.png").exists()
    assert (output / "figures" / "filter_status_summary.png").exists()
    assert (output / "figures" / "candidate_density.png").exists()
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


def test_cli_analyze_prints_run_summary(tmp_path: Path, capsys) -> None:
    fasta = tmp_path / "valid.fasta"
    output = tmp_path / "results"
    fasta.write_text(">seq1\n" + "A" * 20 + "AGG\n", encoding="utf-8")

    exit_code = main(["analyze", "--input", str(fasta), "--output", str(output)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Analise concluida." in captured.out
    assert "Sequencias lidas: 1" in captured.out
    assert "Avisos de validacao: 0" in captured.out
    assert "PAMs encontrados: 1" in captured.out
    assert "Candidatos extraidos: 1" in captured.out
    assert str(output) in captured.out
    assert "technical_report.html" in captured.out


def test_cli_analyze_without_candidates_generates_empty_outputs(tmp_path: Path, capsys) -> None:
    fasta = tmp_path / "sem_pam.fasta"
    output = tmp_path / "results"
    fasta.write_text(">sem_pam\n" + "A" * 40 + "\n", encoding="utf-8")

    exit_code = main(["analyze", "--input", str(fasta), "--output", str(output)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "PAMs encontrados: 0" in captured.out
    assert "Candidatos extraidos: 0" in captured.out

    candidate_lines = (output / "tables" / "candidates.csv").read_text(encoding="utf-8").splitlines()
    assert candidate_lines[0].split(",") == CANDIDATE_COLUMNS
    assert len(candidate_lines) == 1

    assert (output / "figures" / "candidates_per_sequence.png").exists()
    assert (output / "figures" / "gc_distribution_candidates.png").exists()
    assert (output / "figures" / "filter_status_summary.png").exists()
    assert (output / "figures" / "candidate_density.png").exists()
    assert (output / "tables" / "candidates.bed").read_text(encoding="utf-8") == ""

    markdown = (output / "reports" / "technical_report.md").read_text(encoding="utf-8")
    assert "Total de candidatos: 0" in markdown
    assert "_Sem registros._" in markdown

    candidates_json = json.loads((output / "json" / "candidates.json").read_text(encoding="utf-8"))
    assert candidates_json == []


def test_cli_analyze_rejects_invalid_target_length(tmp_path: Path, capsys) -> None:
    fasta = tmp_path / "valid.fasta"
    output = tmp_path / "results"
    fasta.write_text(">seq1\n" + "A" * 20 + "AGG\n", encoding="utf-8")

    exit_code = main(
        ["analyze", "--input", str(fasta), "--output", str(output), "--target-length", "-5"]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "target_length" in captured.err
    assert not output.exists()


def test_cli_analyze_rejects_inverted_gc_range(tmp_path: Path, capsys) -> None:
    fasta = tmp_path / "valid.fasta"
    output = tmp_path / "results"
    fasta.write_text(">seq1\n" + "A" * 20 + "AGG\n", encoding="utf-8")

    exit_code = main(
        [
            "analyze",
            "--input",
            str(fasta),
            "--output",
            str(output),
            "--min-gc",
            "90",
            "--max-gc",
            "10",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "min_gc" in captured.err
    assert not output.exists()


def test_cli_analyze_rejects_five_prime_pam_position(tmp_path: Path, capsys) -> None:
    fasta = tmp_path / "valid.fasta"
    output = tmp_path / "results"
    fasta.write_text(">seq1\n" + "A" * 20 + "AGG\n", encoding="utf-8")

    exit_code = main(
        ["analyze", "--input", str(fasta), "--output", str(output), "--pam-position", "5linha"]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "pam_position aceita apenas" in captured.err
    assert not output.exists()


def test_cli_validate_rejects_invalid_min_sequence_length(tmp_path: Path, capsys) -> None:
    fasta = tmp_path / "valid.fasta"
    fasta.write_text(">seq1\nACGTACGTACGTACGTACGT\n", encoding="utf-8")

    exit_code = main(
        ["validate", "--input", str(fasta), "--min-sequence-length", "0"]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "min_sequence_length" in captured.err


def test_cli_analyze_logs_unexpected_failure(tmp_path: Path, monkeypatch, capsys) -> None:
    fasta = tmp_path / "valid.fasta"
    output = tmp_path / "results"
    fasta.write_text(">seq1\n" + "A" * 20 + "AGG\n", encoding="utf-8")

    def falha_simulada(**_kwargs: object) -> list[str]:
        raise RuntimeError("falha simulada na geracao das saidas")

    monkeypatch.setattr("alvocas9.cli.write_pipeline_outputs", falha_simulada)

    exit_code = main(["analyze", "--input", str(fasta), "--output", str(output)])

    captured = capsys.readouterr()
    log_text = (output / "logs" / "pipeline.log").read_text(encoding="utf-8")
    assert exit_code == 1
    assert "falha simulada na geracao das saidas" in captured.err
    assert "Falha inesperada durante a execucao do pipeline." in log_text
    assert "falha simulada na geracao das saidas" in log_text
    assert "Fim da execucao com erro." in log_text
