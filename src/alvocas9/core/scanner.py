from __future__ import annotations

from dataclasses import dataclass, field

from alvocas9.config import PipelineConfig
from alvocas9.core.pam import find_pam_positions, validate_pam_pattern
from alvocas9.core.sequence_utils import reverse_complement
from alvocas9.io.fasta_reader import FastaRecord


CAS9_CUT_OFFSET_FROM_PAM = 3
"""Distancia, em pares de base, entre o sitio de corte e o PAM.

Para a SpCas9, o corte de dupla-fita ocorre cerca de 3 pb a 5' do PAM, ou seja,
entre as posicoes 17 e 18 de um protospacer de 20 nucleotideos. Este valor e
uma premissa do modelo, valida para sistemas com PAM a 3' do protospacer, e nao
uma medicao feita pelo pipeline.
"""


@dataclass(frozen=True, slots=True)
class ScanConfig:
    pam_pattern: str = "NGG"
    target_length: int = 20

    @classmethod
    def from_pipeline_config(cls, config: PipelineConfig) -> "ScanConfig":
        return cls(pam_pattern=config.pam, target_length=config.target_length)


@dataclass(frozen=True, slots=True)
class PamHit:
    sequence_id: str
    strand: str
    pam_sequence_5to3: str
    pam_start_0based: int
    pam_end_0based: int
    pam_start_1based: int
    pam_end_1based: int
    pam_pattern: str


@dataclass(frozen=True, slots=True)
class Candidate:
    sequence_id: str
    strand: str
    protospacer_sequence_5to3: str
    pam_sequence_5to3: str
    protospacer_start_1based: int
    protospacer_end_1based: int
    pam_start_1based: int
    pam_end_1based: int
    cut_site_1based: int | None
    full_candidate_start_1based: int
    full_candidate_end_1based: int
    relative_position_percent: float
    target_length: int
    pam_pattern: str

    def to_dict(self) -> dict[str, object]:
        """Converte o candidato em dicionario, campo a campo.

        Escrito manualmente em vez de usar ``dataclasses.asdict`` porque
        ``asdict`` faz copia recursiva de cada campo. Com dezenas de milhares
        de candidatos, a diferenca e mensuravel: em uma entrada de 50 kb, a
        conversao respondia por mais tempo do que a propria busca de PAM.
        """

        return {
            "sequence_id": self.sequence_id,
            "strand": self.strand,
            "protospacer_sequence_5to3": self.protospacer_sequence_5to3,
            "pam_sequence_5to3": self.pam_sequence_5to3,
            "protospacer_start_1based": self.protospacer_start_1based,
            "protospacer_end_1based": self.protospacer_end_1based,
            "pam_start_1based": self.pam_start_1based,
            "pam_end_1based": self.pam_end_1based,
            "cut_site_1based": self.cut_site_1based,
            "full_candidate_start_1based": self.full_candidate_start_1based,
            "full_candidate_end_1based": self.full_candidate_end_1based,
            "relative_position_percent": self.relative_position_percent,
            "target_length": self.target_length,
            "pam_pattern": self.pam_pattern,
        }


@dataclass(slots=True)
class ScanStats:
    pams_found_plus: int = 0
    pams_found_minus: int = 0
    pams_skipped_insufficient_upstream_plus: int = 0
    pams_skipped_insufficient_upstream_minus: int = 0

    @property
    def pams_found_total(self) -> int:
        return self.pams_found_plus + self.pams_found_minus

    @property
    def pams_skipped_insufficient_upstream_total(self) -> int:
        return (
            self.pams_skipped_insufficient_upstream_plus
            + self.pams_skipped_insufficient_upstream_minus
        )

    def to_dict(self) -> dict[str, int]:
        return {
            "pams_found_plus": self.pams_found_plus,
            "pams_found_minus": self.pams_found_minus,
            "pams_found_total": self.pams_found_total,
            "pams_skipped_insufficient_upstream_plus": self.pams_skipped_insufficient_upstream_plus,
            "pams_skipped_insufficient_upstream_minus": self.pams_skipped_insufficient_upstream_minus,
            "pams_skipped_insufficient_upstream_total": self.pams_skipped_insufficient_upstream_total,
        }


@dataclass(slots=True)
class ScanResult:
    candidates: list[dict[str, object]] = field(default_factory=list)
    stats_by_sequence: dict[str, ScanStats] = field(default_factory=dict)


