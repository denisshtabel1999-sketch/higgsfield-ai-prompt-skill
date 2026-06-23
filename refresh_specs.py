#!/usr/bin/env python3
"""Spec-drift tripwire — Wave C Tier 1 (item 5).

Turns the reactive 30-day staleness WARN in validate.py into a PROACTIVE check:
pull the live model catalog from the Higgsfield CLI, diff it against the
committed `specs/models_explore_snapshot_<date>.json`, and report drift loudly.

WHY THE CLI IS A DETECTOR, NOT A SOURCE OF TRUTH
  `higgsfield model get <id> --json` returns enum VALUES but no parameter
  `description` prose, and that prose is where sync_specs.py reads the
  cross-constraints ("4k only with mode='std'"). So this tool catches the
  high-value drift — new/removed models, enum-option changes (a `resolution`
  gaining `4k` IS visible), default changes, a tracked param vanishing — but it
  CANNOT see a pure cross-constraint prose change when enum membership holds.
  That blind spot is acknowledged and logged, never silently passed.

TWO-TIER MODEL
  Tier 1 (this script, headless): detect drift → tell you WHEN to refresh.
  Tier 2 (unchanged, interactive): a full `models_explore` dump → sync_specs.py,
  the only source with the constraint prose. Human-in-loop, as today.

  This script DETECTS ONLY — it never writes specs, never opens a PR, never
  edits the curated guides. When it reports drift, a human runs Tier 2.

Usage:
  python3 refresh_specs.py                 # check video + image
  python3 refresh_specs.py --type video    # one type
  python3 refresh_specs.py --json          # machine-readable diff

Exit codes (the three states must stay distinguishable — a silent failure would
falsely read as "fresh", which is worse than the reactive WARN we already have):
  0  fresh — no tracked drift
  3  drift detected — run the Tier 2 refresh + audit evals/cases/
  1  pull failed — CLI/auth error (e.g. session expired; run `higgsfield auth login`)
  2  usage error
"""
import argparse
import json
import shutil
import subprocess
import sys

from sync_specs import SPECS_DIR, find_snapshot, snapshot_date

CLI = "higgsfield"
# Snapshot top-level fields that the CLI represents as parameters instead.
_ASPECT_PARAM = "aspect_ratio"


class PullError(RuntimeError):
    """The live pull failed (CLI missing, not authenticated, bad JSON). Kept
    distinct from "drift" so the exit code can stay loud."""


# ── Normalization: snapshot item ↔ CLI `model get`, into one comparable view ──

def _opts(values) -> list:
    return sorted(str(v) for v in (values or []))


def snapshot_view(item: dict) -> dict:
    """Comparable view of one committed-snapshot model (the tracked shape)."""
    return {
        "id": item["id"],
        "output_type": item.get("output_type"),
        "aspect_ratios": _opts(item.get("aspect_ratios")),
        "params": {
            p["name"]: {"options": _opts(p.get("options")),
                        "default": p.get("default")}
            for p in item.get("parameters", [])
        },
    }


def cli_view(get_json: dict) -> dict:
    """Comparable view of one `higgsfield model get` payload. The CLI calls the
    enum list `enum` (snapshot says `options`) and carries aspect ratios as an
    `aspect_ratio` param rather than a top-level field — normalize both away."""
    params = {p["name"]: p for p in get_json.get("params", [])}
    aspect = params.get(_ASPECT_PARAM, {})
    return {
        "id": get_json.get("job_set_type"),
        "output_type": get_json.get("type"),
        "aspect_ratios": _opts(aspect.get("enum")),
        "params": {
            name: {"options": _opts(p.get("enum")), "default": p.get("default")}
            for name, p in params.items()
        },
    }


# ── The diff (pure) ──────────────────────────────────────────────────────────

