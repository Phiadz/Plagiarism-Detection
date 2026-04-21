# Đo thời gian thực thi
import time


class Timer:
    def __init__(self) -> None:
        self._start: float | None = None
        self._end: float | None = None

    def start(self) -> None:
        self._start = time.perf_counter()
        self._end = None

    def stop(self) -> float:
        if self._start is None:
            raise RuntimeError("Timer has not been started. Call start() first.")
        self._end = time.perf_counter()
        return self.elapsed_ms

    @property
    def elapsed_ms(self) -> float:
        if self._start is None:
            return 0.0
        end = self._end if self._end is not None else time.perf_counter()
        return (end - self._start) * 1000