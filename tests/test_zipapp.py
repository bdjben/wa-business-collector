from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

from scripts.build_zipapp import build_zipapp

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_build_zipapp_creates_no_install_runnable_archive(tmp_path: Path) -> None:
    output = tmp_path / "wa-business-collector.pyz"

    build_zipapp(PROJECT_ROOT, output)

    assert output.exists()
    with zipfile.ZipFile(output) as archive:
        names = set(archive.namelist())
    assert "__main__.py" in names
    assert "wa_business_collector/cli.py" in names
    assert "wa_business_collector/web_ui.py" in names
    assert "wa_business_collector/assets/chrome_devtools.mjs" in names

    completed = subprocess.run(
        [sys.executable, str(output), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "wa-business-collector" in completed.stdout
    assert "ui" in completed.stdout
