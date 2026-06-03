# PHASE 1 — INVENTORY & DECISIONS (v3.8.0)

Consumes PHASE-0-VERIFICATION.md. Locks architecture per surface, per-element
translation rules, source-evidence DO-NOT-WRITE lists, cite disposition,
decisions register, and the Phase 2 sub-phase order with explicit STOPs.

---

## 1A — File-by-file plan

### NEW files

| # | Path | Source | Est. lines |
|---|---|---|---|
| N1 | `skills/higgsfield-canvas/SKILL.md` | canvas-intro (web) + canvas PDF + 11 imgs | ~175 |
| N2 | `skills/higgsfield-content-factory/SKILL.md` | content-factory/SKILL.md (Stages 1–3 + taxonomy + UX) | ~430 |
| N3 | `skills/higgsfield-content-factory/publish-and-report-workflow.md` | content-factory Stages 4–5 | ~200 |
| N4 | `skills/higgsfield-gpt-image-2/reference-sheet-workflow.md` | Reference Workflow PDF + PRODUCT REFERENCE SHEET PROMPTS.txt | ~200 |
| N5 | `templates/seedance/anime-animation.md` | Fotachu workflow md | ~110 |

### EDITED files (content)

| # | Path | Change |
|---|---|---|
| E1 | `skills/higgsfield-workspaces/SKILL.md` | NEW `### Higgsfield Collab` section |
| E2 | `skills/higgsfield-seedance/SKILL.md` | NEW `## Video References (@video_1)` section |
| E3 | `skills/higgsfield-motion/SKILL.md` | Kling Motion Control delta subsection |

### EDITED files (infra / cascade)

| # | Path | Change |
|---|---|---|
| I1 | `seedance_lint.py` | T5: bracket-notation + NSFW-FP + GREAT-tier vocab |
| I2 | `.markdownlint.json` | `"MD060": false` (record table-style decision) |
| I3 | `generate_user_guide.py` | +2 SUB_SKILL_DESCRIPTIONS entries; version; FAQ §25 |
| I4 | `validate_user_guide.py` | baseline retarget v3.7.16 → v3.8.0 |
| I5 | `SKILL.md` (root dispatcher) | +2 sub-skill routing rows; version 3.8.0 |
| I6 | `README.md` | version badge + footer |
| I7 | `CLAUDE.md` | "21 sub-skill directories" → "25" |
| I8 | `CHANGELOG.md` | v3.8.0 entry (house style) |
| I9 | `docs/user-guide/USER-GUIDE.pdf` + `.baseline-v3.8.0` | regen + rotate |

### Frontmatter version cascade

All NEW SKILL.md files get `metadata.version: 1.0.0`, `updated: <date>`,
`parent: higgsfield`. EDITED sub-skills get `metadata.version` bumped + `updated`
refreshed. Root SKILL.md `metadata.version: 3.8.0`.

---

## 1B — Per-element translation rules

### N1 Canvas (per-element)
| Element | Rule |
|---|---|
| What Canvas is | Translate canvas-intro definition; "node-based editor / infinite board" verbatim-close (verifiable surface fact) |
| Node types | List the documented set: Prompt, Image, Video model, Style transfer, Motion, Render output, References (Upload, Assets). Cross-check against EXTRA VIEWS screenshot node menu (Prompt / Image Generator / Video Generator / Voice Generator / LLM Assistant / Upload / Assets) — present BOTH framings as "node categories" without over-claiming exact menu labels |
| Supported models | 7 named (Soul 2.0, Seedance 2.0, Kling 3.0, Wan 2.7, Veo 3.1, GPT Image 2.0, Nano Banana Pro) — verbatim from canvas-intro; defer model detail to sibling skills |
| Connection model | "prompt feeds image, image feeds video, style branches" — translate; typed sockets noted from screenshots |
| Named canvas patterns | Simple Seedance 2.0 / Extend Video / Image Edit / StoryBoard With Elements / Long Video (fan-out) — from CANVAS B–F titlebars + PDF; one-line each |
| Cost model | "build/connect/edit free; credits deducted only when a node generates, same rate as elsewhere" — verbatim-close (load-bearing) |
| Shared Canvas | "real-time team collaboration via shared link; like Figma; auto-versioning; node-attached comments" — from canvas-intro |
| Templates / assets-as-nodes | translate |