def diff_model(old: dict, new: dict) -> dict:
    """Classify drift in one model into DRIFT vs NOTICE, comparing only the
    TRACKED params (those the snapshot carries).

    The two sources diverge in DETAIL, not just coverage: the CLI's `model get`
    sometimes returns `enum: null` where the snapshot enumerates options (e.g.
    clipify fonts), and omits some params/models the snapshot has. So a
    capability the snapshot has but the CLI lacks is usually the CLI
    under-reporting, NOT a real withdrawal. The reliable, apples-to-apples
    signal is the OTHER direction: a value the live CLI has that the snapshot
    LACKS — a new capability shipped (the Seedance-4K staleness case). That is
    DRIFT. Removals / missing things are NOTICE: real-or-artifact, Tier 2 to
    confirm. Returns {"drift": [...], "notice": [...]}."""
    drift, notice = [], []
    aspect_added = [a for a in new["aspect_ratios"] if a not in old["aspect_ratios"]]
    aspect_gone = [a for a in old["aspect_ratios"] if a not in new["aspect_ratios"]]
    if aspect_added:
        drift.append({"kind": "aspect_ratios", "added": aspect_added})
    if aspect_gone:
        notice.append({"kind": "aspect_ratios_gone", "removed": aspect_gone})

    for pname, op in old["params"].items():
        np = new["params"].get(pname)
        if np is None:
            notice.append({"kind": "param_missing", "param": pname})
            continue
        # New option only counts when BOTH sides enumerate (else it's the CLI
        # simply not listing options, not a real membership change).
        if op["options"] and np["options"]:
            added = [o for o in np["options"] if o not in op["options"]]
            removed = [o for o in op["options"] if o not in np["options"]]
            if added:
                drift.append({"kind": "options_added", "param": pname, "added": added})
            if removed:
                notice.append({"kind": "options_removed", "param": pname, "removed": removed})
        elif op["options"] != np["options"]:
            notice.append({"kind": "options_undetailed", "param": pname})
        if op["default"] is not None and np["default"] is not None \
                and op["default"] != np["default"]:
            drift.append({"kind": "default", "param": pname,
                          "from": op["default"], "to": np["default"]})
    return {"drift": drift, "notice": notice}


def diff_catalog(old_views: dict, new_views: dict) -> dict:
    """Diff committed-snapshot views (old) against live-CLI views (new).

    Only ADDED capabilities on shared models flip the drift state (high
    confidence, low false-positive — see diff_model). Catalog membership
    differences are NOTICE: the CLI list is a superset on one axis (utility
    jobs) and a subset on another (it omits some models the snapshot tracks),
    so neither `models_added` nor `models_removed` is a reliable alarm."""
    old_ids, new_ids = set(old_views), set(new_views)
    per_model = {}
    for mid in sorted(old_ids & new_ids):
        d = diff_model(old_views[mid], new_views[mid])
        if d["drift"] or d["notice"]:
            per_model[mid] = d
    return {
        "models_changed": per_model,
        "models_removed": sorted(old_ids - new_ids),   # notice
        "models_added": sorted(new_ids - old_ids),      # notice
    }


def has_drift(diff: dict) -> bool:
    """Drift = a live ADDED capability on a tracked model. Catalog membership
    and any removal/under-detail are notices, not drift."""
    return any(m["drift"] for m in diff["models_changed"].values())


# ── The live pull (impure — isolated so the diff stays unit-testable) ─────────

