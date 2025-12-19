"""Utilities for 8-bit parameter quantization and dequantization."""
from __future__ import annotations

from typing import Iterable, List, Tuple


def quantize(values: Iterable[float], value_range: Tuple[float, float]) -> List[int]:
    v_min, v_max = value_range
    if v_max <= v_min:
        raise ValueError("Invalid value range")
    scale = 255.0 / (v_max - v_min)
    return [int(max(0, min(255, round((v - v_min) * scale)))) for v in values]


def dequantize(values: Iterable[int], value_range: Tuple[float, float]) -> List[float]:
    v_min, v_max = value_range
    if v_max <= v_min:
        raise ValueError("Invalid value range")
    scale = (v_max - v_min) / 255.0
    return [v_min + v * scale for v in values]
