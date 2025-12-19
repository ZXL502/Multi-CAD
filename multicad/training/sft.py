"""Supervised finetuning scaffolding for DSL models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Protocol, Sequence

from ..dsl import DSLToken


class DSLModel(Protocol):
    def log_probs(self, tokens: Sequence[DSLToken]) -> float:
        ...

    def update(self, loss: float) -> None:
        ...


@dataclass
class SFTExample:
    images: Sequence[object]
    prompt: str
    target: List[DSLToken]


def sft_loss(model: DSLModel, example: SFTExample) -> float:
    return -model.log_probs(example.target)


def train_sft(model: DSLModel, dataset: Iterable[SFTExample]) -> float:
    total_loss = 0.0
    for example in dataset:
        loss = sft_loss(model, example)
        model.update(loss)
        total_loss += loss
    return total_loss