### N2/N3 Content-factory (per-element)
| Element | Rule |
|---|---|
| 5-stage pipeline | Translate the spine (Research→Plan→Generate→Publish→Report) as orchestration guidance, downgraded register (craft-opinion default split) |
| 5 UGC format taxonomy | UGC Entertainment / Street Interview / Unboxing / Product Review / ASMR — translate as a campaign-mix layer; even `floor(N/5)` split labelled "default, user-overridable" |
| Button-driven UX | AskUserQuestion discipline + per-stage banners — translate as interaction pattern |
| API ground-truth | DEFER to higgsfield-marketing-studio; do NOT re-document presets/params/avatars; cross-ref only |
| Stage 1 research | 8 web searches + 2 web_fetch + Viral Content Brief — translate as method, not guarantee |
| Stage 4 Meta Ads (satellite) | Translate the WORKFLOW only; name no unverified Meta tool signatures; heavy "not verified, connector-dependent" caveat |
| Stage 5 cost report (satellite) | Cost-comparison concept only; dollar figures presented as "user-supplied / industry-average estimate, NOT a Higgsfield quote"; pull live spend via `transactions(limit=200)` (already in MS §12 — cross-ref) |

### N4 Reference-sheet (per-element)
| Element | Rule |
|---|---|
| Automatic Product Reference Sheet | 3-step UI flow (upload → paste provided prompt → generate); "best with Nano Banana Pro / Nano Banana 2 / GPT Image 2" verbatim |
| GLOBAL IDENTITY LOCK prompt | Preserve VERBATIM from `.txt` (load-bearing copy/paste asset) with bracketed placeholders |
| Automatic Prompt Creator meta-prompt | Preserve VERBATIM from `.txt` |
| Worked hat + dress examples | Preserve VERBATIM (real production prompts) |
| Camera/capture spec | Canon EOS R5 / RF 100mm Macro / f/8 / ISO 100 — verbatim (it's in the source template) |

### N5 Anime-animation (per-element)
| Element | Rule |
|---|---|
| Layered formula | SUBJECT+ACTION+ENVIRONMENT+CAMERA+STYLE+CONSTRAINTS — translate |
| Anime style block | Preserve VERBATIM (the "2026 animation style… cel-shading…" block) as a reusable style string |
| Character-spreadsheet prompt | Preserve VERBATIM (the turnaround-board prompt) |
| IP-safe constraints | Preserve the NO NSFW / NO COPYRIGHTED / RESPECT MANGA PANELS line verbatim |
| Attribution | Credit Fotachu (CPP creator) in source-acknowledgment footer |

### E2 Video references (per-element): translate the "reads reliably (world/material/physics/camera/production/color/weather) vs less reliably (frame-accurate continuation / exact identity / dialogue)" contract + @video_1 per-intent syntax + the three "cannot" limits. All from Reference Workflow PDF (Higgsfield official).

### E3 Kling delta: add only the net-new (Matches Video/Image binding, element-binding-Matches-Video-only, shorter-output diagnostic, motion-library source, close-up-face/emotional-transition). Reconcile orientation naming as "also surfaced as Matches Video / Matches Image."

---

## 1C — Source-evidence boundary (DO-NOT-WRITE, per surface)

**Canvas (N1):**
- ❌ Hard node/fan-in limits, max node counts.
- ❌ Fixed per-node credit numbers as pricing (only "as shown in UI").
- ❌ Plan-gating for Canvas (none documented).
- ❌ A named "Hixie" assistant. The LLM Assistant node is generic.
- ❌ Exact menu-label certainty beyond what screenshots + canvas-intro jointly support.

**Content-factory (N2/N3):**
- ❌ `generate_video.mode` slug table / `ugc_how_to` / `product_showcase` (known-false).
- ❌ Nested `avatars` inside `params`; `source` filter field (use MS §6 shape).
- ❌ Stage 5 traditional-production dollar figures as Higgsfield fact — only as user-overridable, explicitly-labelled industry estimates.
- ❌ Hard per-credit USD rate as canonical.
- ❌ Meta MCP tool/parameter signatures or auto-detect behavior as guaranteed.
- ❌ Hardcoded hook/setting/avatar UUIDs — runtime live-enumeration only.
- ❌ "empty avatars → random face" as verified (carry source-corpus-only caveat).

**Collab (E1):** only documented features (access levels, Share-to-Collab, calls, Orgs/Team-Plans shared credits/elements/admin/SSO, karma). No invented limits.

**Reference-sheet (N4):** if a product has no visible branding, do not invent any (rule already in source). No fabricated brand claims in worked examples beyond what the source shows.

**Kling (E3):** no invented numeric limits beyond the existing 3–30s / 720p-1080p already shipped.

---

## 1D — Cite / cross-reference disposition

- Root `SKILL.md`: add canvas + content-factory routing rows + Sub-Skills rows.
- `higgsfield-canvas` → cross-ref soul (Soul ID nodes), seedance/cinema/motion (model detail), marketing-studio + content-factory.
- `higgsfield-content-factory` → defer API ground-truth to marketing-studio; image-pack to gpt-image-2; pricing to marketing-studio §12; cost-report transactions to MS §12.
- `reference-sheet-workflow.md` → cross-ref gpt-image-2 parent + image-models.md (NBP/NB2/GPT Image 2) + marketing-studio cross-surface.
- `higgsfield-gpt-image-2/SKILL.md` → add satellite pointer (mirror static-ads-workflow pointer).
- seedance Video References → cross-ref cinema § @ Reference patterns.
- DISCIPLINE.md → no change required (patterns already cover the register-downgrade + DO-NOT-WRITE discipline applied here).

---

## 1E — Decisions register

| # | Decision | Rationale |
|---|---|---|
| D1 | Canvas = new sub-skill (not cinema §) | distinct nav-bar product hosting all models |
| D2 | content-factory = new sub-skill + satellite | repo pre-reserved; orchestration ≠ engine reference; isolate speculative tail |
| D3 | marketing-studio-director = ship nothing | fully consumed v3.7.13 |
| D4 | ad-creative.md = drop | generic non-Higgsfield |
| D5 | reference-sheet = satellite under gpt-image-2 | static-image production pattern; mirrors static-ads-workflow |
| D6 | Video references = seedance §-expansion | reference roles already live there |
| D7 | Collab = workspaces §-expansion | team/surface collaboration layer |
| D8 | Kling = motion §-expansion (deltas only) | section already exists |
| D9 | anime = new template | mirrors templates/seedance precedent |
| D10 | Power-user char-sheet = DROP | already covered by soul § Character Sheet Creation |
| D11 | G13 【镜头N】 = DROP resolved-by-absence | 5th surface of absence; T5 bracket-check covers delimiter case |
| D12 | MD060 = config-disable (record decision) | reformatting 50+ tables is byte-churn with zero value |
| D13 | USER-GUIDE refactor = resolved-by-dict-parity-gate | v3.7.16 gate forces propagation; add 2 dict entries |
| D14 | G15a Shared Canvas = ship (web-resolved) | canvas-intro documents live-link collab |
| D15 | G15b Collab = ship (web-resolved) | chat-intro + Team-Plans blog document it |
| D16 | G15c Hixie = NEEDS PETER | no source names it |
| D17 | G1 = NEEDS PETER | UI-flow verification, web cannot settle |
| D18 | Version = v3.8.0 minor | 2 new sub-skills (23→25) + structural scope |
| D19 | T5 linter = ship 3 checks | no dependency, long-queued |

---

## 1F — Phase 2 sub-phase order (with STOPs)

| Sub-phase | Work | STOP gate |
|---|---|---|
| 2A | N5 anime template (smallest, verbatim-heavy — warm-up) | self-review verbatim preservation |
| 2B | N4 reference-sheet satellite (verbatim templates) | DO-NOT-WRITE audit (no invented branding) |
| 2C | N1 canvas sub-skill | DO-NOT-WRITE audit (no Hixie, no limits, no pricing) |
| 2D | N2 content-factory parent | DO-NOT-WRITE audit (defer API; no known-false slugs) |
| 2E | N3 publish-and-report satellite | DO-NOT-WRITE audit (Meta/cost caveats present) |
| 2F | E1 Collab + E2 Video refs + E3 Kling §-expansions | cite check |
| 2G | I1 seedance_lint T5 + self-check | `python3 seedance_lint.py` smoke |
| 2H | I2 markdownlint + I3/I4 version constants + I5 root dispatcher + I7 CLAUDE.md | dict-parity dry-run |
| 2I | Frontmatter version cascade (all touched files) | grep audit of versions |
| 2J | I8 CHANGELOG + backlog memory updates | — |
| 2K | Validation gate: validate.py 4 phases + regen PDF + baseline + seedance_lint | all green |
| 2L | Stage diff + handoff (NO commit) | HARD STOP |

---

## 1G — Proposed version: v3.8.0 (Peter confirms at review)
