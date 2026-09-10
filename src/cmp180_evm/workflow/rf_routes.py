"""RF routing gate based on what the instrument and this software can actually do.

與 `wlan_bands.py` 相同的分層原則，但判定依據已在 2026-09-10 改變：

舊行為以 `approved_profile.routes` 白名單擋下所有未完成 HIL 的路徑，導致
「要跑 HIL 才能加進白名單、但不在白名單就不能跑 HIL」的死結。頻率／頻寬／功率
早已改為只擋物理上做不到的事（見 CLAUDE.md），route 現在對齊同一原則。

現在只擋兩件軟硬體真的做不到的事：

1. Port 必須實際存在於這台儀器，且 Generator 與 Analyzer 不可同一個 port。
2. Generator 端的輸出 port 必須是本軟體控制得到的。CMP180 command map 目前只有
   query `ROUTe:GPRF:GEN:SPATh?`，**沒有**經過驗證的 generator RF path setter，
   因此 Generator 輸出固定在儀器 workspace 既有的 port（實機為 RF1.1）。
   接線換到別的 Generator port，軟體無法通知儀器，量測必然收不到訊號。

Analyzer 端相反：`ROUTe:WLAN:MEAS:SPATh` 已驗證可寫入，所以 RF1.1 → 任一已安裝
Analyzer port 都可以實際送 RF 蒐證。

`approved_profile.routes` 保留為「是否已完成 HIL」的**標示**，由
`route_is_hil_verified()` 查詢，不再阻擋執行。
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
    installed_ports: list[str],
    commandable_generator_ports: list[str] | None = None,
) -> RfRoute:
    """Allow any route this instrument physically has and this software can command.

    `commandable_generator_ports` 為 None 時只做「port 存在 + 兩端不同」檢查，供
    校正等不送 RF 的紙上作業使用；要開 RF 的呼叫端必須傳入清單。
    """
    route = parse_route(value)
    installed = {port.strip().upper() for port in installed_ports}
    for port in (route.generator_port, route.analyzer_port):
        if port not in installed:
            raise ValueError(
                f"Port {port} is not present on this instrument; installed ports are "
                f"{', '.join(sorted(installed))}"
            )
    if commandable_generator_ports is not None:
        commandable = {port.strip().upper() for port in commandable_generator_ports}
        if route.generator_port not in commandable:
            # 不是安全政策，是能力限制：沒有已驗證的 generator RF path setter，
            # 軟體無法把 Generator 輸出切到別的 port，硬送只會量到空氣。
            raise ValueError(
                f"Generator port {route.generator_port} cannot be selected remotely: no "
                f"verified CMP180 generator RF path setter exists, so the generator stays "
                f"on {', '.join(sorted(commandable))}. Move the generator cable back, or "
                f"add a verified setter to the SCPI command map first."
            )
    return route


def route_is_hil_verified(value: object, approved_routes: list[str]) -> bool:
    """Report whether a route already has HIL evidence, without blocking execution."""
    # 純標示用途：未完成 HIL 的路徑仍可執行以蒐集證據，但結果不得作 compliance 宣稱。
    approved = {normalize_route(item) for item in approved_routes}
    return normalize_route(value) in approved
