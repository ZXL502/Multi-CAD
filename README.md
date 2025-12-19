# Multi-CAD

## 1. Problem Definition
Given multi-view images (front, top, right, iso) and a natural-language prompt describing design intent, the goal is to generate an executable, parameterized CAD program. The program is expressed in a hierarchical, slot-based DSL with 8-bit discretized parameters, primarily using `Extrude` operations with auxiliary `Revolve` operations. Outputs must have valid syntax, run in OCC/CadQuery, and match the provided views.

## 2. Dataset to DSL Mapping
Source data is CAD JSON containing sequences of `ExtrudeFeature`, `RevolveFeature`, `Profile`, `Loop`, and `Curve`. Existing parsers (`macro.py`, `sketch.py`, `curves.py`, `extrude.py`) convert JSON into the DSL command sequence.

### DSL Definition (v1.3)
- **Structure Commands:** `SOLID_START`, `SOLID_END`, `PROFILE_START`, `PROFILE_END`, `LOOP_START`, `LOOP_END`
- **Sketch Primitives:** `LINE`, `ARC`, `CIRCLE`
- **Operations:** `OP_EXTRUDE` (primary), `OP_REVOLVE` (auxiliary)
- **Termination:** `EOS`

Each token has `N_ARGS = 20` slots; unused slots are filled with `PAD_VAL = -1`. Parameters are discretized to the 0–255 range. Sketch parameters cover coordinates, radii, and angles; extrude parameters include `extent_pos`, `extent_neg`, and boolean flags; revolve parameters include axis, angle, and booleans.

This DSL is stepwise generative with grammar masks, supports local parameter edits, allows precise log-likelihood computation, and compiles deterministically for execution—distinct from latent-vector representations.

## 3. Model Architecture
- **Input:** Four-view images plus natural-language prompt describing logic, symmetry, and operations.
- **Backbone:** Open-source VLM/MLLM with frozen base; LoRA finetunes language decoding and cross-attention layers.
- **Outputs:**
  - Command head classifies over `ALL_COMMANDS_V13` (cross-entropy loss).
  - Argument head predicts 0–255 values per slot with `CMD_ARGS_MASK_V13` masking invalid slots (masked cross-entropy loss).
- **Grammar Mask:** Enforces legal next commands and slot fillability via `TREE_HIERARCHY_V13`, greatly reducing invalid programs.

## 4. Training Algorithm
1. **SFT (Supervised Finetuning):** Learn DSL syntax and parameter distributions with loss `L = L_cmd + L_args(masked)` to produce baseline policy \(\pi_{sft}\) targeting ≥50–70% program validity (PV).
2. **Automatic Preference Data (Execution-verified):** Sample K candidates (K=8/16) from \(\pi_{sft}\), dequantize to CadQuery, execute in OCC, render multi-view silhouettes, and score \(S = w_v \cdot valid + w_i \cdot IoU - w_l \cdot length\) (recommended \(w_v=3, w_i=2, w_l=0.05\)). Form preference pairs with best (y⁺) vs worst/bottom-k (y⁻).
3. **DPO (Direct Preference Optimization):** Optimize only LoRA parameters with reference \(\pi_{sft}\) so the model prefers executable, geometrically accurate DSL programs, using combined command and masked-argument log probabilities.
4. **Iterative DPO (Optional):** Re-generate preferences with \(\pi_{dpo}\) for 1–2 rounds to boost PV/IoU.

## 5. Inference
Decode DSL with grammar masks from images and prompt, compile to CadQuery, and execute in OCC. If invalid, resample or beam search (limited retries). Output is an editable CAD program.

## 6. Experimental Design
- **Metrics:** Program Validity (PV), multi-view silhouette IoU, Chamfer Distance (optional), command accuracy, extrude/revolve operation accuracy, and parameter error (token accuracy or dequantization error).
- **Subset Analysis:** Report PV/IoU on revolve-heavy subset to show prompt + DPO handles long-tail operations.
- **Comparisons:** SFT-only, no grammar mask, valid-only vs valid+IoU preference scoring, and (optional) free-form Python generation as a baseline to justify DSL.
- **Ablations:** Vary K (4/8/16), remove prompt, remove args mask, and compare hierarchy versions (v1.2 vs v1.3).

## 7. Core Contributions
- Hierarchical slot-based DSL mapping CAD JSON into executable, optimizable program space.
- Execution-verified preference optimization via OCC + rendering without RL rollouts.
- VLM + LoRA + DPO pipeline improving executability and geometric fidelity under multi-view + language conditions.
- Extrude-focused backbone with explicit revolve long-tail evaluation.

## 8. Minimal End-to-End Checklist
- Fixed DSL: `ALL_COMMANDS_V13` + `CMD_ARGS_MASK_V13`.
- DSL→CadQuery compiler.
- OCC + silhouette IoU evaluator.
- SFT training.
- Preference-construction scripts.
- DPO (LoRA).

## 9. Repo Layout and Reference Implementations
- **`multicad/constants.py`** — enumerates v1.3 commands, slot masks, and the tree hierarchy used by grammar masks.
- **`multicad/dsl.py`** — minimal token structure, serialization helpers, and padding logic for 20-slot commands.
- **`multicad/grammar.py`** — grammar-state tracker that emits command masks compatible with `TREE_HIERARCHY_V13`.
- **`multicad/quantization.py`** — 8-bit quantization/dequantization helpers for parameter slots.
- **`multicad/compiler.py`** — validation-oriented CadQuery shim that checks slot masks per token before dispatching to a kernel.
- **`multicad/evaluation.py`** — execution-aware scoring with PV/IoU-weighted score (w_v=3, w_i=2, w_l=0.05 default).
- **`multicad/training/sft.py`** — protocol-based SFT scaffold (`log_probs`, `update`) for grammar-masked supervised tuning.
- **`multicad/training/preferences.py`** — execution-verified preference builder selecting best/worst candidates per silhouette/length score.
- **`multicad/training/dpo.py`** — DPO loss/training loop over preference pairs, suitable for LoRA-only updates against π_sft.

These stubs make the paper plan executable: load images/prompts, decode DSL with grammar masks, compile/check programs, build automatic preferences, and apply SFT→DPO.
