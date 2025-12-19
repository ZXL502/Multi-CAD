"""Central DSL constants for Multi-CAD."""
from __future__ import annotations

from typing import Dict, List

# Command set version v1.3
ALL_COMMANDS_V13: List[str] = [
    "SOLID_START",
    "SOLID_END",
    "PROFILE_START",
    "PROFILE_END",
    "LOOP_START",
    "LOOP_END",
    "LINE",
    "ARC",
    "CIRCLE",
    "OP_EXTRUDE",
    "OP_REVOLVE",
    "EOS",
]

# Per-command argument masks (True means the slot is used)
N_ARGS = 20
PAD_VAL = -1

# Minimal illustrative slot masks. Real projects should align these with the
# production CadQuery compiler expectations.
CMD_ARGS_MASK_V13: Dict[str, List[bool]] = {
    "SOLID_START": [False] * N_ARGS,
    "SOLID_END": [False] * N_ARGS,
    "PROFILE_START": [False] * N_ARGS,
    "PROFILE_END": [False] * N_ARGS,
    "LOOP_START": [False] * N_ARGS,
    "LOOP_END": [False] * N_ARGS,
    # Sketch primitives: x0, y0, x1, y1, radius, angle
    "LINE": [True, True, True, True] + [False] * (N_ARGS - 4),
    "ARC": [True, True, True, True, True, True] + [False] * (N_ARGS - 6),
    "CIRCLE": [True, True, True] + [False] * (N_ARGS - 3),
    # Extrude: extent_pos, extent_neg, boolean join flag
    "OP_EXTRUDE": [True, True, True] + [False] * (N_ARGS - 3),
    # Revolve: axis idx, angle, boolean join flag
    "OP_REVOLVE": [True, True, True] + [False] * (N_ARGS - 3),
    "EOS": [False] * N_ARGS,
}

# Hierarchical tree used to validate next-commands during generation.
TREE_HIERARCHY_V13: Dict[str, List[str]] = {
    "ROOT": ["SOLID_START"],
    "SOLID_START": ["PROFILE_START"],
    "PROFILE_START": ["LOOP_START", "PROFILE_END"],
    "LOOP_START": ["LINE", "ARC", "CIRCLE", "LOOP_END"],
    "LINE": ["LINE", "ARC", "CIRCLE", "LOOP_END"],
    "ARC": ["LINE", "ARC", "CIRCLE", "LOOP_END"],
    "CIRCLE": ["LINE", "ARC", "CIRCLE", "LOOP_END"],
    "LOOP_END": ["PROFILE_START", "PROFILE_END"],
    "PROFILE_END": ["OP_EXTRUDE", "OP_REVOLVE", "SOLID_END"],
    "OP_EXTRUDE": ["PROFILE_START", "OP_EXTRUDE", "OP_REVOLVE", "SOLID_END"],
    "OP_REVOLVE": ["PROFILE_START", "OP_EXTRUDE", "OP_REVOLVE", "SOLID_END"],
    "SOLID_END": ["EOS"],
}
