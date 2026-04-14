import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, func_name: str, block_time: datetime, message: str):
        self.func_name = func_name
        self.block_time = block_time
        super().__init__(message)


def is_positive_int(num: int) -> bool:
    return isinstance(num, int) and num > 0


def validate_init_data(critical_count: int, time_to_recover: int) -> None:
    errors = []

    if not is_positive_int(critical_count):
        errors.append(ValueError(INVALID_CRITICAL_COUNT))

    if not is_positive_int(time_to_recover):
        errors.append(ValueError(INVALID_RECOVERY_TIME))

    if errors:
        raise ExceptionGroup(VALIDATIONS_FAILED, errors)


@dataclass
class BreakerState:
    count_of_tryings: int = 0
    fall_time: datetime | None = None


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ):
        validate_init_data(critical_count, time_to_recover)
        self.critical_count: int = critical_count
        self.time_to_recover: int = time_to_recover
        self.triggers_on: type[Exception] = triggers_on

    def __call__(self, func: CallableWithMeta[P, R_co]) -> Callable[..., R_co]:
        state = BreakerState()

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            self._check_fall_time(func, state)
            return self._call_func(func, state, *args, **kwargs)

        return wrapper

    def _check_fall_time(self, func: CallableWithMeta[P, R_co], state: BreakerState) -> None:
        now = datetime.now(UTC)

        if state.fall_time is not None:
            if (now - state.fall_time).total_seconds() < self.time_to_recover:
                msg = f"{func.__module__}.{func.__name__}"
                raise BreakerError(msg, state.fall_time, TOO_MUCH)
            state.fall_time = None
            state.count_of_tryings = 0

    def _call_func(
        self, func: CallableWithMeta[P, R_co], state: BreakerState, *args: P.args, **kwargs: P.kwargs
    ) -> Any:
        try:
            res = func(*args, **kwargs)
        except self.triggers_on as e:
            state.count_of_tryings += 1
            if state.count_of_tryings < self.critical_count:
                raise
            state.fall_time = datetime.now(UTC)
            msg = f"{func.__module__}.{func.__name__}"
            raise BreakerError(msg, state.fall_time, TOO_MUCH) from e
        else:
            state.count_of_tryings = 0
            state.fall_time = None
            return res


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
