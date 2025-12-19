"""Execution-aware scoring utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Sequence

from .compiler import CadQueryCompiler
from .dsl import DSLToken


@dataclass
class ProgramScore:
    valid: bool
    iou: float
    length_penalty: float

    @property
    def score(self) -> float:
        return 3 * float(self.valid) + 2 * self.iou - 0.05 * self.length_penalty


def silhouette_iou(render_a: Sequence[int], render_b: Sequence[int]) -> float:
    if len(render_a) != len(render_b) or not render_a:
        return 0.0
    intersection = sum(int(a and b) for a, b in zip(render_a, render_b))
    union = sum(int(a or b) for a, b in zip(render_a, render_b))
    return intersection / union if union else 0.0


def score_program(
    tokens: List[DSLToken],
    compiler: CadQueryCompiler,
    render_fn: Callable[[List[DSLToken]], Sequence[int]] | None = None,
    target_render: Sequence[int] | None = None,
) -> ProgramScore:
    compiled = compiler.compile(tokens)
    valid = compiled.success
    iou = 0.0
    if render_fn is not None and target_render is not None:
        iou = silhouette_iou(render_fn(tokens), target_render)
    return ProgramScore(valid=valid, iou=iou, length_penalty=len(tokens))
