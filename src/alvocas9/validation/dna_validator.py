from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from alvocas9.io.fasta_reader import FastaRecord, read_fasta


@dataclass(frozen=True, slots=True)
class ValidationMessage:
    level: str
    message: str
    sequence_id: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "level": self.level,
            "sequence_id": self.sequence_id,
            "message": self.message,
        }


@dataclass(slots=True)
class SequenceValidationSummary:
    sequence_id: str
    length: int
    n_count: int
    n_percent: float
    valid: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "sequence_id": self.sequence_id,
            "length": self.length,
            "n_count": self.n_count,
            "n_percent": self.n_percent,
            "valid": self.valid,
        }


@dataclass(slots=True)
class ValidationReport:
    """Resultado estruturado da validacao FASTA.

    As propriedades ``errors`` e ``warnings`` agregam mensagens globais e por
    registro para manter compatibilidade com a CLI e os relatorios.
    """

    input_path: str
    valid: bool
    records: list[FastaRecord] = field(default_factory=list)
    global_errors: list[ValidationMessage] = field(default_factory=list)
    global_warnings: list[ValidationMessage] = field(default_factory=list)
    per_record_errors: dict[str, list[ValidationMessage]] = field(default_factory=dict)
    per_record_warnings: dict[str, list[ValidationMessage]] = field(default_factory=dict)
    sequence_summaries: list[SequenceValidationSummary] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationMessage]:
        messages = list(self.global_errors)
        for record_messages in self.per_record_errors.values():
            messages.extend(record_messages)
        return messages

    @property
    def warnings(self) -> list[ValidationMessage]:
        messages = list(self.global_warnings)
        for record_messages in self.per_record_warnings.values():
            messages.extend(record_messages)
        return messages

    def to_dict(self) -> dict[str, object]:
        return {
            "input_path": self.input_path,
            "valid": self.valid,
            "records": [_record_to_dict(record) for record in self.records],
            "global_errors": [message.to_dict() for message in self.global_errors],
            "global_warnings": [message.to_dict() for message in self.global_warnings],
            "per_record_errors": _message_map_to_dict(self.per_record_errors),
            "per_record_warnings": _message_map_to_dict(self.per_record_warnings),
            "errors": [message.to_dict() for message in self.errors],
            "warnings": [message.to_dict() for message in self.warnings],
            "sequence_summaries": [summary.to_dict() for summary in self.sequence_summaries],
            "record_count": len(self.records),
        }


