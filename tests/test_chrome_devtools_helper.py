from pathlib import Path

from wa_business_collector.devtools_bridge import NODE_HELPER

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HELPER = NODE_HELPER


def test_devtools_helper_is_resolved_from_packaged_resources() -> None:
    assert HELPER.exists()
    assert HELPER.name == "chrome_devtools.mjs"
    assert HELPER.parent.name == "assets"


def test_devtools_helper_does_not_activate_or_bring_windows_to_front() -> None:
    helper_source = HELPER.read_text()

    assert "Page.bringToFront" not in helper_source
    assert "Target.activateTarget" not in helper_source


def test_hourly_export_uses_edge_hidden_placement_for_scheduled_checker() -> None:
    script_source = (PROJECT_ROOT / "scripts" / "hourly_tv_export.sh").read_text()

    assert "--placement-mode edge-hidden" in script_source
    assert "--placement-mode visible" not in script_source


def test_hourly_export_uses_configured_python_binary_instead_of_bare_python() -> None:
    script_source = (PROJECT_ROOT / "scripts" / "hourly_tv_export.sh").read_text()

    assert "PYTHON_BIN=" in script_source
    assert "PYTHONPATH=src python -m" not in script_source
