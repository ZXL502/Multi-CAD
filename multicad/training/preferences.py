"""Execution-verified preference construction utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

from ..compiler import CadQueryCompiler
from ..dsl import DSLToken
from ..evaluation import ProgramScore, score_program


@dataclass
class PreferencePair:
    preferred: List[DSLToken]
    disfavored: List[DSLToken]
    preferred_score: ProgramScore
    disfavored_score: ProgramScore


def build_preferences(
    candidates: Iterable[Sequence[DSLToken]],
    compiler: CadQueryCompiler,
    render_target: Sequence[int] | None = None,
) -> List[PreferencePair]:
    scored: List[tuple[List[DSLToken], ProgramScore]] = []
    for candidate in candidates:
        tokens = list(candidate)
        score = score_program(tokens, compiler, render_fn=None, target_render=render_target)
        scored.append((tokens, score))
    if not scored:
        return []
    scored.sort(key=lambda pair: pair[1].score, reverse=True)
    best_tokens, best_score = scored[0]
    worst_tokens, worst_score = scored[-1]
    return [
        PreferencePair(
            preferred=best_tokens,
            disfavored=worst_tokens,
            preferred_score=best_score,
            disfavored_score=worst_score,
        )
    ]
