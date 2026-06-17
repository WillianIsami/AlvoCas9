from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class FastaRecord:
    """Registro FASTA com identificador, descricao e sequencia normalizada."""

    identifier: str
    sequence: str
    description: str = ""

    @property
    def sequence_id(self) -> str:
        """Alias mantido para os demais modulos do pipeline."""

        return self.identifier


@dataclass(frozen=True, slots=True)
class FastaReadResult:
    records: list[FastaRecord]
    parse_errors: list[str]


def read_fasta(path: str | Path) -> FastaReadResult:
    """Le um FASTA simples sem assumir dependencias externas.

    O leitor normaliza bases para maiusculas, mas nao remove caracteres
    internos invalidos. Assim, entradas como ``ACXGT`` ou ``AC GT`` chegam ao
    validador e podem ser reportadas como erro.
    """

    fasta_path = Path(path)
    records: list[FastaRecord] = []
    errors: list[str] = []

    current_identifier: str | None = None
    current_description: str = ""
    sequence_lines: list[str] = []

    def flush_record() -> None:
        nonlocal current_identifier, current_description, sequence_lines
        if current_identifier is None:
            return
        sequence = "".join(sequence_lines).upper()
        records.append(
            FastaRecord(
                identifier=current_identifier,
                sequence=sequence,
                description=current_description,
            )
        )
        current_identifier = None
        current_description = ""
        sequence_lines = []

    try:
        with fasta_path.open("r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = raw_line.rstrip("\r\n")
                if not line:
                    continue
                if line.startswith(">"):
                    flush_record()
                    header = line[1:].strip()
                    if header:
                        parts = header.split(maxsplit=1)
                        current_identifier = parts[0]
                        current_description = parts[1] if len(parts) > 1 else ""
                    else:
                        current_identifier = ""
                        current_description = ""
                    continue
                if current_identifier is None:
                    errors.append(
                        f"Linha {line_number}: sequencia encontrada antes do primeiro cabecalho FASTA."
                    )
                    continue
                sequence_lines.append(line)
        flush_record()
    except OSError as exc:
        errors.append(f"Nao foi possivel ler o arquivo FASTA: {exc}")

    return FastaReadResult(records=records, parse_errors=errors)
