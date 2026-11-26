from __future__ import annotations

import csv
import hashlib
import html
import json
import platform
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from alvocas9 import __version__
from alvocas9.config import PipelineConfig
from alvocas9.core.scanner import ScanStats
from alvocas9.validation.dna_validator import ValidationReport
from alvocas9.visualization.plots import create_plots


REPORT_TITLE = "Relatório técnico de triagem in silico CRISPR-Cas9"
PROJECT_NAME = "AlvoCas9"
REPORT_TIMEZONE = "America/Sao_Paulo"

# Numero maximo de candidatos exibidos na tabela do relatorio. As tabelas CSV e
# JSON continuam completas. Sem este limite, uma entrada de 50 kb gera um
# relatorio HTML de quase 2 MB, com mais de seis mil linhas de tabela, que
# nenhum navegador apresenta de forma util.
REPORT_MAX_CANDIDATE_ROWS = 50

# O formato BED usa score inteiro de 0 a 1000, enquanto o score heuristico do
# projeto vai de 0 a 100.
BED_SCORE_MAX = 1000
LIMITATION_TEXT = (
    "Os resultados apresentados representam uma triagem computacional inicial baseada em "
    "padrões de sequência. Os candidatos identificados não constituem recomendação "
    "experimental, clínica ou terapêutica. A seleção real de guias CRISPR-Cas9 exige "
    "análises adicionais, incluindo avaliação de off-target em genoma de referência, "
    "contexto biológico, validação experimental e revisão especializada."
)

