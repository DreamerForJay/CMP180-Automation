import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT / "assets" / "cmp180_3d"


def test_cmp180_model_spec_records_scale_ports_and_provenance() -> None:
    spec = json.loads((ASSET_DIR / "model-spec.json").read_text(encoding="utf-8"))

    assert spec["scale"] == "1 Blender unit = 1 metre"
    assert spec["dimensions_m"]["chassis_width"] == 0.465
    assert spec["front_panel"]["rf_ports"] == 16
    assert len(spec["sources"]) >= 3
    assert "not a mechanical CAD" in spec["accuracy_note"]


def test_cmp180_generator_declares_safe_local_only_outputs() -> None:
    script = (ROOT / "scripts" / "build_cmp180_blender.py").read_text(encoding="utf-8")

    assert "bpy.ops.wm.save_as_mainfile" in script
    assert "bpy.ops.render.render" in script
    assert "bpy.ops.export_scene.gltf" in script
    assert "SCPI" not in script
