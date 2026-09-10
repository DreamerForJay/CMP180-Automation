"""從單一資料來源產生可重算的功能完成度 checklist。"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "docs" / "feature-completion-data.yaml"
OUTPUT_PATH = ROOT / "docs" / "FEATURE_COMPLETION_CHECKLIST.md"
LABELS = {
    "architecture": "Architecture / Data Model",
    "software": "Software Implemented",
    "unit_tests": "Unit Tested",
    "mock": "Mock Verified",
    "hil": "HIL Verified",
    "approved": "Approved for DUT Use",
    "documented": "Documented",
}


def _percent(done: float, total: float) -> int:
    return round(done / total * 100) if total else 100


def calculate(data: dict[str, object]) -> dict[str, int]:
    features = data["features"]
    weights = data["weights"]

    def weighted(keys: tuple[str, ...]) -> int:
        done = total = 0.0
        for feature in features:
            for key in keys:
                value = feature[key]
                if value is None:
                    continue
                weight = float(weights[key])
                total += weight
                done += weight if value else 0
        return _percent(done, total)

    scores: list[float] = []
    for feature in features:
        applicable = [key for key in weights if feature[key] is not None]
        total = sum(float(weights[key]) for key in applicable)
        done = sum(float(weights[key]) for key in applicable if feature[key])
        score = done / total * 100 if total else 100
        # RF acquisition 尚未 HIL 時最高 70%，避免完整 Mock 被誤讀為 hardware ready。
        if feature["kind"] == "rf_acquisition" and feature["hil"] is False:
            score = min(score, 70)
        feature["score"] = round(score)
        scores.append(score)

    return {
        "software": weighted(("architecture", "software", "unit_tests")),
        "mock": weighted(("mock",)),
        "hil": weighted(("hil",)),
        "documentation": weighted(("documented",)),
        "production": round(sum(scores) / len(scores)),
    }


def _badge(value: bool | None) -> str:
    return "✅" if value is True else "❌" if value is False else "N/A"


def _overall(feature: dict[str, object]) -> str:
    # 單有 gap 文件不算功能落地；Overall 只看六層 completion，文件另行計分。
    applicable = [
        feature[key]
        for key in LABELS
        if key != "documented" and feature[key] is not None
    ]
    return "COMPLETE" if all(applicable) else "TODO" if not any(applicable) else "PARTIAL"


def render(data: dict[str, object]) -> str:
    percentages = calculate(data)
    lines = [
        "# 功能完成度 Checklist",
        "",
        "> 本頁由 `docs/feature-completion-data.yaml` 經 `python scripts/build_feature_checklist.py` 產生。百分比與 Dashboard 不可手動修改；狀態判定必須同時查核程式碼、測試、artifact 與 HIL evidence。",
        "",
        "## Dashboard",
        "",
        "| Feature | Software | Mock | HIL | Approved | Overall | Score |",
        "|---|---:|---:|---:|---:|---|---:|",
    ]
    for feature in data["features"]:
        software = feature["architecture"] is True and feature["software"] is True and feature["unit_tests"] is not False
        lines.append(
            f"| {feature['name']} | {_badge(software)} | {_badge(feature['mock'])} | {_badge(feature['hil'])} | {_badge(feature['approved'])} | {_overall(feature)} | {feature['score']}% |"
        )
    lines.extend(
        [
            "",
            "## 自動計算摘要",
            "",
            f"- Overall Software Completion: **{percentages['software']}%**",
            f"- Mock Verification: **{percentages['mock']}%**",
            f"- Hardware/HIL Completion: **{percentages['hil']}%**",
            f"- Documentation Completion: **{percentages['documentation']}%**",
            f"- Production Readiness: **{percentages['production']}%**",
            "",
            "計分權重：Architecture/Data Model 15%、Software 25%、Unit Tested 15%、Mock 15%、HIL 20%、Approved 5%、Documented 5%。不適用項目不進入該分母；RF acquisition 未完成 HIL 時單項最高 70%。",
            "",
        ]
    )
    for feature in data["features"]:
        lines.extend(
            [
                f"## {feature['name']}",
                "",
                f"Overall: **{_overall(feature)}** · Priority: **{feature['priority']}** · Score: **{feature['score']}%**",
                "",
                f"Current implementation: {feature['current']}",
                "",
                f"Evidence: `{feature['evidence']}`",
                "",
                f"Missing work: {feature['missing']}",
                "",
            ]
        )
        for key, label in LABELS.items():
            value = feature[key]
            if value is None:
                lines.append(f"- N/A — {label}")
            else:
                lines.append(f"- [{'x' if value else ' '}] {label}")
        lines.extend(
            [
                "",
                f"Status: Software {'READY' if feature['software'] else 'PENDING'} / Mock {'VERIFIED' if feature['mock'] else 'PENDING' if feature['mock'] is False else 'N/A'} / HIL {'VERIFIED' if feature['hil'] else 'PENDING' if feature['hil'] is False else 'N/A'}",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只檢查輸出是否為最新")
    args = parser.parse_args()
    data = yaml.safe_load(DATA_PATH.read_text(encoding="utf-8"))
    output = render(data) + "\n"
    if args.check:
        return 0 if OUTPUT_PATH.is_file() and OUTPUT_PATH.read_text(encoding="utf-8") == output else 1
    OUTPUT_PATH.write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
