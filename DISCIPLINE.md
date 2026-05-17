# Higgsfield Skill Library — Discipline Patterns

## What this is

Cross-cutting discipline patterns observed across the higgsfield
skill library plus the v3.7.5 ecosystem audit (Joey's banana-
pro-director + cinema-worldbuilder; screenwriter-skill;
shotlist-builder). Three tiers: **workflow** (how to author
prompts), **output** (what to emit), **architectural** (how
multi-step work composes). Each pattern points to a concrete
demonstration in higgsfield's existing codebase — observed
practice, not aspirational claims.

For a new sub-skill: check **Tier 1** if it involves multi-step
authoring, **Tier 2** if it produces output, **Tier 3** if it
composes multiple stages. Pick what applies.

## Tier 1 — Workflow Discipline

### Pre-Prompt Confirmation Gate

Confirm intent in short form before composing a long prompt;
when stuck, prefer one narrow question over three open-ended.

**When to apply:** Output longer than a few sentences, or any sub-skill triggering expensive downstream work.

**Demonstrated in:** root `SKILL.md` § Workflow → Full Path —
Production Requests (confirm-before-generating + anti-fragmentation
rule).

### Explicit-Stop Between Phases

Multi-phase workflows don't collapse into one response; each
phase produces an artifact the next phase consumes.

**When to apply:** Stateful loops where intermediate artifacts need user confirmation.

**Demonstrated in:** `skills/higgsfield-pipeline/SKILL.md` §
Pipelines A-E — stage-based artifact handoff; Pipeline Pitfall 1
encodes the don't-skip-ahead rule explicitly.

### Inventory-Extraction Checklist Before Composing

Silently catalog what the user provided — who / where / doing
what / with what camera / mood — before composing.

**When to apply:** Sub-skills authoring prompts from free-form briefs.

**Demonstrated in:** `skills/higgsfield-prompt/SKILL.md` § The
Pre-Prompt Checklist — 5-question inventory before writing.

## Tier 2 — Output Discipline

### Visual-Marker-Only Output Discipline

Describe characters and objects by visible markers (clothing,
build, posture, action, hair), not proper names, age labels, or
unobservable attributes. Visual markers carry across regenerations.

**When to apply:** Any prompt for image or video generation.

**Demonstrated in:** `skills/higgsfield-prompt/SKILL.md` §
Seedance 2.0 Engine Constraints → Age-blind character rule.

### Triple-Redundant Runtime

Runtime appears in title, meta header, and per-shot timing
labels — all three must agree, per-shot labels must sum to total.

**When to apply:** Multi-shot or time-anchored output.

**Demonstrated in:** `skills/higgsfield-seedance/SKILL.md` §
Runtime arithmetic for multi-shot prompts.

### Single-Variable Iteration

Change exactly one variable per regeneration. Multi-variable
iteration makes diagnosis impossible.

**When to apply:** Iteration on close-but-not-right generations.

**Demonstrated in:** `skills/higgsfield-prompt/SKILL.md` § The
Iteration Rule — Change One Variable at a Time + 6-Pass Diagnostic.

## Tier 3 — Architectural Discipline

### 3-Stage Chain / 4-Phase Loop Architectural Pattern

Multi-step production decomposes into named stages where each
stage produces an artifact the next stage consumes. Common shapes:
3-stage chain (character → image → video) or 4-phase loop
(script → assets → blocking → prompts).

**When to apply:** Orchestrating multiple generation stages.

**Demonstrated in:** `skills/higgsfield-pipeline/SKILL.md` § The
Master Production Chain + § Pipelines A-E.

### Closing-Block-Baked-Into-Every-Prompt

A shared text fragment appended to every prompt ensures
cross-prompt consistency. Defined once, applied without
redrafting.

**When to apply:** Multiple prompts share a common closing concern.

**Demonstrated in:** root `SKILL.md` § MANDATORY WORKFLOW step 4
("Append shared negative constraints from
`skills/shared/negative-constraints.md` before delivering any
prompt") + the shared constraints file.

### Strict-Order Workflow with Refusal-to-Skip Phases

Sequential workflows enforce order — Step N+1 can't start until
Step N is approved. Skipping surfaces drift downstream.

**When to apply:** Numbered sequence where each step depends on the prior step's artifact.

**Demonstrated in:** `skills/higgsfield-cinema/SKILL.md` § The
10-Step Cinema Studio 2.5 Workflow.

## Source attribution

Pattern *form* is the v3.7.5 audit contribution, IP-safe per the
audit's pattern-not-text classification. Pattern *demonstration*
is higgsfield's own existing practice.