def scan_sequence_for_pam(
    sequence: str,
    *,
    sequence_id: str,
    strand: str = "+",
    config: ScanConfig | None = None,
    original_length: int | None = None,
) -> list[PamHit]:
    """Busca PAMs em uma sequencia ja orientada 5'->3'."""

    scan_config = config or ScanConfig()
    pam_pattern = validate_pam_pattern(scan_config.pam_pattern)
    if strand not in {"+", "-"}:
        raise ValueError("strand deve ser '+' ou '-'.")

    oriented_sequence = sequence.upper()
    length_for_mapping = original_length if original_length is not None else len(oriented_sequence)
    pam_length = len(pam_pattern)
    hits: list[PamHit] = []

    for pam_start in find_pam_positions(oriented_sequence, pam_pattern):
        pam_end = pam_start + pam_length
        if strand == "+":
            pam_start_1, pam_end_1 = pam_start + 1, pam_end
        else:
            pam_start_1, pam_end_1 = _map_rc_interval_to_original(
                pam_start,
                pam_end,
                length_for_mapping,
            )

        hits.append(
            PamHit(
                sequence_id=sequence_id,
                strand=strand,
                pam_sequence_5to3=oriented_sequence[pam_start:pam_end],
                pam_start_0based=pam_start,
                pam_end_0based=pam_end,
                pam_start_1based=pam_start_1,
                pam_end_1based=pam_end_1,
                pam_pattern=pam_pattern,
            )
        )

    return hits


def extract_candidates_from_both_strands(
    sequence_id: str,
    sequence: str,
    config: ScanConfig | None = None,
) -> list[Candidate]:
    """Extrai candidatos nas fitas direta e reversa complementar.

    API auxiliar, usada pelos testes para inspecionar os candidatos como
    objetos ``Candidate``. O pipeline usa ``scan_records``.
    """

    candidates, _stats = _extract_candidates_with_stats(sequence_id, sequence, config or ScanConfig())
    return candidates


def scan_records(records: list[FastaRecord], config: PipelineConfig) -> ScanResult:
    """Varre todos os registros nas fitas direta e reversa complementar.

    Esta e a funcao usada pelo pipeline, chamada por ``cli.run_pipeline``.
    """

    scan_config = ScanConfig.from_pipeline_config(config)
    result = ScanResult()
    for record in records:
        candidates, stats = _extract_candidates_with_stats(
            record.sequence_id,
            record.sequence,
            scan_config,
        )
        result.candidates.extend(candidate.to_dict() for candidate in candidates)
        result.stats_by_sequence[record.sequence_id] = stats
    return result


def scan_record(record: FastaRecord, config: PipelineConfig) -> tuple[list[dict[str, object]], ScanStats]:
    """Varre um unico registro FASTA e devolve candidatos e estatisticas.

    API auxiliar, usada pelos testes de coordenadas para isolar uma sequencia.
    O pipeline usa ``scan_records``, que percorre todos os registros.
    """

    candidates, stats = _extract_candidates_with_stats(
        record.sequence_id,
        record.sequence,
        ScanConfig.from_pipeline_config(config),
    )
    return [candidate.to_dict() for candidate in candidates], stats


def _extract_candidates_with_stats(
    sequence_id: str,
    sequence: str,
    config: ScanConfig,
) -> tuple[list[Candidate], ScanStats]:
    pam_pattern = validate_pam_pattern(config.pam_pattern)
    scan_config = ScanConfig(pam_pattern=pam_pattern, target_length=config.target_length)
    original_sequence = sequence.upper()
    reverse_sequence = reverse_complement(original_sequence)
    original_length = len(original_sequence)
    stats = ScanStats()
    candidates: list[Candidate] = []

    plus_hits = scan_sequence_for_pam(
        original_sequence,
        sequence_id=sequence_id,
        strand="+",
        config=scan_config,
    )
    stats.pams_found_plus = len(plus_hits)
    for hit in plus_hits:
        candidate = _candidate_from_hit(hit, original_sequence, original_length, scan_config)
        if candidate is None:
            stats.pams_skipped_insufficient_upstream_plus += 1
        else:
            candidates.append(candidate)

    minus_hits = scan_sequence_for_pam(
        reverse_sequence,
        sequence_id=sequence_id,
        strand="-",
        config=scan_config,
        original_length=original_length,
    )
    stats.pams_found_minus = len(minus_hits)
    for hit in minus_hits:
        candidate = _candidate_from_hit(hit, reverse_sequence, original_length, scan_config)
        if candidate is None:
            stats.pams_skipped_insufficient_upstream_minus += 1
        else:
            candidates.append(candidate)

    return candidates, stats


