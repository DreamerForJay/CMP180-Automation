import pytest

from cmp180_evm.utils.retry import RetryPolicy, run_with_bounded_retry


def test_bounded_retry_cleans_up_then_succeeds() -> None:
    attempts: list[int] = []
    cleanups: list[int] = []

    def operation(attempt: int) -> str:
        attempts.append(attempt)
        if attempt < 3:
            raise TimeoutError("temporary")
        return "ok"

    result = run_with_bounded_retry(
        operation,
        policy=RetryPolicy(retry_count=2, retry_interval_ms=0),
        cleanup=lambda attempt, exc: cleanups.append(attempt),
    )

    assert result == "ok"
    assert attempts == [1, 2, 3]
    assert cleanups == [1, 2]


def test_bounded_retry_does_not_retry_non_transient_failure() -> None:
    attempts: list[int] = []

    with pytest.raises(ValueError, match="invalid result"):
        run_with_bounded_retry(
            lambda attempt: attempts.append(attempt) or (_ for _ in ()).throw(
                ValueError("invalid result")
            ),
            policy=RetryPolicy(retry_count=3, retry_interval_ms=0),
            cleanup=lambda attempt, exc: pytest.fail("cleanup must not run"),
        )

    assert attempts == [1]


def test_retry_policy_is_bounded() -> None:
    with pytest.raises(ValueError, match="0..5"):
        RetryPolicy(retry_count=6)
