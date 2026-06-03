# PHASE 0 — VERIFICATION (v3.8.0)

**Release:** v3.8.0 (proposed — MINOR bump; see § VERIFY 0.6)
**Kickoff:** Close out the WORKING FOLDER integration arc — integrate net-new
working-folder documentation + a cross-reference pass for anything the
v3.7.12–16 burst missed. One mega release.
**Date stamped at composition.** Methodology inherits v3.7.13/14/15/16
translation precedent + DISCIPLINE.md source-evidence boundary.

---

## VERIFY 0.0 — Repo baseline

- Branch `main`, clean tree, latest tag **v3.7.16** (`662e47b`). ✓ confirmed.
- Sub-skill count: **23** (`skills/*/SKILL.md`, excluding `skills/shared/`).
  `ls skills/` → 24 dirs incl. `shared/`; `find skills -name SKILL.md` → 23. ✓
- **CLAUDE.md drift:** line 26 says "21 sub-skill directories" — stale by 2
  (pre-dates gpt-image-2 + marketing-studio). After this release the count is
  **25** (adds higgsfield-canvas + higgsfield-content-factory). CLAUDE.md must
  be corrected to 25 this release (was the standing "recount if it drifts"
  instruction).

---

## VERIFY 0.1 — WORKING FOLDER recursive inventory

Walked `~/Desktop/WORKING FOLDER` recursively (5 top subfolders; spellings
verified on disk, not assumed). Classification per doc:

### Already-consumed corpora (prior releases — NO re-translation)

| Source | Prior release | Status |
|---|---|---|
| `OTHER SKIILS/` — Joey banana-pro-director + cinema-worldbuilder (V1.0 + V2.0), screenwriter-skill, shotlist-builder | v3.7.5 / v3.7.7 | CONSUMED |
| `ADDITIONAL SKIILS/` — seedance-2-pro-director, Road-to-Cannes Ep1–3 SRT, HACK screenshots | v3.7.7 | CONSUMED |
| `EVEN MORE SKILLS/gpt-image-2-director/SKILL.md` (13KB) | v3.7.16 | CONSUMED (same Adil source) |
| `EVEN MORE SKILLS/MORE CUSTOM SKILLS/static-ads.md` (20KB) | v3.7.16 | CONSUMED (→ static-ads-workflow.md) |
| `EVEN MORE SKILLS/MORE CUSTOM SKILLS/cinematic-motion-language.md` (8KB) | v3.7.15 | CONSUMED (5-pillar → vocab.md) |
| `EVEN MORE SKILLS/marketing-studio-director/SKILL.md` (18KB) | v3.7.13 | CONSUMED — delta check below |

**marketing-studio-director delta verdict: FULLY CONSUMED.** Line-level delta
analysis vs shipped `skills/higgsfield-marketing-studio/SKILL.md` (50KB) found
zero load-bearing net-new. The only literally-absent items (antislop word list,
age-blind rule one-liner, `<<<image_n>>>` paste syntax, hardcoded generate link)
are either generic prose-hygiene, output-contract conventions specific to the
standalone director that the shipped MCP-routing skill deliberately replaced, or
already covered in §3/§5/§8. Shipped §13 already names this file as its v3.7.13
source and cites it by line number throughout. **Ship nothing.**

### Out-of-scope

| Source | Reason |
|---|---|
| `EVEN MORE SKILLS/MORE CUSTOM SKILLS/ad-creative.md` (14KB) | **Generic, non-Higgsfield.** References `paid-ads`, `copywriting`, `tools/REGISTRY.md`, Anthropic growth team. A different skill ecosystem; only one incidental Higgsfield mention. Not a Higgsfield source-of-truth. DROP. |
| `EVEN MORE SKILLS/higgsfield-content-factory 2/SKILL.md` | Byte-identical duplicate of `higgsfield-content-factory/SKILL.md` (`diff -q` → identical). Use the canonical one. |
| LEARNING HUB generic/duplicate PDFs (handbook restatements, AI prompting handbooks, ONESHOT/UNDERNEATH-THE-CHAOS, Cinematic-Universe/Script-to-System cluster, Seedance handbook/prompt-modes/serious-examples) | ALREADY-COVERED or GENERIC. See § VERIFY 0.4. |

