"""Explicitly pending CMP180 constellation acquisition boundary."""

from __future__ import annotations

from .models import ConstellationDataset, HilStatus


class CMP180ConstellationSource:
    """Reserved adapter; no production SCPI exists until CMP180 evidence is verified."""

    hil_status = HilStatus.HIL_PENDING
    hardware_support = "HIL_PENDING"

    def acquire(self) -> ConstellationDataset:
        # Repository 尚無已驗證的 CMP180 constellation query／格式證據，禁止猜測指令。
        raise NotImplementedError(
            "CMP180 constellation acquisition is HIL_PENDING; no verified SCPI is registered"
        )
