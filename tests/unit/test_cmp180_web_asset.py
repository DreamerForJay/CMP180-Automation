import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "src" / "cmp180_evm" / "web" / "static"


def read_glb(path: Path) -> tuple[bytes, dict]:
    body = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", body)
    assert (magic, version, length) == (b"glTF", 2, len(body))
    chunk_length, chunk_type = struct.unpack_from("<I4s", body, 12)
    assert chunk_type == b"JSON"
    return body, json.loads(body[20 : 20 + chunk_length])


def triangle_count(asset: dict) -> int:
    return sum(
        asset["accessors"][primitive["indices"]]["count"] // 3
        for mesh in asset["meshes"]
        for primitive in mesh["primitives"]
    )


def test_web_model_preserves_geometry_and_is_self_contained() -> None:
    source_body, source = read_glb(ROOT / "assets" / "cmp180_3d" / "cmp180.glb")
    body, asset = read_glb(STATIC / "assets" / "cmp180-web.glb")
    manifest = json.loads((STATIC / "assets" / "cmp180-web.manifest.json").read_text())

    # Web 副本只做合併與量化；原始三角面數不減少，避免孔位與接口被簡化掉。
    assert triangle_count(asset) == triangle_count(source) == manifest["triangles"]
    assert len(asset["materials"]) == len(source["materials"])
    assert len(asset["meshes"]) <= 24
    assert len(body) < len(source_body) * 0.75
    assert hashlib.sha256(body).hexdigest() == manifest["web_sha256"]
    assert hashlib.sha256(source_body).hexdigest() == manifest["source_sha256"]
    # 內網執行不可依賴遠端貼圖、buffer 或需要外部下載的解碼器。
    assert all("uri" not in item for item in asset.get("buffers", []) + asset.get("images", []))
    assert not {"KHR_draco_mesh_compression", "EXT_meshopt_compression"}.intersection(
        asset.get("extensionsRequired", [])
    )
    assert not any("Studio" in node.get("name", "") for node in asset["nodes"])


def test_viewer_vendor_matches_manifest_and_includes_license() -> None:
    manifest = json.loads((STATIC / "assets" / "cmp180-web.manifest.json").read_text())
    vendor = STATIC / "vendor" / "model-viewer"
    # Git for Windows 可能將文字換行改為 CRLF；完整性檢查先正規化為上游 LF。
    viewer = (vendor / "model-viewer.min.js").read_text(encoding="utf-8").replace("\r\n", "\n").encode()
    assert hashlib.sha256(viewer).hexdigest() == manifest["model_viewer_sha256"]
    assert "Apache License" in (vendor / "LICENSE").read_text()


def test_viewer_load_is_opt_in_and_does_not_bind_instrument_actions() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    script = (STATIC / "cmp180-viewer.js").read_text(encoding="utf-8")
    assert '<model-viewer' not in html
    assert '/assets/cmp180-hero.png' in html
    assert "loadButton.addEventListener('click', load)" in script
    assert 'src="/cmp180-viewer.js?v=1"' in html
    assert "/api/" not in script
    assert "cmp180-language-change" in script
    assert "visibilitychange" in script
    assert "prefers-reduced-motion" in script
