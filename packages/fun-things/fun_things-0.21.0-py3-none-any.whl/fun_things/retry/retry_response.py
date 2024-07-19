from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RetryResponse(Generic[T]):
    value: T
    ok: bool
    error: Exception