def _candidate_from_hit(
    hit: PamHit,
    oriented_sequence: str,
    original_length: int,
    config: ScanConfig,
) -> Candidate | None:
    if hit.pam_start_0based < config.target_length:
        return None

    protospacer_start = hit.pam_start_0based - config.target_length
    protospacer_end = hit.pam_start_0based
    protospacer_sequence = oriented_sequence[protospacer_start:protospacer_end]

    if hit.strand == "+":
        prot_start_1, prot_end_1 = protospacer_start + 1, protospacer_end
        pam_start_1, pam_end_1 = hit.pam_start_1based, hit.pam_end_1based
    else:
        prot_start_1, prot_end_1 = _map_rc_interval_to_original(
            protospacer_start,
            protospacer_end,
            original_length,
        )
        pam_start_1, pam_end_1 = hit.pam_start_1based, hit.pam_end_1based

    full_start_1 = min(prot_start_1, pam_start_1)
    full_end_1 = max(prot_end_1, pam_end_1)

    return Candidate(
        sequence_id=hit.sequence_id,
        strand=hit.strand,
        protospacer_sequence_5to3=protospacer_sequence,
        pam_sequence_5to3=hit.pam_sequence_5to3,
        protospacer_start_1based=prot_start_1,
        protospacer_end_1based=prot_end_1,
        pam_start_1based=pam_start_1,
        pam_end_1based=pam_end_1,
        cut_site_1based=_cut_site_1based(hit.strand, pam_start_1, pam_end_1, original_length),
        full_candidate_start_1based=full_start_1,
        full_candidate_end_1based=full_end_1,
        relative_position_percent=_relative_position_percent(
            full_start_1, full_end_1, original_length
        ),
        target_length=config.target_length,
        pam_pattern=hit.pam_pattern,
    )


def _relative_position_percent(
    start_1based: int,
    end_1based: int,
    original_length: int,
) -> float:
    """Posicao do ponto medio do candidato na sequencia, em porcentagem.

    Indica se o sitio esta perto do inicio, no meio ou perto do fim da
    sequencia de entrada.

    A interpretacao usual em desenho de guias e que sitios na porcao inicial da
    regiao codificante tendem a ser preferidos para nocaute, porque uma
    interrupcao precoce tem mais chance de inativar a proteina. Essa leitura so
    vale quando a entrada e de fato um gene na orientacao codificante, o que o
    pipeline nao tem como verificar. Por isso o campo e uma indicacao de
    posicao, e nao um criterio de qualidade, e nao entra no score.
    """

    if original_length <= 0:
        return 0.0
    meio = (start_1based + end_1based) / 2
    return round(meio / original_length * 100, 1)


def _cut_site_1based(
    strand: str,
    pam_start_1based: int,
    pam_end_1based: int,
    original_length: int,
) -> int | None:
    """Calcula o sitio de corte previsto, na sequencia original.

    Devolve a posicao da base imediatamente anterior ao corte: o corte ocorre
    entre a posicao devolvida e a seguinte.

    Na fita direta, o PAM esta a jusante do protospacer, e o corte fica
    ``CAS9_CUT_OFFSET_FROM_PAM`` bases antes do inicio do PAM. Na fita reversa
    complementar, o PAM aparece em coordenadas menores da sequencia original,
    entao o corte fica a mesma distancia depois do fim do PAM.

    Devolve ``None`` quando a posicao cairia fora da sequencia, o que pode
    ocorrer com protospacers muito curtos ou PAM nas extremidades.
    """

    if strand == "+":
        position = pam_start_1based - CAS9_CUT_OFFSET_FROM_PAM - 1
    else:
        position = pam_end_1based + CAS9_CUT_OFFSET_FROM_PAM

    if 1 <= position <= original_length - 1:
        return position
    return None


def _map_rc_interval_to_original(start_0: int, end_0: int, original_length: int) -> tuple[int, int]:
    """Mapeia intervalo 0-based [start, end) do reverso complementar para original 1-based."""

    start_1based = original_length - end_0 + 1
    end_1based = original_length - start_0
    return start_1based, end_1based
