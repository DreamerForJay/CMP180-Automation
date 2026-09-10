"""尚待 CMP180 evidence 的 MCS hardware acquisition 邊界。"""


class CMP180MCSSweepSource:
    hardware_support = "HIL_PENDING"
    hil_status = "HIL_PENDING"

    def acquire(self, *_args: object, **_kwargs: object) -> None:
        # 尚無已驗證 waveform／MCS SCPI mapping；禁止以其他儀器語法或推測命令代替。
        raise NotImplementedError(
            "CMP180 MCS sweep acquisition is HIL_PENDING: no verified waveform/SCPI mapping"
        )