# Frases afirmativas que o relatorio nunca deve conter. A verificacao e por
# frase, e nao por palavra isolada, porque o texto obrigatorio de limitacao usa
# as palavras "clinica" e "terapeutica" justamente para negar essas aplicacoes.
FORBIDDEN_REPORT_TERMS = [
    "guia recomendado",
    "guia validado",
    "alvo seguro",
    "alvo recomendado",
    "aplicação clínica",
    "uso terapêutico",
    "eficiência garantida",
    "pronto para uso experimental",
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
    "cut_site_1based",
    "full_candidate_start_1based",
    "full_candidate_end_1based",
    "relative_position_percent",
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
    """Escreve tabelas, JSON, graficos e relatorios.

    Devolve a lista dos arquivos **efetivamente gravados**, conferida em disco.
    Antes esta funcao devolvia uma lista fixa do que deveria existir, de modo
    que o log afirmava ter gerado arquivos sem verificar nenhum, o que
    contradizia a rastreabilidade que o projeto defende.
    """

    output_dir = config.output_dir
    tables_dir = output_dir / "tables"
    json_dir = output_dir / "json"
    figures_dir = output_dir / "figures"
    reports_dir = output_dir / "reports"
    logs_dir = output_dir / "logs"
    for directory in (tables_dir, json_dir, figures_dir, reports_dir, logs_dir):
        directory.mkdir(parents=True, exist_ok=True)

    serializable_candidates = _serializable_candidates(candidates)
    escritos: list[Path] = [
        _write_csv(tables_dir / "sequences_summary.csv", sequence_summary),
        _write_csv(tables_dir / "candidates.csv", serializable_candidates, CANDIDATE_COLUMNS),
        _write_csv(tables_dir / "validation_summary.csv", _validation_rows(validation)),
        _write_bed(tables_dir / "candidates.bed", serializable_candidates),
        _write_json(json_dir / "validation.json", validation.to_dict()),
        _write_json(json_dir / "candidates.json", serializable_candidates),
        _write_json(json_dir / "run_config.json", _run_config_payload(config)),
    ]
    escritos.extend(create_plots(candidates, figures_dir))

    report_html = reports_dir / "technical_report.html"
    report_md = reports_dir / "technical_report.md"
    log_file = logs_dir / "pipeline.log"

    # Os relatorios precisam listar a si mesmos, entao entram na lista antes de
    # serem gravados. A conferencia em disco acontece no final.
    previstos = escritos + [report_html, report_md]
    if log_file.exists():
        previstos.append(log_file)

    context = _build_report_context(
        config=config,
        validation=validation,
        sequence_summary=sequence_summary,
        candidates=serializable_candidates,
        stats_by_sequence=stats_by_sequence,
        generated_files=[_caminho_relativo(path, output_dir) for path in previstos],
    )
    markdown = _render_template(_template_path("technical_report.md.j2"), context)
    rendered_html = _render_template(_template_path("technical_report.html.j2"), context)
    _assert_report_language(markdown)
    _assert_report_language(rendered_html)
    report_md.write_text(markdown, encoding="utf-8")
    report_html.write_text(rendered_html, encoding="utf-8")

    return [
        _caminho_relativo(path, output_dir) for path in previstos if path.is_file()
    ]


def write_validation_failure_outputs(
    *,
    config: PipelineConfig,
    validation: ValidationReport,
) -> list[str]:
    """Escreve artefatos mínimos quando erros críticos impedem a análise.

    Como em ``write_pipeline_outputs``, a lista devolvida é conferida em disco,
    e não fixa no código.
    """

    output_dir = config.output_dir
    json_dir = output_dir / "json"
    json_dir.mkdir(parents=True, exist_ok=True)
    previstos = [
        _write_json(json_dir / "validation.json", validation.to_dict()),
        _write_json(json_dir / "run_config.json", _run_config_payload(config)),
        output_dir / "logs" / "pipeline.log",
    ]
    return [_caminho_relativo(path, output_dir) for path in previstos if path.is_file()]


def _run_config_payload(config: PipelineConfig) -> dict[str, object]:
    """Monta o conteudo do ``run_config.json``.

    Alem dos parametros da execucao, registra o que e preciso para repeti-la
    com seguranca: a versao do AlvoCas9, a versao do Python, a data e hora, e o
    hash SHA-256 do arquivo de entrada.

    Sem esses campos, dois ``run_config.json`` identicos podiam corresponder a
    execucoes diferentes, sobre arquivos diferentes ou versoes diferentes do
    software, o que esvaziava a reprodutibilidade que o projeto defende.

    O campo ``executed_at`` muda a cada execucao, por definicao. E o unico
    campo de saida que nao e deterministico, junto com o carimbo do relatorio.
    """

    payload = config.to_dict()
    payload["alvocas9_version"] = __version__
    payload["python_version"] = platform.python_version()
    payload["executed_at"] = _format_generated_at()
    payload["input_sha256"] = _sha256_do_arquivo(config.input_path)
    return payload


def _sha256_do_arquivo(path: Path) -> str | None:
    """SHA-256 do arquivo, ou ``None`` quando ele nao pode ser lido.

    Devolver ``None`` em vez de falhar mantem o registro possivel mesmo quando
    a entrada desapareceu entre a leitura e a escrita das saidas.
    """

    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return None


def _format_generated_at(timezone_key: str = REPORT_TIMEZONE) -> str:
    """Formata a data e hora da execucao do relatorio.

    Usa o fuso brasileiro quando a base de fusos IANA esta disponivel. Em
    sistemas sem essa base, como o Windows sem o pacote ``tzdata``, usa o fuso
    local e registra o deslocamento numerico. Assim, a ausencia de uma
    dependencia opcional nao interrompe a geracao dos relatorios depois de o
    pipeline ja ter gravado tabelas, JSON e graficos.
    """

    try:
        return datetime.now(ZoneInfo(timezone_key)).strftime("%Y-%m-%d %H:%M:%S %Z")
    except (ZoneInfoNotFoundError, ValueError, OSError):
        return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")


def _build_report_context(
    *,
    config: PipelineConfig,
    validation: ValidationReport,
    sequence_summary: list[dict[str, object]],
    candidates: list[dict[str, object]],
    stats_by_sequence: dict[str, ScanStats],
    generated_files: list[str],
) -> dict[str, str]:
    generated_at = _format_generated_at()
    visible_candidates = candidates[:REPORT_MAX_CANDIDATE_ROWS]
    candidates_table_note = _candidates_table_note(len(candidates), len(visible_candidates))
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
        "candidates_table": _markdown_table(visible_candidates),
        "candidates_table_note": candidates_table_note,
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
            "candidates_table": _html_table(visible_candidates),
            "candidates_table_note": (
                f"<p>{html.escape(candidates_table_note)}</p>" if candidates_table_note else ""
            ),
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
        {"configuracao": "posição do PAM", "valor": f"{config.pam_position} (a 3' do protospacer)"},
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


def _candidates_table_note(total: int, exibidos: int) -> str:
    """Texto que avisa que a tabela do relatorio foi truncada."""

    if total <= exibidos:
        return ""
    return (
        f"A tabela mostra os {exibidos} candidatos de maior score heuristico, "
        f"de um total de {total}. A listagem completa está em "
        "tables/candidates.csv e em json/candidates.json."
    )


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


def _write_bed(path: Path, candidates: list[dict[str, object]]) -> Path:
    """Escreve os candidatos em BED, convertendo o sistema de coordenadas.

    O projeto usa coordenadas **1-based inclusivas** e o BED usa **0-based
    semiabertas**. A conversao e:

        inicio_bed = inicio_1based - 1
        fim_bed    = fim_1based

    O fim nao muda de valor porque o limite semiaberto do BED coincide
    numericamente com o limite inclusivo 1-based: um intervalo que vai da base
    1 a base 23 em 1-based inclusivo e [0, 23) em 0-based semiaberto.

    O arquivo tem seis colunas, sem cabecalho, separadas por tabulacao, e pode
    ser carregado em navegadores genomicos. A ordem das linhas acompanha a do
    ``candidates.csv``, ou seja, por score decrescente.
    """

    linhas: list[str] = []
    for indice, candidato in enumerate(candidates, start=1):
        inicio_1based = int(candidato["full_candidate_start_1based"])
        fim_1based = int(candidato["full_candidate_end_1based"])
        score = min(int(candidato["heuristic_score"]) * 10, BED_SCORE_MAX)
        linhas.append(
            "\t".join(
                [
                    str(candidato["sequence_id"]),
                    str(inicio_1based - 1),
                    str(fim_1based),
                    f"{candidato['sequence_id']}_cand{indice:04d}",
                    str(score),
                    str(candidato["strand"]),
                ]
            )
        )

    path.write_text("\n".join(linhas) + ("\n" if linhas else ""), encoding="utf-8")
    return path


def _caminho_relativo(path: Path, output_dir: Path) -> str:
    """Caminho do arquivo relativo ao diretorio de saida, com barras normais."""

    return path.relative_to(output_dir).as_posix()


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> Path:
    if fieldnames is None:
        fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    return path


def _write_json(path: Path, data: object) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _validation_rows(validation: ValidationReport) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for message in validation.errors + validation.warnings:
        rows.append(message.to_dict())
    if not rows:
        rows.append({"level": "info", "sequence_id": "", "message": "Validação concluída sem erros."})
    return rows


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
    if value is None:
        return ""
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
        parts.extend(
            f"<td>{html.escape('' if row.get(column) is None else str(row.get(column)))}</td>"
            for column in columns
        )
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def _assert_report_language(text: str) -> None:
    lowered = text.lower()
    forbidden = [term for term in FORBIDDEN_REPORT_TERMS if term in lowered]
    if forbidden:
        raise ValueError(f"Relatorio contem termo proibido: {', '.join(forbidden)}")
