import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("project", ROOT / "project.py")
project = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(project)


def test_end_screen_triggered_at_one_million_score():
    assert project.should_trigger_end_screen(999_999) is False
    assert project.should_trigger_end_screen(1_000_000) is True
    assert project.should_trigger_end_screen(1_000_001) is True
