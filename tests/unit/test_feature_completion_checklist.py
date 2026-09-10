from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml


def _module():
    path = Path("scripts/build_feature_checklist.py")
    spec = importlib.util.spec_from_file_location("build_feature_checklist", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_feature_percentages_are_derived_and_bounded() -> None:
    module = _module()
    data = yaml.safe_load(Path("docs/feature-completion-data.yaml").read_text(encoding="utf-8"))
    percentages = module.calculate(data)

    assert set(percentages) == {"software", "mock", "hil", "documentation", "production"}
    assert all(0 <= value <= 100 for value in percentages.values())
    constellation = next(item for item in data["features"] if item["name"] == "Constellation")
    assert constellation["score"] <= 70


def test_generated_checklist_is_current_and_constellation_is_partial() -> None:
    module = _module()
    data = yaml.safe_load(Path("docs/feature-completion-data.yaml").read_text(encoding="utf-8"))
    generated = module.render(data) + "\n"

    assert generated == Path("docs/FEATURE_COMPLETION_CHECKLIST.md").read_text(encoding="utf-8")
    assert "## Constellation" in generated
    assert "Overall: **PARTIAL**" in generated
    assert "- [x] Mock Verified" in generated
    assert "- [ ] HIL Verified" in generated
    assert "Authentication" not in generated.split("Missing work:")[-1]
