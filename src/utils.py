from __future__ import annotations

import math
import re
from typing import Any, Iterable


def resolve_block_order(subject_id: Any, block_orders: Iterable[Iterable[int]]) -> list[int]:
    """Assign one of the six 2/4/8 orders from stable subject digits."""

    orders = [[int(value) for value in order] for order in block_orders]
    if not orders:
        raise ValueError("task.block_orders must contain at least one order")
    digits = re.findall(r"\d+", str(subject_id))
    subject_number = int(digits[-1]) if digits else 0
    return orders[subject_number % len(orders)]


def _finite_correct_rts(rows: Iterable[dict[str, Any]], set_size: int | None = None) -> list[float]:
    values: list[float] = []
    for row in rows:
        if set_size is not None and int(row.get("set_size", 0) or 0) != int(set_size):
            continue
        if not bool(row.get("response_correct", False)):
            continue
        value = row.get("response_rt_s")
        if value is None:
            continue
        rt_s = float(value)
        if math.isfinite(rt_s):
            values.append(rt_s)
    return values


def summarize_trials(rows: Iterable[dict[str, Any]]) -> dict[str, float | int]:
    """Return accuracy, set-size means, and the participant Hick slope."""

    data = list(rows)
    trial_count = len(data)
    correct_count = sum(bool(row.get("response_correct", False)) for row in data)
    timeout_count = sum(bool(row.get("response_timeout", False)) for row in data)

    means_ms: dict[int, float] = {}
    for set_size in (2, 4, 8):
        rts = _finite_correct_rts(data, set_size)
        means_ms[set_size] = 1000.0 * sum(rts) / len(rts) if rts else float("nan")

    xs: list[float] = []
    ys: list[float] = []
    for set_size in (2, 4, 8):
        mean_ms = means_ms[set_size]
        if math.isfinite(mean_ms):
            xs.append(math.log2(set_size))
            ys.append(mean_ms)

    intercept_ms = slope_ms_per_bit = r_squared = float("nan")
    if len(xs) >= 2:
        x_bar = sum(xs) / len(xs)
        y_bar = sum(ys) / len(ys)
        denominator = sum((x - x_bar) ** 2 for x in xs)
        if denominator > 0:
            slope_ms_per_bit = sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys)) / denominator
            intercept_ms = y_bar - slope_ms_per_bit * x_bar
            fitted = [intercept_ms + slope_ms_per_bit * x for x in xs]
            ss_total = sum((y - y_bar) ** 2 for y in ys)
            ss_residual = sum((y - y_hat) ** 2 for y, y_hat in zip(ys, fitted))
            r_squared = 1.0 - ss_residual / ss_total if ss_total > 0 else 1.0

    all_correct_rts = _finite_correct_rts(data)
    mean_correct_rt_ms = (
        1000.0 * sum(all_correct_rts) / len(all_correct_rts) if all_correct_rts else float("nan")
    )
    return {
        "trial_count": trial_count,
        "correct_count": correct_count,
        "timeout_count": timeout_count,
        "accuracy": correct_count / trial_count if trial_count else 0.0,
        "timeout_rate": timeout_count / trial_count if trial_count else 0.0,
        "mean_correct_rt_ms": mean_correct_rt_ms,
        "mean_rt_n2_ms": means_ms[2],
        "mean_rt_n4_ms": means_ms[4],
        "mean_rt_n8_ms": means_ms[8],
        "hick_intercept_ms": intercept_ms,
        "hick_slope_ms_per_bit": slope_ms_per_bit,
        "hick_r_squared": r_squared,
    }
