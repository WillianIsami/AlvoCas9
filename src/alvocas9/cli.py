from __future__ import annotations

import argparse
import sys
from pathlib import Path

from alvocas9.analysis.features import add_candidate_features, build_sequence_summary
from alvocas9.analysis.filters import apply_filters
from alvocas9.config import PipelineConfig
from alvocas9.core.pam import validate_pam_pattern
from alvocas9.core.scanner import scan_records
from alvocas9.reporting.report_generator import (
    write_pipeline_outputs,
    write_validation_failure_outputs,
)
from alvocas9.utils.logging_utils import configure_logging
from alvocas9.validation.dna_validator import validate_fasta


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="alvocas9",
        description="Pipeline in silico educacional para triagem inicial de candidatos CRISPR-Cas9.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validar arquivo FASTA.")
    validate_parser.add_argument("--input", required=True, type=Path, help="Arquivo FASTA de entrada.")
    validate_parser.add_argument("--allow-n", action="store_true", help="Aceitar N como base desconhecida.")
    validate_parser.add_argument("--min-sequence-length", type=int, default=20)

    analyze_parser = subparsers.add_parser("analyze", help="Executar pipeline completo.")
    analyze_parser.add_argument("--input", required=True, type=Path, help="Arquivo FASTA de entrada.")
    analyze_parser.add_argument("--output", required=True, type=Path, help="Diretorio de resultados.")
    analyze_parser.add_argument("--pam", default="NGG", help="Padrao PAM em IUPAC. Padrao: NGG.")
    analyze_parser.add_argument("--target-length", type=int, default=20)
    analyze_parser.add_argument("--min-gc", type=float, default=40.0)
    analyze_parser.add_argument("--max-gc", type=float, default=60.0)
    analyze_parser.add_argument("--max-homopolymer", type=int, default=4)
    analyze_parser.add_argument("--allow-n", action="store_true", help="Aceitar N como base desconhecida.")
    analyze_parser.add_argument("--min-sequence-length", type=int, default=20)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        report = validate_fasta(
            args.input,
            allow_n=args.allow_n,
            min_sequence_length=args.min_sequence_length,
        )
        _print_validation(report)
        return 0 if report.valid else 1

    if args.command == "analyze":
        try:
            validate_pam_pattern(args.pam)
            config = PipelineConfig(
                input_path=args.input,
                output_dir=args.output,
                pam=args.pam.upper(),
                target_length=args.target_length,
                min_gc=args.min_gc,
                max_gc=args.max_gc,
                max_homopolymer=args.max_homopolymer,
                allow_n=args.allow_n,
                min_sequence_length=args.min_sequence_length,
            )
            run_pipeline(config)
        except Exception as exc:  # pragma: no cover - CLI defensive path
            print(f"Erro: {exc}", file=sys.stderr)
            return 1
        return 0

    parser.print_help()
    return 1


def run_pipeline(config: PipelineConfig) -> None:
    logs_dir = config.output_dir / "logs"
    logger = configure_logging(logs_dir / "pipeline.log")
    logger.info("Inicio da execucao do AlvoCas9.")
    logger.info("Arquivo de entrada: %s", config.input_path)
    logger.info("Diretorio de saida: %s", config.output_dir)

    validation = validate_fasta(
        config.input_path,
        allow_n=config.allow_n,
        min_sequence_length=config.min_sequence_length,
    )
    sequence_summary = build_sequence_summary(validation.records)
    logger.info("Numero de sequencias lidas: %s", len(validation.records))
    logger.info(
        "Validacao FASTA: %s erro(s), %s aviso(s).",
        len(validation.errors),
        len(validation.warnings),
    )

    if not validation.valid:
        logger.error("Validacao critica falhou. A analise foi encerrada antes da busca de PAM.")
        for error in validation.errors:
            prefix = f"[{error.sequence_id}] " if error.sequence_id else ""
            logger.error("%s%s", prefix, error.message)
        generated_files = write_validation_failure_outputs(config=config, validation=validation)
        logger.info("Arquivos gerados: %s", ", ".join(generated_files))
        logger.info("Fim da execucao com erro de validacao.")
        validation_path = config.output_dir / "json" / "validation.json"
        log_path = config.output_dir / "logs" / "pipeline.log"
        raise ValueError(
            f"FASTA invalido. Consulte {validation_path} e {log_path}."
        )

    if validation.warnings:
        for warning in validation.warnings:
            prefix = f"[{warning.sequence_id}] " if warning.sequence_id else ""
            logger.warning("%s%s", prefix, warning.message)

    scan_result = scan_records(validation.records, config)
    candidates = add_candidate_features(scan_result.candidates)
    candidates = apply_filters(candidates, config)
    generated_files = write_pipeline_outputs(
        config=config,
        validation=validation,
        sequence_summary=sequence_summary,
        candidates=candidates,
        stats_by_sequence=scan_result.stats_by_sequence,
    )
    logger.info("PAMs encontrados: %s", sum(stats.pams_found_total for stats in scan_result.stats_by_sequence.values()))
    logger.info("Candidatos extraidos: %s", len(candidates))
    logger.info("Arquivos gerados: %s", ", ".join(generated_files))
    logger.info("Fim da execucao.")


def _print_validation(report) -> None:
    print(f"Arquivo: {report.input_path}")
    print(f"Valido: {report.valid}")
    print(f"Registros: {len(report.records)}")
    print(f"Erros: {len(report.errors)}")
    for error in report.errors:
        prefix = f"[{error.sequence_id}] " if error.sequence_id else ""
        print(f"ERRO: {prefix}{error.message}")
    print(f"Avisos: {len(report.warnings)}")
    for warning in report.warnings:
        prefix = f"[{warning.sequence_id}] " if warning.sequence_id else ""
        print(f"AVISO: {prefix}{warning.message}")
