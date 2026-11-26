from pathlib import Path

from alvocas9.validation.dna_validator import validate_fasta


def test_validate_accepts_valid_fasta(tmp_path: Path) -> None:
    fasta = tmp_path / "valid.fasta"
    fasta.write_text(">seq1 descricao\nACGTACGTACGTACGTACGT\n", encoding="utf-8")

    report = validate_fasta(fasta)

    assert report.valid is True
    assert report.global_errors == []
    assert report.per_record_errors == {}
    assert len(report.records) == 1
    assert report.records[0].identifier == "seq1"
    assert report.records[0].description == "descricao"
    assert report.sequence_summaries[0].length == 20


def test_validate_accepts_multiple_sequences(tmp_path: Path) -> None:
    fasta = tmp_path / "multi.fasta"
    fasta.write_text(
        ">seq1\nACGTACGTACGTACGTACGT\n>seq2 segunda\nTTTTCCCCAAAAGGGGACGT\n",
        encoding="utf-8",
    )

    report = validate_fasta(fasta)

    assert report.valid is True
    assert [record.identifier for record in report.records] == ["seq1", "seq2"]
    assert report.records[1].description == "segunda"


def test_validate_rejects_missing_file(tmp_path: Path) -> None:
    report = validate_fasta(tmp_path / "nao_existe.fasta")

    assert report.valid is False
    assert report.records == []
    assert any("Arquivo nao existe" in error.message for error in report.global_errors)


def test_validate_rejects_path_that_is_not_a_file(tmp_path: Path) -> None:
    report = validate_fasta(tmp_path)

    assert report.valid is False
    assert report.records == []
    assert any("nao e um arquivo" in error.message for error in report.global_errors)


def test_validate_rejects_file_without_fasta_records(tmp_path: Path) -> None:
    fasta = tmp_path / "sem_registros.fasta"
    fasta.write_text("\n\n\n", encoding="utf-8")

    report = validate_fasta(fasta)

    assert report.valid is False
    assert report.records == []
    assert any("Nenhum registro FASTA" in error.message for error in report.global_errors)


def test_validate_rejects_empty_file(tmp_path: Path) -> None:
    fasta = tmp_path / "empty.fasta"
    fasta.write_text("", encoding="utf-8")

    report = validate_fasta(fasta)

    assert report.valid is False
    assert any("vazio" in error.message for error in report.global_errors)


def test_validate_reports_sequence_before_header(tmp_path: Path) -> None:
    fasta = tmp_path / "bad.fasta"
    fasta.write_text("ACGT\n>seq1\nACGTACGTACGTACGTACGT\n", encoding="utf-8")

    report = validate_fasta(fasta)

    assert report.valid is False
    assert any("antes do primeiro cabecalho" in error.message for error in report.global_errors)


def test_validate_rejects_empty_header(tmp_path: Path) -> None:
    fasta = tmp_path / "empty_header.fasta"
    fasta.write_text(">\nACGTACGTACGTACGTACGT\n", encoding="utf-8")

    report = validate_fasta(fasta)

    assert report.valid is False
    assert "record_1" in report.per_record_errors
    assert any("Cabecalho FASTA vazio" in error.message for error in report.per_record_errors["record_1"])


def test_validate_rejects_empty_sequence(tmp_path: Path) -> None:
    fasta = tmp_path / "empty_sequence.fasta"
    fasta.write_text(">seq1\n>seq2\nACGTACGTACGTACGTACGT\n", encoding="utf-8")

    report = validate_fasta(fasta)

    assert report.valid is False
    assert any("sequencia vazia" in error.message for error in report.per_record_errors["seq1"])


def test_validate_rejects_duplicate_id(tmp_path: Path) -> None:
    fasta = tmp_path / "duplicate.fasta"
    fasta.write_text(">seq1\nACGTACGTACGTACGTACGT\n>seq1\nTTTTCCCCAAAAGGGGACGT\n", encoding="utf-8")

    report = validate_fasta(fasta)

    assert report.valid is False
    assert any("duplicado" in error.message for error in report.per_record_errors["seq1"])


def test_validate_rejects_invalid_characters(tmp_path: Path) -> None:
    fasta = tmp_path / "invalid.fasta"
    fasta.write_text(">seq1\nACGTXXXXACGTACGTACGT\n", encoding="utf-8")

    report = validate_fasta(fasta)

    assert report.valid is False
    assert any("caracteres nao permitidos" in error.message for error in report.per_record_errors["seq1"])


def test_validate_allow_n_reports_warning(tmp_path: Path) -> None:
    fasta = tmp_path / "with_n.fasta"
    fasta.write_text(">seq1\nACGTACGTACGTACGTACGN\n", encoding="utf-8")

    report = validate_fasta(fasta, allow_n=True)

    assert report.valid is True
    assert len(report.warnings) == 1
    assert report.sequence_summaries[0].n_count == 1
    assert any("base(s) N" in warning.message for warning in report.per_record_warnings["seq1"])


def test_validate_rejects_n_without_flexible_mode(tmp_path: Path) -> None:
    fasta = tmp_path / "with_n.fasta"
    fasta.write_text(">seq1\nACGTACGTACGTACGTACGN\n", encoding="utf-8")

    report = validate_fasta(fasta, allow_n=False)

    assert report.valid is False
    assert any("N" in error.message for error in report.per_record_errors["seq1"])


def test_validate_short_sequence_is_warning(tmp_path: Path) -> None:
    fasta = tmp_path / "short.fasta"
    fasta.write_text(">seq1\nACGT\n", encoding="utf-8")

    report = validate_fasta(fasta, min_sequence_length=20)

    assert report.valid is True
    assert any("Sequencia curta" in warning.message for warning in report.per_record_warnings["seq1"])


def test_validate_high_n_percent_is_warning_in_flexible_mode(tmp_path: Path) -> None:
    fasta = tmp_path / "high_n.fasta"
    fasta.write_text(">seq1\nACGTNNNNNN\n", encoding="utf-8")

    report = validate_fasta(fasta, allow_n=True, high_n_percent_threshold=10)

    assert report.valid is True
    messages = " ".join(warning.message for warning in report.per_record_warnings["seq1"])
    assert "Proporcao alta de N" in messages


def test_validate_reports_tab_as_invalid_character(tmp_path: Path) -> None:
    fasta = tmp_path / "com_tab.fasta"
    fasta.write_text(">seq1\nACGT\tACGTACGTACGTACGT\n", encoding="utf-8")

    report = validate_fasta(fasta)

    assert report.valid is False
    assert any("<tab>" in error.message for error in report.per_record_errors["seq1"])


def test_validate_reports_space_as_invalid_character(tmp_path: Path) -> None:
    """O leitor FASTA preserva espacos para que a validacao possa reporta-los."""

    fasta = tmp_path / "com_espaco.fasta"
    fasta.write_text(">seq1\nACGT ACGTACGTACGTACGT\n", encoding="utf-8")

    report = validate_fasta(fasta)

    assert report.valid is False
    assert any("<espaco>" in error.message for error in report.per_record_errors["seq1"])
