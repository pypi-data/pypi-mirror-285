import time
from dataclasses import dataclass
from datetime import timedelta
from itertools import count


class OutOfRetriesError(RuntimeError):
    pass


class Retrier:
    def __iter__(self):
        raise NotImplementedError


class RetryPolicy:
    def create_retrier(self) -> Retrier:
        raise NotImplementedError


NO_LIMIT = 0


def _get_range(max_retries):
    if max_retries == NO_LIMIT:
        return count()
    return range(max_retries + 1)


@dataclass
class ExponentialBackoffRetry(RetryPolicy):
    initial: timedelta
    multiplier: float
    max_retries: int = NO_LIMIT
    max_interval: timedelta = timedelta.max

    def create_retrier(self) -> Retrier:
        return _ExponentialBackooffRetrier(self)


class _ExponentialBackooffRetrier(Retrier):
    def __init__(self, policy: ExponentialBackoffRetry):
        self._current_interval = policy.initial
        self._max_interval = policy.max_interval
        self._multiplier = policy.multiplier
        self._max_retries = policy.max_retries

    def __iter__(self):
        for _ in _get_range(self._max_retries):
            yield self
            intv = self._current_interval
            time.sleep(intv.total_seconds())
            self._current_interval = min(
                self._max_interval, self._current_interval * self._multiplier
            )


@dataclass
class FixedIntervalRetry(RetryPolicy):
    interval: timedelta
    max_retries: int = NO_LIMIT

    def create_retrier(self) -> Retrier:
        return _FixedIntervalRetrier(self)


class _FixedIntervalRetrier(Retrier):
    def __init__(self, policy: FixedIntervalRetry):
        self._interval = policy.interval
        self._max_retries = policy.max_retries

    def __iter__(self):
        for _ in _get_range(self._max_retries):
            yield self
            time.sleep(self._interval.total_seconds())


class NoRetry(RetryPolicy):
    def create_retrier(self) -> Retrier:
        return _NoRetrier(self)


class _NoRetrier(Retrier):
    def __init__(self, policy: NoRetry):
        self._max_retries = 0

    def __iter__(self):
        # We need to yield self at least once, because the caller will use the retrier as so:
        #
        # ```
        # for _ in retrier:
        #     send_request()
        # ```
        for _ in range(1):
            yield self


__all__ = [
    "RetryPolicy",
    "ExponentialBackoffRetry",
    "FixedIntervalRetry",
    "NoRetry",
    "OutOfRetriesError",
]