def validate_fasta(
    path: str | Path,
    *,
    allow_n: bool = False,
    min_sequence_length: int = 20,
    high_n_percent_threshold: float = 10.0,
) -> ValidationReport:
    """Valida arquivo FASTA e separa erros de avisos."""

    fasta_path = Path(path)
    global_errors: list[ValidationMessage] = []
    global_warnings: list[ValidationMessage] = []
    per_record_errors: dict[str, list[ValidationMessage]] = {}
    per_record_warnings: dict[str, list[ValidationMessage]] = {}
    sequence_summaries: list[SequenceValidationSummary] = []

    if not fasta_path.exists():
        global_errors.append(ValidationMessage("error", "Arquivo nao existe."))
        return _build_report(fasta_path, [], global_errors, global_warnings, per_record_errors, per_record_warnings)

    if not fasta_path.is_file():
        global_errors.append(ValidationMessage("error", "Caminho informado nao e um arquivo."))
        return _build_report(fasta_path, [], global_errors, global_warnings, per_record_errors, per_record_warnings)

    if fasta_path.stat().st_size == 0:
        global_errors.append(ValidationMessage("error", "Arquivo FASTA esta vazio."))
        return _build_report(fasta_path, [], global_errors, global_warnings, per_record_errors, per_record_warnings)

    read_result = read_fasta(fasta_path)
    for parse_error in read_result.parse_errors:
        global_errors.append(ValidationMessage("error", parse_error))

    if not read_result.records:
        global_errors.append(ValidationMessage("error", "Nenhum registro FASTA foi encontrado."))

    allowed_bases = set("ACGTN" if allow_n else "ACGT")
    seen_ids: set[str] = set()

    for index, record in enumerate(read_result.records, start=1):
        record_valid = True
        record_key = _record_key(record, index)
        sequence_id = record.identifier

        if not sequence_id:
            _add_message(
                per_record_errors,
                record_key,
                ValidationMessage("error", "Cabecalho FASTA vazio ou sem identificador.", sequence_id),
            )
            record_valid = False
        elif sequence_id in seen_ids:
            _add_message(
                per_record_errors,
                record_key,
                ValidationMessage("error", "Identificador FASTA duplicado.", sequence_id),
            )
            record_valid = False
        if sequence_id:
            seen_ids.add(sequence_id)

        if not record.sequence:
            _add_message(
                per_record_errors,
                record_key,
                ValidationMessage("error", "Registro FASTA com sequencia vazia.", sequence_id),
            )
            record_valid = False

        invalid_chars = sorted({base for base in record.sequence if base not in allowed_bases})
        if invalid_chars:
            joined = ", ".join(_display_char(char) for char in invalid_chars)
            _add_message(
                per_record_errors,
                record_key,
                ValidationMessage(
                    "error",
                    f"Sequencia contem caracteres nao permitidos: {joined}.",
                    sequence_id,
                ),
            )
            record_valid = False

        if record.sequence and len(record.sequence) < min_sequence_length:
            _add_message(
                per_record_warnings,
                record_key,
                ValidationMessage(
                    "warning",
                    f"Sequencia curta: tamanho {len(record.sequence)} menor que {min_sequence_length}.",
                    sequence_id,
                ),
            )

        n_count = record.sequence.count("N")
        n_percent = round((n_count / len(record.sequence) * 100) if record.sequence else 0.0, 2)
        if n_count and allow_n:
            _add_message(
                per_record_warnings,
                record_key,
                ValidationMessage(
                    "warning",
                    f"Sequencia contem {n_count} base(s) N ({n_percent}%).",
                    sequence_id,
                ),
            )
            if n_percent >= high_n_percent_threshold:
                _add_message(
                    per_record_warnings,
                    record_key,
                    ValidationMessage(
                        "warning",
                        f"Proporcao alta de N: {n_percent}% (limite {high_n_percent_threshold}%).",
                        sequence_id,
                    ),
                )

        sequence_summaries.append(
            SequenceValidationSummary(
                sequence_id=sequence_id,
                length=len(record.sequence),
                n_count=n_count,
                n_percent=n_percent,
                valid=record_valid,
            )
        )

    valid = not global_errors and not any(per_record_errors.values())
    return ValidationReport(
        input_path=str(fasta_path),
        valid=valid,
        records=read_result.records,
        global_errors=global_errors,
        global_warnings=global_warnings,
        per_record_errors=per_record_errors,
        per_record_warnings=per_record_warnings,
        sequence_summaries=sequence_summaries,
    )


def _build_report(
    fasta_path: Path,
    records: list[FastaRecord],
    global_errors: list[ValidationMessage],
    global_warnings: list[ValidationMessage],
    per_record_errors: dict[str, list[ValidationMessage]],
    per_record_warnings: dict[str, list[ValidationMessage]],
) -> ValidationReport:
    return ValidationReport(
        input_path=str(fasta_path),
        valid=not global_errors and not any(per_record_errors.values()),
        records=records,
        global_errors=global_errors,
        global_warnings=global_warnings,
        per_record_errors=per_record_errors,
        per_record_warnings=per_record_warnings,
    )


def _add_message(
    target: dict[str, list[ValidationMessage]],
    record_key: str,
    message: ValidationMessage,
) -> None:
    target.setdefault(record_key, []).append(message)


def _record_key(record: FastaRecord, index: int) -> str:
    return record.identifier or f"record_{index}"


def _record_to_dict(record: FastaRecord) -> dict[str, str]:
    return {
        "identifier": record.identifier,
        "description": record.description,
        "sequence": record.sequence,
    }


def _message_map_to_dict(
    messages: dict[str, list[ValidationMessage]],
) -> dict[str, list[dict[str, str]]]:
    return {key: [message.to_dict() for message in value] for key, value in messages.items()}


def _display_char(char: str) -> str:
    if char == " ":
        return "<espaco>"
    if char == "\t":
        return "<tab>"
    return char
