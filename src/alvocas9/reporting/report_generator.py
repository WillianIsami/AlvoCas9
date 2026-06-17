from __future__ import annotations

import csv
import html
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from alvocas9.config import PipelineConfig
from alvocas9.core.scanner import ScanStats
from alvocas9.validation.dna_validator import ValidationReport
from alvocas9.visualization.plots import create_plots


REPORT_TITLE = "Relatório técnico de triagem in silico CRISPR-Cas9"
PROJECT_NAME = "AlvoCas9"
LIMITATION_TEXT = (
    "Os resultados apresentados representam uma triagem computacional inicial baseada em "
    "padrões de sequência. Os candidatos identificados não constituem recomendação "
    "experimental, clínica ou terapêutica. A seleção real de guias CRISPR-Cas9 exige "
    "análises adicionais, incluindo avaliação de off-target em genoma de referência, "
    "contexto biológico, validação experimental e revisão especializada."
)

FORBIDDEN_REPORT_TERMS = [
    "guia recomendado",
    "alvo seguro",
    "aplicação clínica",
    "eficiência garantida",
]

CANDIDATE_COLUMNS = [
    "sequence_id",
    "strand",
    "protospacer_sequence_5to3",
    "pam_sequence_5to3",
    "protospacer_start_1based",
    "protospacer_end_1based",
    "pam_start_1based",
    "pam_end_1based",
    "full_candidate_start_1based",
    "full_candidate_end_1based",
    "target_length",
    "pam_pattern",
    "gc_percent",
    "n_count",
    "has_n",
    "max_homopolymer_run",
    "duplicate_exact_count_within_input",
    "warnings",
    "heuristic_score",
    "filter_status",
]


def write_pipeline_outputs(
    *,
    config: PipelineConfig,
    validation: ValidationReport,
    sequence_summary: list[dict[str, object]],
    candidates: list[dict[str, object]],
    stats_by_sequence: dict[str, ScanStats],
) -> list[str]:
    """Escreve tabelas, JSON, graficos e relatorios."""

    output_dir = config.output_dir
    tables_dir = output_dir / "tables"
    json_dir = output_dir / "json"
    figures_dir = output_dir / "figures"
    reports_dir = output_dir / "reports"
    logs_dir = output_dir / "logs"
    for directory in (tables_dir, json_dir, figures_dir, reports_dir, logs_dir):
        directory.mkdir(parents=True, exist_ok=True)

    serializable_candidates = _serializable_candidates(candidates)
    generated_files = _expected_generated_files()

    _write_csv(tables_dir / "sequences_summary.csv", sequence_summary)
    _write_csv(tables_dir / "candidates.csv", serializable_candidates, CANDIDATE_COLUMNS)
    _write_csv(tables_dir / "validation_summary.csv", _validation_rows(validation))

    _write_json(json_dir / "validation.json", validation.to_dict())
    _write_json(json_dir / "candidates.json", serializable_candidates)
    _write_json(json_dir / "run_config.json", config.to_dict())

    create_plots(candidates, figures_dir)

    context = _build_report_context(
        config=config,
        validation=validation,
        sequence_summary=sequence_summary,
        candidates=serializable_candidates,
        stats_by_sequence=stats_by_sequence,
        generated_files=generated_files,
    )
    markdown = _render_template(_template_path("technical_report.md.j2"), context)
    rendered_html = _render_template(_template_path("technical_report.html.j2"), context)
    _assert_report_language(markdown)
    _assert_report_language(rendered_html)
    (reports_dir / "technical_report.md").write_text(markdown, encoding="utf-8")
    (reports_dir / "technical_report.html").write_text(rendered_html, encoding="utf-8")
    return generated_files


def write_validation_failure_outputs(
    *,
    config: PipelineConfig,
    validation: ValidationReport,
) -> list[str]:
    """Escreve artefatos mínimos quando erros críticos impedem a análise."""

    json_dir = config.output_dir / "json"
    json_dir.mkdir(parents=True, exist_ok=True)
    _write_json(json_dir / "validation.json", validation.to_dict())
    _write_json(json_dir / "run_config.json", config.to_dict())
    return ["json/validation.json", "json/run_config.json", "logs/pipeline.log"]


