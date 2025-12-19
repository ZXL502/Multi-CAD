"""Placeholder CadQuery compiler interface for DSL programs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .constants import CMD_ARGS_MASK_V13
from .dsl import DSLToken


@dataclass
class CompiledResult:
    """Represents compilation status and diagnostic info."""

    success: bool
    message: str
    geometry: object | None = None


class CadQueryCompiler:
    """Lightweight shim to validate DSL arguments and hand off to a real CAD kernel."""

    def compile(self, tokens: List[DSLToken]) -> CompiledResult:
        for token in tokens:
            mask = CMD_ARGS_MASK_V13.get(token.command)
            if mask is None:
                return CompiledResult(False, f"Unknown command: {token.command}")
            masked = token.masked_args(mask)
            if len(masked) != len(mask):
                return CompiledResult(False, "Mask length mismatch")
        return CompiledResult(True, "Validation passed", geometry=None)
