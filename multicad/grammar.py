"""Grammar mask helpers to constrain DSL decoding."""
from __future__ import annotations

from typing import List, Sequence

from .constants import ALL_COMMANDS_V13, TREE_HIERARCHY_V13


class GrammarState:
    """Tracks the current grammar frontier during decoding."""

    def __init__(self) -> None:
        self.stack: List[str] = ["ROOT"]

    def allowed_commands(self) -> List[str]:
        head = self.stack[-1]
        return TREE_HIERARCHY_V13.get(head, [])

    def step(self, command: str) -> None:
        if command not in ALL_COMMANDS_V13:
            raise ValueError(f"Unknown command: {command}")
        allowed = self.allowed_commands()
        if command not in allowed:
            raise ValueError(f"Command {command} not allowed after {self.stack[-1]}")
        # Update stack with simple pushdown rules based on hierarchy
        if command in TREE_HIERARCHY_V13:
            self.stack.append(command)
        else:
            # Tokens that do not introduce new scope pop until a scope matches
            while self.stack and command not in TREE_HIERARCHY_V13.get(self.stack[-1], []):
                self.stack.pop()
            self.stack.append(command)

    def reset(self) -> None:
        self.stack = ["ROOT"]


def grammar_mask(grammar: GrammarState) -> List[int]:
    """Binary mask over ALL_COMMANDS_V13 for the next step."""
    allowed = set(grammar.allowed_commands())
    return [1 if cmd in allowed else 0 for cmd in ALL_COMMANDS_V13]


def enforce_command_sequence(commands: Sequence[str]) -> None:
    state = GrammarState()
    for cmd in commands:
        state.step(cmd)