def _build_report_context(
    *,
    config: PipelineConfig,
    validation: ValidationReport,
    sequence_summary: list[dict[str, object]],
    candidates: list[dict[str, object]],
    stats_by_sequence: dict[str, ScanStats],
    generated_files: list[str],
) -> dict[str, str]:
    generated_at = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S %Z")
    validation_rows = _validation_rows(validation)
    sequence_rows = _sequence_report_rows(sequence_summary, validation)
    candidate_summary = _candidate_summary_rows(candidates)
    stats_rows = [
        {"sequence_id": sequence_id, **stats.to_dict()}
        for sequence_id, stats in stats_by_sequence.items()
    ]

    markdown_values = {
        "title": REPORT_TITLE,
        "project_name": PROJECT_NAME,
        "generated_at": generated_at,
        "input_path": str(config.input_path),
        "config_table": _markdown_table(_config_rows(config)),
        "sequence_summary_table": _markdown_table(sequence_rows),
        "validation_error_count": str(len(validation.errors)),
        "validation_warning_count": str(len(validation.warnings)),
        "validation_messages_table": _markdown_table(validation_rows),
        "candidate_total": str(len(candidates)),
        "candidates_per_sequence_table": _markdown_table(_counter_rows(Counter(str(row["sequence_id"]) for row in candidates), "sequence_id")),
        "candidates_by_strand_table": _markdown_table(_counter_rows(Counter(str(row["strand"]) for row in candidates), "strand")),
        "filter_status_table": _markdown_table(_counter_rows(Counter(str(row["filter_status"]) for row in candidates), "filter_status")),
        "pam_stats_table": _markdown_table(stats_rows),
        "candidate_summary_table": _markdown_table(candidate_summary),
        "candidates_table": _markdown_table(candidates),
        "generated_files_list": "\n".join(f"- `{item}`" for item in generated_files),
        "limitation_text": LIMITATION_TEXT,
    }

    html_values = {
        key: html.escape(value)
        for key, value in {
            "title": REPORT_TITLE,
            "project_name": PROJECT_NAME,
            "generated_at": generated_at,
            "input_path": str(config.input_path),
            "validation_error_count": str(len(validation.errors)),
            "validation_warning_count": str(len(validation.warnings)),
            "candidate_total": str(len(candidates)),
            "limitation_text": LIMITATION_TEXT,
        }.items()
    }
    html_values.update(
        {
            "config_table": _html_table(_config_rows(config)),
            "sequence_summary_table": _html_table(sequence_rows),
            "validation_messages_table": _html_table(validation_rows),
            "candidates_per_sequence_table": _html_table(_counter_rows(Counter(str(row["sequence_id"]) for row in candidates), "sequence_id")),
            "candidates_by_strand_table": _html_table(_counter_rows(Counter(str(row["strand"]) for row in candidates), "strand")),
            "filter_status_table": _html_table(_counter_rows(Counter(str(row["filter_status"]) for row in candidates), "filter_status")),
            "pam_stats_table": _html_table(stats_rows),
            "candidate_summary_table": _html_table(candidate_summary),
            "candidates_table": _html_table(candidates),
            "generated_files_list": "\n".join(f"<li><code>{html.escape(item)}</code></li>" for item in generated_files),
        }
    )

    context: dict[str, str] = {}
    for key, value in markdown_values.items():
        context[f"md_{key}"] = value
    for key, value in html_values.items():
        context[f"html_{key}"] = value
    context.update(markdown_values)
    return context


def _config_rows(config: PipelineConfig) -> list[dict[str, object]]:
    return [
        {"configuracao": "PAM", "valor": config.pam},
        {"configuracao": "target length", "valor": config.target_length},
        {"configuracao": "min GC", "valor": config.min_gc},
        {"configuracao": "max GC", "valor": config.max_gc},
        {"configuracao": "max homopolymer", "valor": config.max_homopolymer},
        {"configuracao": "allow N", "valor": config.allow_n},
    ]