### Net-new sources (this release)

| Source | Surface | Size | Maps to |
|---|---|---|---|
| `EVEN MORE SKILLS/higgsfield-content-factory/SKILL.md` | Marketing Studio 5-stage campaign orchestration (Adil) | 55KB / 997 lines | NEW sub-skill |
| `CANVAS/canvas-based AI production studio.pdf` + 6 CANVAS pngs + 5 EXTRA VIEWS + `higgsfield.ai/canvas-intro` (web) | Canvas node-based workspace + Shared Canvas | PDF 4p + 11 imgs + web | NEW sub-skill |
| `higgsfield.ai/chat-intro` + Team-Plans blog (web) | Higgsfield Collab (collaboration space) | web | §-expansion (workspaces) |
| `LEARNING HUB/Reference Workflow_.pdf` + `LEARNING HUB/PRODUCT REFERENCE SHEET PROMPTS.txt` | Automatic Product Reference Sheet + Automatic Prompt Creator + Video References | 9p + 16KB | NEW satellite (gpt-image-2) + §-expansion (seedance) |
| `OTHER SKIILS/Fotachu/Workflow Fotachu - …anime…md` | Anime-animation Seedance workflow (Fotachu / CPP) | 16KB | NEW template |
| `LEARNING HUB/Kling Motion Control.pdf` | Kling Motion Control 3.0 deltas | 5p | §-expansion (motion) |
| `LEARNING HUB/Power User @madmax6xx.pdf` | Manual multi-pass character-sheet build | 16p | DROP — already covered by soul § Character Sheet Creation (assessed marginal) |

---

## VERIFY 0.2 — Coverage matrix vs 23 sub-skills + root refs

| Surface | Repo state | Action |
|---|---|---|
| Marketing Studio video (presets/params) | COVERED — higgsfield-marketing-studio | — |
| Marketing Studio **campaign orchestration** (research→plan→generate→publish→report) | **MISSING** — repo pre-reserved the name (`marketing-studio/SKILL.md:43` names content-factory as "what orchestrates MS programmatically"); v3.7.13 explicitly deferred the 5-stage pipeline | **NEW sub-skill higgsfield-content-factory** |
| Canvas (node workspace) | **MISSING** — only an incidental "Coming in Assist: Canvas" line | **NEW sub-skill higgsfield-canvas** |
| Shared Canvas (live link collab) | MISSING / was-deferred G15a | Section in canvas sub-skill |
| Collab (projects/chat/calls) | MISSING / was-deferred G15b | §-expansion higgsfield-workspaces |
| Product reference sheet (1-img→multi-view + identity-lock prompt) | PARTIAL — "reference sheet" named in gpt-image-2 but no how-to/prompt scaffold | **NEW satellite reference-sheet-workflow.md** |
| Video references (@video_1 world/camera carryover) | PARTIAL — reference roles named in seedance/cinema, no read-reliably/not contract | §-expansion higgsfield-seedance |
| Kling Motion Control 3.0 | COVERED (motion § Kling 3.0 Motion Control) — deltas only | §-expansion: Matches Video/Image binding, element binding, shorter-output diagnostic, motion library |
| Anime-animation Seedance genre | MISSING as a template | **NEW template templates/seedance/anime-animation.md** |
| Character sheet (manual multi-pass) | COVERED — soul § Character Sheet Creation + Anchor Block + Multi-Form | DROP (marginal) |

---

## VERIFY 0.3 — Backlog forward (implementable-now vs blocked)

### Implementable now

