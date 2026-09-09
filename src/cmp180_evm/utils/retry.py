"""Bounded retry support for explicitly transient, side-effect-safe operations."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    """A bounded policy where retry_count excludes the initial attempt."""

    retry_count: int = 0
    retry_interval_ms: int = 1000

    def __post_init__(self) -> None:
        if not 0 <= self.retry_count <= 5:
            raise ValueError("retry_count must be within the bounded range 0..5")
        if not 0 <= self.retry_interval_ms <= 30_000:
            raise ValueError("retry_interval_ms must be within 0..30000")


def is_transient_instrument_error(exc: BaseException) -> bool:
    """Return whether a connection/timeout failure is eligible for retry."""
    # RsInstrument 是 optional dependency；用例外類別名稱辨識 vendor timeout，避免 CI 匯入 driver。
    vendor_transient_names = {"TimeoutException", "ResourceError"}
    return isinstance(exc, (TimeoutError, ConnectionError, OSError)) or (
        type(exc).__name__ in vendor_transient_names
    )


def run_with_bounded_retry(
    operation: Callable[[int], T],
    *,
    policy: RetryPolicy,
    cleanup: Callable[[int, BaseException], None],
    is_transient: Callable[[BaseException], bool] = is_transient_instrument_error,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Run an opt-in operation and clean up before every bounded retry."""
    for attempt in range(1, policy.retry_count + 2):
        try:
            return operation(attempt)
        except BaseException as exc:
            # Safety rejection、SCPI error 與資料 INV 不屬於 transient fault，必須立即保留原錯誤。
            if not is_transient(exc) or attempt > policy.retry_count:
                raise
            # 重試前先讓呼叫端回復安全狀態；cleanup 失敗不可被下一次 attempt 掩蓋。
            cleanup(attempt, exc)
            if policy.retry_interval_ms:
                sleep(policy.retry_interval_ms / 1000)
    raise AssertionError("bounded retry loop exited unexpectedly")
