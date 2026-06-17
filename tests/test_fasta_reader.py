from pathlib import Path

from alvocas9.io.fasta_reader import read_fasta


def test_read_fasta_valid_record(tmp_path: Path) -> None:
    fasta = tmp_path / "input.fasta"
    fasta.write_text(">seq1 descricao do gene\nacgt\nAC\n", encoding="utf-8")

    result = read_fasta(fasta)

    assert result.parse_errors == []
    assert len(result.records) == 1
    assert result.records[0].identifier == "seq1"
    assert result.records[0].sequence_id == "seq1"
    assert result.records[0].description == "descricao do gene"
    assert result.records[0].sequence == "ACGTAC"


def test_read_fasta_multiple_records(tmp_path: Path) -> None:
    fasta = tmp_path / "input.fasta"
    fasta.write_text(">seq1 primeira\nACGT\nAC\n>seq2\nTTTT\n", encoding="utf-8")

    result = read_fasta(fasta)

    assert result.parse_errors == []
    assert [record.identifier for record in result.records] == ["seq1", "seq2"]
    assert result.records[0].sequence == "ACGTAC"
    assert result.records[0].description == "primeira"
    assert result.records[1].description == ""


def test_read_fasta_reports_sequence_before_header(tmp_path: Path) -> None:
    fasta = tmp_path / "bad.fasta"
    fasta.write_text("ACGT\n>seq1\nACGT\n", encoding="utf-8")

    result = read_fasta(fasta)

    assert result.records[0].identifier == "seq1"
    assert result.parse_errors
    assert "antes do primeiro cabecalho" in result.parse_errors[0]


def test_read_fasta_keeps_invalid_characters_for_validator(tmp_path: Path) -> None:
    fasta = tmp_path / "invalid_chars.fasta"
    fasta.write_text(">seq1\nACX GT\n", encoding="utf-8")

    result = read_fasta(fasta)

    assert result.records[0].sequence == "ACX GT"
