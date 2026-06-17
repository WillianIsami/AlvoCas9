from __future__ import annotations

from pathlib import Path

from alvocas9.cli import main


ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    raise SystemExit(
        main(
            [
                "analyze",
                "--input",
                str(ROOT / "data" / "examples" / "exemplo_simples.fasta"),
                "--output",
                str(ROOT / "results" / "example"),
            ]
        )
    )
