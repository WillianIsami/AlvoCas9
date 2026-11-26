from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


PAM_POSITION_3_LINHA = "3linha"
"""Unica posicao de PAM suportada: a 3' do protospacer, como na SpCas9.

A arquitetura do scanner assume que o protospacer fica imediatamente a 5' do
PAM. Sistemas com PAM a 5', como o TTTV de Cas12a, exigiriam outra logica de
extracao. Expor isso como parametro deixa a premissa visivel na interface, em
vez de escondida no codigo.
"""


def validate_min_sequence_length(value: int) -> None:
    """Valida o tamanho minimo de sequencia aceito na validacao do FASTA."""

    if value < 1:
        raise ValueError(
            f"min_sequence_length deve ser maior ou igual a 1. Valor informado: {value}."
        )


@dataclass(slots=True)
class PipelineConfig:
    """Configuracoes transparentes do pipeline."""

    input_path: Path
    output_dir: Path
    pam: str = "NGG"
    pam_position: str = PAM_POSITION_3_LINHA
    target_length: int = 20
    min_gc: float = 40.0
    max_gc: float = 60.0
    max_homopolymer: int = 4
    allow_n: bool = False
    min_sequence_length: int = 20

    def __post_init__(self) -> None:
        """Rejeita parametros que gerariam resultado sem significado biologico.

        Sem esta checagem, valores como ``target_length=0`` ou ``target_length``
        negativo produzem candidatos com protospacer vazio e coordenadas
        invertidas, e uma faixa de GC impossivel reprova todos os candidatos,
        sempre com codigo de saida de sucesso. Todos os problemas encontrados
        sao reportados juntos, para evitar correcao por tentativa e erro.
        """

        problems: list[str] = []

        if self.pam_position != PAM_POSITION_3_LINHA:
            problems.append(
                f"pam_position aceita apenas '{PAM_POSITION_3_LINHA}'. Valor informado: "
                f"'{self.pam_position}'. O AlvoCas9 extrai o protospacer a 5' do PAM, "
                "premissa valida para SpCas9. Sistemas com PAM a 5', como Cas12a, "
                "exigiriam outra logica de extracao e nao sao suportados."
            )

        if self.target_length < 1:
            problems.append(
                f"target_length deve ser maior ou igual a 1. Valor informado: {self.target_length}."
            )
        if not 0.0 <= self.min_gc <= 100.0:
            problems.append(
                f"min_gc deve estar entre 0 e 100. Valor informado: {self.min_gc}."
            )
        if not 0.0 <= self.max_gc <= 100.0:
            problems.append(
                f"max_gc deve estar entre 0 e 100. Valor informado: {self.max_gc}."
            )
        if self.min_gc > self.max_gc:
            problems.append(
                "min_gc nao pode ser maior que max_gc. "
                f"Valores informados: min_gc={self.min_gc} e max_gc={self.max_gc}."
            )
        if self.max_homopolymer < 1:
            problems.append(
                f"max_homopolymer deve ser maior ou igual a 1. Valor informado: {self.max_homopolymer}."
            )
        try:
            validate_min_sequence_length(self.min_sequence_length)
        except ValueError as exc:
            problems.append(str(exc))

        if problems:
            raise ValueError("Parametros invalidos: " + " ".join(problems))

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["input_path"] = str(self.input_path)
        data["output_dir"] = str(self.output_dir)
        return data
