"""Direct Preference Optimization utilities."""
from __future__ import annotations

import math
from typing import Iterable, Protocol

from ..dsl import DSLToken
from .preferences import PreferencePair


class PreferenceModel(Protocol):
    def log_probs(self, tokens: Iterable[DSLToken]) -> float:
        ...

    def update(self, loss: float) -> None:
        ...


def dpo_loss(
    model: PreferenceModel,
    pair: PreferencePair,
    reference_log_ratio: float | None = None,
    beta: float = 0.1,
) -> float:
    logp_pref = model.log_probs(pair.preferred)
    logp_dis = model.log_probs(pair.disfavored)
    if reference_log_ratio is None:
        reference_log_ratio = 0.0
    log_ratio = logp_pref - logp_dis - reference_log_ratio
    return -math.log1p(-math.tanh(beta * log_ratio))


def train_dpo(model: PreferenceModel, pairs: Iterable[PreferencePair], beta: float = 0.1) -> float:
    total_loss = 0.0
    for pair in pairs:
        loss = dpo_loss(model, pair, beta=beta)
        model.update(loss)
        total_loss += loss
    return total_loss