def _cli_json(args: list) -> object:
    if shutil.which(CLI) is None:
        raise PullError(f"`{CLI}` CLI not found on PATH (brew install higgsfield-ai/tap/higgsfield)")
    proc = subprocess.run([CLI, *args, "--json"], capture_output=True, text=True)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip().splitlines()
        hint = err[0] if err else f"exit {proc.returncode}"
        raise PullError(f"`{CLI} {' '.join(args)}` failed: {hint}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise PullError(f"`{CLI} {' '.join(args)}` returned non-JSON: {e}")


def pull_cli_views(output_type: str, tracked_ids: set) -> tuple:
    """Live CLI views for every tracked id present in the catalog, plus the set
    of all catalog ids (so new/untracked models can be noticed). N+1 calls: one
    `model list`, one `model get` per tracked model present."""
    catalog = _cli_json(["model", "list", f"--{output_type}"])
    catalog_ids = {m["job_set_type"]: m.get("display_name", m["job_set_type"])
                   for m in catalog}
    views = {}
    for mid in sorted(tracked_ids & set(catalog_ids)):
        views[mid] = cli_view(_cli_json(["model", "get", mid]))
    return views, catalog_ids


# ── Report + driver ──────────────────────────────────────────────────────────

def render(output_type: str, snap_date: str, diff: dict, catalog_ids: dict,
           verbose: bool = False) -> str:
    lines = [f"[{output_type}] snapshot {snap_date} vs live CLI catalog"]
    for mid, d in diff["models_changed"].items():
        for c in d["drift"]:
            if c["kind"] == "options_added":
                lines.append(f"  ⚠ DRIFT — {mid}.{c['param']} gained {'/'.join(c['added'])}")
            elif c["kind"] == "aspect_ratios":
                lines.append(f"  ⚠ DRIFT — {mid} aspect_ratios gained {'/'.join(c['added'])}")
            elif c["kind"] == "default":
                lines.append(f"  ⚠ DRIFT — {mid}.{c['param']} default "
                             f"{c['from']!r} → {c['to']!r}")
    if not has_drift(diff):
        lines.append("  ✓ no tracked drift (no new live capability the snapshot lacks)")

    # Notices: real-or-artifact, surfaced for review, never flip the exit code.
    notices = []
    if diff["models_removed"]:
        notices.append(f"snapshot models absent from CLI catalog: "
                       f"{', '.join(diff['models_removed'])}")
    if diff["models_added"]:
        notices.append(f"CLI catalog models not in snapshot (new or utility): "
                       f"{', '.join(diff['models_added'])}")
    n_model_notices = sum(len(d["notice"]) for d in diff["models_changed"].values())
    if verbose:
        for mid, d in diff["models_changed"].items():
            for c in d["notice"]:
                notices.append(f"{mid}: {c['kind']} "
                               f"{c.get('param', '') or '/'.join(c.get('removed', []))}".strip())
    elif n_model_notices:
        notices.append(f"{n_model_notices} param-level note(s) (CLI under-detail / "
                       f"removals) — rerun with --verbose to list")
    for n in notices:
        lines.append(f"  · {n}")
    return "\n".join(lines)


def check_type(output_type: str, verbose: bool = False) -> tuple:
    """Returns (report_text, diff_dict). Raises PullError on a failed pull."""
    snap_path = find_snapshot(output_type=output_type)
    snapshot = json.loads(snap_path.read_text(encoding="utf-8"))
    old_views = {m["id"]: snapshot_view(m)
                 for m in snapshot.get("items", [])
                 if m.get("output_type") == output_type}
    new_views, catalog_ids = pull_cli_views(output_type, set(old_views))
    diff = diff_catalog(old_views, new_views)
    return render(output_type, snapshot_date(snap_path), diff, catalog_ids, verbose), diff


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="refresh_specs.py", description=__doc__.splitlines()[0])
    p.add_argument("--type", choices=("video", "image", "both"), default="both")
    p.add_argument("--json", action="store_true", help="machine-readable diff")
    p.add_argument("--verbose", action="store_true", help="list every param-level notice")
    args = p.parse_args(argv)
    types = ("video", "image") if args.type == "both" else (args.type,)

    reports, diffs, drift = [], {}, False
    for t in types:
        try:
            text, diff = check_type(t, verbose=args.verbose)
        except PullError as e:
            print(f"PULL FAILED [{t}]: {e}", file=sys.stderr)
            print("  → not fresh, not drift — the live state is unknown. "
                  "If the session expired, run: higgsfield auth login", file=sys.stderr)
            return 1
        except FileNotFoundError as e:
            print(f"NO SNAPSHOT [{t}]: {e}", file=sys.stderr)
            return 1
        reports.append(text)
        diffs[t] = diff
        drift = drift or has_drift(diff)

    if args.json:
        print(json.dumps(diffs, indent=2))
    else:
        print("\n".join(reports))
        if drift:
            print("\nDRIFT DETECTED → refresh the snapshot (Tier 2): dump "
                  "`models_explore`, run `python3 sync_specs.py`, AND audit "
                  "`evals/cases/` in the same PR (a spec change silently stales "
                  "eval traps — see v3.11.2/v3.11.3).")
        else:
            print("\nFresh. (Tier-1 blind spot: a cross-constraint prose change "
                  "with no enum movement is invisible here — Tier 2 is authoritative.)")
    return 3 if drift else 0


if __name__ == "__main__":
    sys.exit(main())
