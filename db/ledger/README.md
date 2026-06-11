# Generation Ledger

An empirical hit-rate system: one row per **generation attempt** — kept,
rejected, or filter-flagged. Unlike `../quality-memory.json` (a failure
ledger), this records the denominator, so after ~30–40 logged generations a
production has real takes-per-kept ratios per shot type and can price credit
risk before generating (`ratio` / `budget` commands in
`../../higgsfield_memory.py`).

**The 5-second rule:** logging one generation costs at most one short command
or one agent question ("keep or reject — what failed?"). The agent writes the
row; the human never formats JSON. If logging costs more attention than that,
adoption dies — optimize the write path above all else.

## Files

| File | Role |
|------|------|
| `<project>.json` | One ledger per project — the primary store. Created lazily by `log-gen <project> …`. |
| `_global.json` | **Generated** cross-project view (never hand-edit). Underscore-prefixed ledgers are excluded from it. |
| `_demo.json` | Test fixture with hand-computed expected ratios (pytest); excluded from `_global` like every `_`-prefixed file. |

Underscore-prefixed names are **reserved**.

## Row schema (append-only)

```json
{
  "id": "adze-0042",                  // <project>-NNNN, generated
  "ts": "2026-06-12T18:40:11Z",
  "model": "seedance_2_0",            // canonical specs/model-specs.json id (aliases resolved at write)
  "mode": "std",                      // optional
  "resolution": "1080p",              // optional
  "aspect": "21:9",                   // optional
  "duration_s": 15,                   // optional
  "internal_cuts": 3,                 // optional
  "shot_tags": ["dialogue-cu", "two-char"],  // controlled vocab; 1..3 (0..3 only when flagged)
  "scene_ref": "S14-P2",              // optional free text
  "prompt_hash": "a1b2c3d4e5f6",      // optional sha1[:12] — dedupe identical re-rolls
  "draft_tier": false,                // 480p exploration rolls; excluded from headline ratios
  "outcome": "kept",                  // kept | rejected | flagged
  "reject_reason": null,              // controlled vocab, REQUIRED iff rejected
  "credits": 160,                     // optional, plan-dependent
  "notes": "",                        // optional, one line max
  "supersedes": null                  // correction pointer — see rules below
}
```

**Rules:**

- **Append-only.** History is never edited. A correction is a NEW row with
  `supersedes: "<old id>"` (use `amend-gen <id> field=value`); the old row
  stays but is masked from all stats.
- `supersedes` points at an **earlier id in the same file**, and each id can
  be superseded **at most once** — to correct a correction, supersede the
  latest amendment.
- Models are stored as **canonical specs ids** only. Optional fields
  (resolution/aspect/duration) are not cross-validated against per-model
  enums in v1 — model-id membership only (use `seedance_lint.py --preflight`
  for enum legality before generating).
- `validate.py` schema-checks every ledger file and regenerates `_global.json`.

## Controlled vocabularies (extend via PR, never ad hoc)

**shot_tags:** `establishing` · `dialogue-cu` · `dialogue-multi` ·
`action-melee` · `action-chase` · `insert-prop` · `vfx-event` · `two-char` ·
`multi-char-3plus` · `dual-instance` · `pov` · `environment-only` ·
`creature-occluded`

**reject_reason:** `identity-drift` · `wardrobe-contamination` · `extra-cuts` ·
`blocking-broken` · `performance` · `camera-wrong` · `physics` ·
`text-render` · `filter-flagged` · `composition` · `other`

## Structural vs stochastic — the split that matters

| Class | Members | Meaning |
|-------|---------|---------|
| **Structural** | `identity-drift`, `wardrobe-contamination`, `extra-cuts`, `blocking-broken`, `text-render`, `filter-flagged`, plus every `outcome=flagged` row | Fix the prompt — re-rolling burns credits on the same failure |
| **Stochastic** | `performance`, `camera-wrong`, `physics`, `composition` | Re-roll territory — the prompt is fine, the roll wasn't |
| (neither) | `other` | Counts in n, classified in neither column |

The `ratio` command reports these classes separately per shot tag — a high
structural% says "stop re-rolling, rewrite"; a high stochastic% prices how
many takes a keep costs.
