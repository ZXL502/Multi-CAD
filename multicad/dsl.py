"""DSL token helpers and serialization utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .constants import N_ARGS, PAD_VAL


@dataclass
class DSLToken:
    """Represents one DSL command and its argument slots."""

    command: str
    args: List[int]

    def __post_init__(self) -> None:
        if len(self.args) != N_ARGS:
            raise ValueError(f"Expected {N_ARGS} args, got {len(self.args)}")

    def masked_args(self, mask: Sequence[bool]) -> List[int]:
        return [value if use else PAD_VAL for value, use in zip(self.args, mask)]


def pad_args(args: Iterable[int]) -> List[int]:
    args_list = list(args)
    if len(args_list) > N_ARGS:
        raise ValueError("Too many args for DSL token")
    return args_list + [PAD_VAL] * (N_ARGS - len(args_list))


def serialize_program(tokens: Sequence[DSLToken]) -> str:
    """Serialize a DSL sequence into a human-readable string."""
    return "\n".join(
        f"{token.command} " + " ".join(map(str, token.args)) for token in tokens
    )


def deserialize_program(lines: Iterable[str]) -> List[DSLToken]:
    tokens: List[DSLToken] = []
    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue
        command, *arg_values = parts
        int_args = [int(v) for v in arg_values]
        tokens.append(DSLToken(command=command, args=pad_args(int_args)))
    return tokens