- **T5 — `seedance_lint.py` expansion.** Add (a) bracket-notation `[0-2s]` /
  `【镜头N】`-style syntax check, (b) NSFW false-positive heuristic (provider-side
  flag risk words), (c) GREAT-tier photographer-vocabulary suggestion table.
  No external dependency. SHIP.
- **MD060 — table-style harmonization.** `.markdownlint.json` exists
  (`default:true`, disables MD013/MD022/MD032, configs MD024). ~50+ repo tables
  use mixed leading/trailing-pipe + separator-spacing styles. **Decision:**
  record the convention via config rather than reformatting 50+ files (huge
  byte-churn, zero functional value, baseline-rotation risk). Add `"MD060":
  false` to record "mixed pipe-style accepted as known stylistic preference"
  (the backlog's "config disable" option). SHIP as config decision.
- **USER-GUIDE.pdf dynamic-content refactor (v3.7.8 concern).** **RESOLVED by
  the v3.7.16 dict-parity gate** — `generate_user_guide.py:97 discover_sub_skills()`
  filesystem-walks `skills/*/SKILL.md` and the dict-parity check (exit 3) FAILS
  the build if `SUB_SKILL_DESCRIPTIONS` drifts from the filesystem. Net-new
  surfaces can no longer silently fail to propagate — the gate forces an entry.
  Remaining hardcoded piece (curated short descriptions) is an intentional
  design choice (module docstring L5–6: descriptions "NOT extracted from
  frontmatter"). Action this release: add the 3 new sub-skill dict entries
  (canvas, content-factory) — wait, 2 — and document the resolution. No risky
  frontmatter-extraction refactor.
- **G13 — Seedance `【镜头N】` block syntax.** Resolved-by-absence across 4 audit
  surfaces (3h47m SRT + 16 slides + 604-line skill). The WORKING FOLDER corpus
  adds a 5th surface of absence (zero hits across content-factory, Reference
  Workflow, Seedance handbooks, Fotachu). **DROP from active backlog** as
  RESOLVED-BY-ABSENCE; the T5 linter's bracket-notation check covers the
  community-delimiter case if any user uses it. No standalone doc.
- **T1 / T4** — no working-folder demand signal surfaced. Remain backlog.

### Web-research resolved (were "likely blocked")

Per the non-negotiable rule (search Higgsfield source-of-truth before flagging
blocked), the following were resolved against official Higgsfield pages:

- **G15a Shared Canvas — UNBLOCKED.** `higgsfield.ai/canvas-intro`: Canvas
  offers "real-time team collaboration" via shared links — "work live, the same
  way they would in Figma; multiple people can drop nodes, chain pipelines, and
  generate at the same time; versions save automatically; comments stay attached
  to the specific nodes they reference." Ship as a Canvas sub-skill section.
- **G15b Collab — UNBLOCKED.** `higgsfield.ai/chat-intro` + Team-Plans blog:
  "Higgsfield Collab is a built-in collaboration space — shared projects, chat
  in real time, voice and video calls, share generations, discover community
  work." Project access levels (private/public/open), "Share to Collab" toggle
  (sends generation to project chat with prompt/model/progress), persistent call
  bar, Orgs/Team Plans (shared credits/elements, admin, SSO), karma→credits.
  Ship as a workspaces §-expansion.

### Still blocked → NEEDS PETER

- **G15c Hixie.** No source — neither the WORKING FOLDER corpus, the CANVAS
  screenshots, nor web search (`higgsfield.ai`, general) — names "Hixie." The
  Canvas node menu documents a generic **LLM Assistant** node + a
  "cinematographer-prompter" LLM role (EXTRA VIEWS screenshot + canvas PDF), but
  no entity named "Hixie." Needs Peter to confirm the feature/name exists before
  it can be documented. The generic LLM-Assistant-node capability IS documented
  in the new Canvas sub-skill.
- **G1 Soul Cinema two-step compositing.** UI-flow verification (does Soul Cinema
  accept the two reference uploads in the documented order and reliably produce a
  character-with-outfit composite). Web search does not surface authoritative
  step-order docs; this needs hands-on UI verification. Remains deferred.

---

## VERIFY 0.4 — LEARNING HUB PDF triage (20 PDFs)

Sampled each (intro + TOC + representative pages). Result:

- **NET-NEW (3):** Kling Motion Control 3.0 (deltas only — motion already has a
  section), Reference Workflow (Automatic Product Reference Sheet + Automatic
  Prompt Creator + Video References), Power User manual character-sheet build
  (assessed marginal vs existing soul coverage → DROP).
- **ALREADY-COVERED:** Seedance 2.0 Handbook, Seedance Prompt Modes &
  Framework, Seedance Serious Examples Supplement (all 5 modes + runtime
  arithmetic already in seedance), Nano Banana Pro/2 guides (image-models.md),
  HiggsfieldToolsGuide (apps/audio/workspaces), Cinema Studio 3.0 Handbook /
  CS3 Doc / CinemaStudioRecap (~90% redundant with higgsfield-cinema; the
  Recap deck is 3.5-branded and already covered), Scene-First / Cinematic-
  Universe / Script-to-System cluster (screenwriter/shotlist/cinema-worldbuilder
  + seedance Working Modes).
- **GENERIC / DUPLICATE:** AI prompting handbooks (cross-model, self-described
  as platform-layer-only), ONESHOT / UNDERNEATH THE CHAOS (iterative-workflow
  philosophy already in DISCIPLINE.md), `Seedance Promt modes.pdf` (earlier
  draft of the framework deck), `article nano (2).pdf` (dup of NBP deck), the
  three Cinematic-Universe/Script-to-System duplicate pairs.

The **Cinema Studio 3.0/Canvas** investigation confirmed Canvas is a distinct
top-level product surface (parallel to Cinema Studio in the nav bar), not a mode
of Cinema Studio — driving the new-sub-skill choice over a cinema §-expansion.

---

## VERIFY 0.5 — Architecture options per net-new surface

Following the marketing-studio + cross-surface-workflow.md precedent
(parent SKILL.md + satellite). Source-hit counts drive each choice.

### Canvas → NEW sub-skill `skills/higgsfield-canvas/`
- α new sub-skill / β §-expansion of higgsfield-cinema / γ satellite under cinema.
- **LOCK α.** Canvas is its own nav-bar product hosting ALL models (Soul,
  Seedance, Kling, Wan, Veo, GPT Image 2, Nano Banana Pro — 7 confirmed); it is
  cross-cutting and references cinema/soul/seedance, not a child of any. Repo
  coverage = 0 ("Meta Ads"/"node-based"/"Canvas-as-surface" → zero skill hits).
  ~160–190 lines incl. Shared Canvas section. G15a re-scoped "Shared Canvas" →
  "Canvas (node workspace) + sharing".

### Content-factory → NEW sub-skill `skills/higgsfield-content-factory/` + satellite
- α new sub-skill+satellite / β §-expansion of marketing-studio / γ satellite under MS.
- **LOCK α.** Repo pre-reserved the name (`marketing-studio/SKILL.md:43`);
  v3.7.13 deferred the 5-stage pipeline explicitly. MS is the *engine reference*;
  content-factory is the *orchestration pipeline that calls it*. Parent carries
  the pipeline spine (5-format taxonomy, onboarding, Stages 1–3, hard rules);
  satellite `publish-and-report-workflow.md` isolates the most-speculative tail
  (Stage 4 Meta Ads + Stage 5 cost report) so heavy DO-NOT-WRITE caveats live in
  one place. Source-hit counts: `Meta` 27, `AskUserQuestion` 24, `ASMR` 24,
  `cost` 18, `floor(VIDEO_COUNT` 6, `Stage 5` 7; cross-repo `"Meta Ads"`/`"cost
  comparison"` → 0 skill hits (genuinely net-new). ~420 parent + ~200 satellite.

### Reference-sheet workflow → NEW satellite `skills/higgsfield-gpt-image-2/reference-sheet-workflow.md`
- **LOCK satellite.** Mirrors gpt-image-2 + static-ads-workflow.md precedent.
  Product reference sheets are a static-image production pattern adjacent to
  static-ads; the verbatim GLOBAL IDENTITY LOCK template + Automatic Prompt
  Creator meta-prompt + worked hat/dress examples (from the `.txt`) are
  preserved verbatim with bracketed placeholders. ~180–220 lines.

### Video references → §-expansion `skills/higgsfield-seedance/`
- **LOCK §-expansion.** Reference roles already named in seedance §245; this
  adds the @video_1 read-reliably / read-less-reliably contract + per-intent
  reference syntax + "cannot continue frame-accurate / cannot override prompt /
  cannot supply identity alone" limits. ~30–40 lines.

### Collab → §-expansion `skills/higgsfield-workspaces/`
- **LOCK §-expansion.** Collab is the team/surface collaboration layer;
  workspaces is the task-first surface decision layer — natural home. New
  `### Higgsfield Collab` under Workspace Descriptions. ~35–45 lines.

### Kling Motion Control → §-expansion `skills/higgsfield-motion/`
- **LOCK §-expansion.** Existing § Kling 3.0 Motion Control already covers the
  8-step workflow + input checklist + resolution + scene source + orientation.
  Net-new deltas only: Matches Video vs Matches Image binding modes, element
  binding (Matches-Video-only), the "output shorter than source = motion too
  fast/complex" diagnostic, motion-library-vs-upload source, close-up-face /
  emotional-transition use cases. ~20 lines.

### Anime-animation → NEW template `templates/seedance/anime-animation.md`
- **LOCK template.** Mirrors the v3.7.7 `templates/seedance/` precedent. Fotachu
  CPP workflow: layered SUBJECT/ENVIRONMENT/ACTION/CAMERA/STYLE formula, verbatim
  anime style block + character-spreadsheet prompt, IP-safe constraints,
  iterative-pass workflow. ~90–120 lines.

---

## VERIFY 0.6 — Version

Current v3.7.16. This release adds **2 new sub-skills** (23→25 — the largest
structural jump in the 3.7 series), 1 new satellite, 1 new template, 4
§-expansions, 3 backlog resolutions, USER-GUIDE regen + baseline rotation. The
sub-skill-count jump + structural scope **warrants a MINOR bump**.

**Proposed: v3.8.0.** (Patch-only convention is for content-refresh releases;
two new top-level surfaces is a minor.) Peter confirms at review.

---

## VERIFY 0.7 — Source-evidence boundary (carried to Phase 1 DO-NOT-WRITE lists)

Highest-risk surfaces (gapped or speculative source):

- **content-factory Stage 4/5** — Meta MCP tool/param names unverified; Stage 5
  traditional-cost dollar figures are invented "industry-average estimates"; per-
  credit USD rates approximate. DO-NOT-WRITE these as Higgsfield fact.
- **content-factory known-false API** — `generate_video.mode` slug table
  (`ugc_how_to`/`product_showcase`), nested `avatars` in `params`, `source`
  filter field: all refuted in marketing-studio reconciliations. Never reproduce;
  defer all API ground-truth to higgsfield-marketing-studio.
- **Canvas** — no hard node-count/fan-in limits documented; credit badges are
  "as shown in UI" not fixed pricing; do not invent plan-gating; the
  "cinematographer-prompter" LLM role is a user-authored node prompt, not a named
  built-in; "Hixie" does not exist in any source.
- **Collab** — translate only the documented project access levels, Share-to-
  Collab, calls, Orgs/Team-Plans, karma. No invented limits.

All DO-NOT-WRITE lists are itemized per surface in PHASE-1-INVENTORY.md § 1C.
