"""RF routing gate driven by the capability profile instead of a hardcoded route.

與 `wlan_bands.py` 相同的分層原則：CMP180 最多 16 個 RF port，但「port 存在」不等於
「這條路徑已驗證可送 RF」。核准的 route 清單來自
`configs/instrument_capabilities.example.yaml` 的 `approved_profile.routes`，
因此新增一條已完成 HIL 的路徑只要改設定檔，不需要改程式。

未列在 approved_profile 的 route 一律拒絕：線材、衰減、輸入保護與 port 校正狀態
都可能不同，未驗證前不得開啟 RF。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RfRoute:
    generator_port: str
    analyzer_port: str

    @property
    def label(self) -> str:
        return f"{self.generator_port}-{self.analyzer_port}"


def normalize_route(value: object) -> str:
    """Normalize operator-entered routing text into the canonical PORT-PORT form."""
    return str(value or "").strip().upper().replace("→", "-").replace(" ", "")


def parse_route(value: object) -> RfRoute:
    """Split a normalized route into generator and analyzer ports."""
    normalized = normalize_route(value)
    if not normalized:
        raise ValueError("Select or enter a cable route")
    parts = normalized.split("-")
    if len(parts) != 2 or not all(parts):
        raise ValueError(f"Cable route {normalized!r} must be in GENERATOR-ANALYZER form")
    generator_port, analyzer_port = parts
    if generator_port == analyzer_port:
        # 同一個 port 不能同時當來源與量測端，這在任何 profile 下都不合法。
        raise ValueError("Generator and analyzer ports must be different")
    return RfRoute(generator_port, analyzer_port)


def validate_route(
    value: object,
    *,
    approved_routes: list[str],
    installed_ports: list[str],
) -> RfRoute:
    """Allow only routes whose ports exist and whose path is approved for RF."""
    route = parse_route(value)
    installed = {port.strip().upper() for port in installed_ports}
    for port in (route.generator_port, route.analyzer_port):
        if port not in installed:
            raise ValueError(
                f"Port {port} is not present on this instrument; installed ports are "
                f"{', '.join(sorted(installed))}"
            )
    approved = {normalize_route(item) for item in approved_routes}
    if route.label not in approved:
        # 已安裝但未核准：需要完成該路徑的線材確認與 HIL 才能加入 approved_profile.routes。
        raise ValueError(
            f"Cable route {route.label} is not hardware-verified; RF output is blocked. "
            f"Approved routes: {', '.join(sorted(approved))}"
        )
    return route
