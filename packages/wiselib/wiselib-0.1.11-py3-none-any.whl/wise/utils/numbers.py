from decimal import Decimal
from typing import Iterable

EPSILON = 1e-6


def is_zero(value: float) -> bool:
    return abs(value) < EPSILON


def safe_sum(col: Iterable[float]) -> float:
    return float(sum([Decimal(str(x)) for x in col], Decimal(0)))


def safe_prod(col: Iterable[float]) -> float:
    d = Decimal("1")
    for item in col:
        d *= Decimal(str(item))
    return float(d)


def safe_add(a: float, b: float) -> float:
    return float(Decimal(str(a)) + Decimal(str(b)))


def safe_sub(a: float, b: float) -> float:
    return float(Decimal(str(a)) - Decimal(str(b)))


def safe_mult(a: float, b: float) -> float:
    return float(Decimal(str(a)) * Decimal(str(b)))


def safe_div(a: float, b: float) -> float:
    return float(Decimal(str(a)) / Decimal(str(b)))


def safe_abs(a: float) -> float:
    return float(abs(Decimal(str(a))))
