import pytest

import alvocas9
from alvocas9.cli import main


def test_package_imports() -> None:
    assert alvocas9.__version__


def test_cli_help_responds(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert "validate" in captured.out
    assert "analyze" in captured.out
