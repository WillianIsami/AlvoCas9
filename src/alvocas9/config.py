from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(slots=True)
class PipelineConfig:
    """Configuracoes transparentes do pipeline."""

    input_path: Path
    output_dir: Path
    pam: str = "NGG"
    target_length: int = 20
    min_gc: float = 40.0
    max_gc: float = 60.0
    max_homopolymer: int = 4
    allow_n: bool = False
    min_sequence_length: int = 20

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["input_path"] = str(self.input_path)
        data["output_dir"] = str(self.output_dir)
        return data