def _sequence_report_rows(
    sequence_summary: list[dict[str, object]],
    validation: ValidationReport,
) -> list[dict[str, object]]:
    status_by_id = {
        summary.sequence_id: "válida" if summary.valid else "inválida"
        for summary in validation.sequence_summaries
    }
    return [
        {
            "ID": row.get("sequence_id", ""),
            "tamanho": row.get("length", ""),
            "GC%": row.get("gc_percent", ""),
            "número de N": row.get("n_count", ""),
            "status de validação": status_by_id.get(str(row.get("sequence_id", "")), "válida" if validation.valid else "não avaliada"),
        }
        for row in sequence_summary
    ]


def _candidate_summary_rows(candidates: list[dict[str, object]]) -> list[dict[str, object]]:
    if not candidates:
        return []
    return [
        {
            "métrica": "total de candidatos",
            "valor": len(candidates),
        },
        {
            "métrica": "sequências com candidatos",
            "valor": len({str(row["sequence_id"]) for row in candidates}),
        },
        {
            "métrica": "candidatos na fita +",
            "valor": sum(1 for row in candidates if row.get("strand") == "+"),
        },
        {
            "métrica": "candidatos na fita -",
            "valor": sum(1 for row in candidates if row.get("strand") == "-"),
        },
    ]


def _counter_rows(counter: Counter[str], label: str) -> list[dict[str, object]]:
    return [{label: key, "quantidade": value} for key, value in sorted(counter.items())]


def _serializable_candidates(candidates: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for candidate in candidates:
        row = dict(candidate)
        warnings = row.get("warnings", [])
        if isinstance(warnings, list):
            row["warnings"] = "; ".join(str(item) for item in warnings)
        rows.append(row)
    return rows


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def _write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _validation_rows(validation: ValidationReport) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for message in validation.errors + validation.warnings:
        rows.append(message.to_dict())
    if not rows:
        rows.append({"level": "info", "sequence_id": "", "message": "Validação concluída sem erros."})
    return rows


def _expected_generated_files() -> list[str]:
    return [
        "tables/sequences_summary.csv",
        "tables/candidates.csv",
        "tables/validation_summary.csv",
        "json/validation.json",
        "json/candidates.json",
        "json/run_config.json",
        "figures/candidates_per_sequence.png",
        "figures/gc_distribution_candidates.png",
        "figures/filter_status_summary.png",
        "reports/technical_report.html",
        "reports/technical_report.md",
        "logs/pipeline.log",
    ]


def _template_path(filename: str) -> Path:
    return Path(__file__).resolve().parent / "templates" / filename


def _render_template(template_path: Path, values: dict[str, str]) -> str:
    rendered = template_path.read_text(encoding="utf-8")
    for key, value in values.items():
        rendered = rendered.replace("{{ " + key + " }}", value)
    return rendered


def _markdown_table(rows: list[dict[str, object]]) -> str:
    if not rows:
        return "_Sem registros._"
    columns = list(rows[0].keys())
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| " + " | ".join(_markdown_cell(row.get(column, "")) for column in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, separator, *body])


def _markdown_cell(value: object) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def _html_table(rows: object) -> str:
    if not isinstance(rows, list) or not rows:
        return "<p><em>Sem registros.</em></p>"
    columns = list(rows[0].keys())
    parts = ["<table><thead><tr>"]
    parts.extend(f"<th>{html.escape(str(column))}</th>" for column in columns)
    parts.append("</tr></thead><tbody>")
    for row in rows:
        parts.append("<tr>")
        parts.extend(f"<td>{html.escape(str(row.get(column, '')))}</td>" for column in columns)
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def _assert_report_language(text: str) -> None:
    lowered = text.lower()
    forbidden = [term for term in FORBIDDEN_REPORT_TERMS if term in lowered]
    if forbidden:
        raise ValueError(f"Relatorio contem termo proibido: {', '.join(forbidden)}")
