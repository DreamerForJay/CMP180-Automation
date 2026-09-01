"""Apply an approved path-loss profile to a measurement plan.

設計重點（與 2026-08-28 的 INV 回歸直接相關）：

- Path loss 套用在 **external attenuation**，而不是 expected nominal power。
  External attenuation 是 CMP180 用來把量測值換算回 DUT reference plane 的機制，
  `wlan_tx.set_external_attenuation` 已通過 read-back 驗證。
- Expected nominal power 一律維持已驗證的 ranging 值。實機證據顯示讓它跟隨
  generator power 會使 28 個欄位全部回傳 `INV`，因此校正不得改動它。
- 沒有提供 profile 時行為與先前完全相同（external attenuation = 0），
  metadata 保留 `calibration_applied=false`。

Draft 或過期的 profile 不得用於量測修正：0 dB 佔位值若被當成正式校正，
會讓未修正的結果被誤認為已修正。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from cmp180_evm.calibration import CalibrationProfile
from cmp180_evm.workflow.rf_routes import normalize_route


@dataclass(frozen=True)
class CalibrationApplication:
    """An approved profile already checked against this run's route and frequencies."""

    profile: CalibrationProfile
    route: str

    def loss_for(self, frequency_hz: float) -> float:
        """Return interpolated path loss; extrapolation stays blocked by the profile."""
        return self.profile.loss_at(frequency_hz)

    def metadata(self) -> dict[str, object]:
        return {
            "calibration_applied": True,
            "calibration_profile_id": self.profile.profile_id,
            "calibration_revision": self.profile.revision,
            "calibration_route": self.route,
            "calibration_equipment_reference": self.profile.equipment_reference,
            "calibration_calibrated_at": self.profile.calibrated_at.isoformat(),
            "calibration_expires_at": self.profile.expires_at.isoformat(),
            # 說明修正套用在哪裡，稽核時不必回頭讀程式碼。
            "calibration_correction_target": "analyzer_external_attenuation_db",
            "calibration_note": (
                "Path loss is applied as analyzer external attenuation so results refer to "
                "the DUT reference plane; expected nominal power keeps its verified ranging value"
            ),
        }


def uncalibrated_metadata(reason: str) -> dict[str, object]:
    """Metadata for a run that intentionally applies no path-loss correction."""
    return {"calibration_applied": False, "calibration_reason": reason}


def resolve_calibration(
    profile: CalibrationProfile | None,
    *,
    route: str,
    frequencies_hz: tuple[float, ...],
    on_date: date | None = None,
) -> CalibrationApplication | None:
    """Return an application only when the profile is approved, current, and in range."""
    if profile is None:
        return None
    # lifecycle 與有效期由 profile 自行把關，錯誤訊息保留原文供稽核。
    profile.require_approved_for_use(on_date)
    expected_route = normalize_route(route)
    if normalize_route(profile.route) != expected_route:
        raise ValueError(
            f"Calibration profile covers route {profile.route}, not {expected_route}"
        )
    if not frequencies_hz:
        raise ValueError("Calibration needs at least one measurement frequency")
    lowest = profile.points[0].frequency_hz
    highest = profile.points[-1].frequency_hz
    outside = [value for value in frequencies_hz if not lowest <= value <= highest]
    if outside:
        # 外插會產生看似合理但沒有證據的修正值，因此整批拒絕而不是靜默夾在端點。
        raise ValueError(
            f"{outside[0] / 1e6:.0f} MHz is outside the calibrated range "
            f"{lowest / 1e6:.0f}–{highest / 1e6:.0f} MHz; extrapolation is blocked"
        )
    return CalibrationApplication(profile, expected_route)
