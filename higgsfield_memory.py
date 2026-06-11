#!/usr/bin/env python3
"""
higgsfield_memory.py
====================
Database read/write operations for the Higgsfield learning memory system.
Called by Claude Cowork via the higgsfield-recall skill.

Usage:
  python higgsfield_memory.py add-filter <json_entry>
  python higgsfield_memory.py add-quality <json_entry>
  python higgsfield_memory.py query-filter <search_terms>
  python higgsfield_memory.py query-quality <search_terms>
  python higgsfield_memory.py update-filter <entry_id> <outcome>
  python higgsfield_memory.py update-quality <entry_id> <outcome> [improved_prompt] [notes]
  python higgsfield_memory.py stats
  python higgsfield_memory.py export-summary
  python higgsfield_memory.py health

Per-project namespacing:
  python higgsfield_memory.py --project <name> <command> ...

  Routes every command to db/projects/<name>-filter-memory.json /
  <name>-quality-memory.json instead of the global databases, so
  production-specific lessons (e.g. one project's dual-instance character
  workaround) don't pollute global memory. Project DBs are created lazily on
  first write; reads from a missing project DB return empty results.
"""

import json
import os
import sys
import re
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
# DB files live alongside the script (sibling directory or same directory).
# The directory is created lazily on first write (see save_db / export_summary),
# not at import time — importing this module should have no filesystem side effects.
# HF_DB_DIR overrides the location (tests point it at a temp dir; works both
# in-process and across subprocess boundaries, unlike monkeypatched constants).
DB_DIR = Path(os.environ["HF_DB_DIR"]) if os.environ.get("HF_DB_DIR") else SCRIPT_DIR / "db"
FILTER_DB = DB_DIR / "filter-memory.json"
QUALITY_DB = DB_DIR / "quality-memory.json"
# Set by the --project CLI option: project-namespaced DBs are created lazily,
# so load_db treats a missing file as empty instead of erroring.
PROJECT_MODE = False

# Allowed outcome values, mirroring the inline documentation on add_filter /
# add_quality. update-* commands validate against these so a typo (e.g.
# "fixedd") can't silently flip every derived boolean to False.
FILTER_OUTCOMES = {"unknown", "fixed", "workaround", "still-blocked"}
QUALITY_OUTCOMES = {"unknown", "improved", "still-failing"}

# ── Helpers ────────────────────────────────────────────────────────────────────

def load_db(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            db = json.load(f)
    except FileNotFoundError:
        if PROJECT_MODE:
            return {"entries": []}
        print(json.dumps({"status": "error", "message": f"Database file not found: {path}"}))
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "message": f"Database file is corrupted: {e}"}))
        sys.exit(1)
    # Guarantee the shape every caller assumes: a dict with a list "entries".
    # A valid-JSON-but-wrong-shape file should fail the clean error contract,
    # not crash later with a raw KeyError/AttributeError traceback.
    if not isinstance(db, dict):
        print(json.dumps({"status": "error", "message": f"Database root is not a JSON object: {path}"}))
        sys.exit(1)
    entries = db.setdefault("entries", [])
    if not isinstance(entries, list):
        print(json.dumps({"status": "error", "message": f"Database 'entries' must be a list: {path}"}))
        sys.exit(1)
    return db

def save_db(path: Path, data: dict):
    data["_last_updated"] = datetime.now(timezone.utc).isoformat()
    data["_total_entries"] = len(data["entries"])
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp_path.replace(path)  # atomic on POSIX, best-effort on Windows
    except OSError as e:
        tmp_path.unlink(missing_ok=True)
        print(json.dumps({"status": "error", "message": f"Failed to save database: {e}"}))
        sys.exit(1)

def next_id(entries: list, prefix: str) -> str:
    if not entries:
        return f"{prefix}-001"
    # Only count ids whose suffix is purely numeric. A hand-edited id like
    # "F-abc" (or any non-numeric suffix) is skipped rather than crashing the
    # whole add command with an uncaught ValueError.
    nums = []
    for e in entries:
        eid = e.get("id", "")
        if not eid.startswith(prefix):
            continue
        suffix = eid.split("-")[-1]
        if suffix.isdigit():
            nums.append(int(suffix))
    return f"{prefix}-{(max(nums) + 1):03d}" if nums else f"{prefix}-001"

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def tokenize(text: str) -> set:
    """Tokenizer for relevance matching. Preserves hyphenated phrases as whole tokens
    in addition to their individual parts (e.g. 'real-person' → {'real-person','real','person'})."""
    lower = text.lower()
    tokens = set(re.findall(r'\b[\w-]+\b', lower))  # includes hyphenated phrases
    # also add individual words from within hyphenated terms
    for token in list(tokens):
        if '-' in token:
            tokens.update(token.split('-'))
    return tokens

def relevance_score(entry: dict, query_tokens: set) -> int:
    """Score an entry against search tokens. Higher = more relevant."""
    text = " ".join([
        entry.get("failed_prompt", ""),
        entry.get("original_prompt", ""),
        entry.get("topic", ""),
        entry.get("error_message", ""),
        entry.get("failure_description", ""),
        entry.get("category", ""),
        " ".join(entry.get("tags", [])),
        " ".join(entry.get("blocked_terms", [])),
    ]).lower()
    entry_tokens = tokenize(text)
    return len(query_tokens & entry_tokens)


# ── Generation Ledger ──────────────────────────────────────────────────────────
# Empirical hit-rate system (Brief #3). Unlike the filter/quality memories
# (failure ledgers), this logs EVERY generation attempt — kept, rejected, or
# filter-flagged — so takes-per-kept ratios have a denominator. Rows are
# APPEND-ONLY: corrections are new rows with `supersedes`, never edits.
# Full schema + vocabulary docs: db/ledger/README.md.

LEDGER_DIR = DB_DIR / "ledger"
GLOBAL_LEDGER = LEDGER_DIR / "_global.json"
PROJECT_NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
GEN_ID_RE = re.compile(r"^(.+)-(\d{4})$")

# Controlled vocabularies (extend via PR, never ad hoc — free-text tags
# fragment and kill aggregation).
SHOT_TAGS = {
    "establishing", "dialogue-cu", "dialogue-multi", "action-melee",
    "action-chase", "insert-prop", "vfx-event", "two-char",
    "multi-char-3plus", "dual-instance", "pov", "environment-only",
    "creature-occluded",
}
REJECT_REASONS = {
    "identity-drift", "wardrobe-contamination", "extra-cuts",
    "blocking-broken", "performance", "camera-wrong", "physics",
    "text-render", "filter-flagged", "composition", "other",
}
# The split that carries the diagnostic value: structural rejections mean
# "fix the prompt, don't re-roll"; stochastic mean "re-roll territory".
# `other` belongs to neither class (counts in n only).
STRUCTURAL_REASONS = {"identity-drift", "wardrobe-contamination", "extra-cuts",
                      "blocking-broken", "text-render", "filter-flagged"}
STOCHASTIC_REASONS = {"performance", "camera-wrong", "physics", "composition"}
OUTCOMES = {"kept", "rejected", "flagged"}

# Default planning ratios for budget estimates when the ledger has no usable
# data for a tag (n<5 or kept=0). These are DEFAULTS, NOT DATA — the brief's
# documented planning bands: 2-3:1 simple, 4-6:1 complex (midpoints used).
DEFAULT_RATIOS = {
    "establishing": 2.5, "dialogue-cu": 2.5, "insert-prop": 2.5,
    "environment-only": 2.5, "pov": 2.5,
    "dialogue-multi": 5.0, "action-melee": 5.0, "action-chase": 5.0,
    "vfx-event": 5.0, "multi-char-3plus": 5.0, "dual-instance": 5.0,
    "creature-occluded": 5.0,
    "two-char": 3.0,
}
LOW_N_THRESHOLD = 5

_LEDGER_REQUIRED = {"id", "ts", "model", "shot_tags", "outcome", "draft_tier"}
_LEDGER_OPTIONAL = {"mode", "resolution", "aspect", "duration_s", "internal_cuts",
                    "scene_ref", "prompt_hash", "credits", "notes",
                    "supersedes", "reject_reason", "project"}


def load_specs_models() -> dict:
    """{id_or_alias: canonical_id} from specs/model-specs.json.

    Ledger rows store CANONICAL ids only (aliases resolved at write time) so
    per-model credit averages can't fragment across an alias. Returns {} when
    the specs layer is missing — callers decide whether that's fatal."""
    path = SCRIPT_DIR / "specs" / "model-specs.json"
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    mapping: dict = {}
    for m in spec.get("models", []):
        mapping[m["id"]] = m["id"]
        for alias in m.get("aliases", []):
            mapping[alias] = m["id"]
    return mapping


def ledger_path(project: str) -> Path:
    if not PROJECT_NAME_RE.fullmatch(project):
        print(json.dumps({"status": "error",
                          "message": f"Invalid project name: {project!r} "
                                     "(alphanumeric, dash, underscore)"}))
        sys.exit(1)
    return LEDGER_DIR / f"{project}.json"


def load_ledger(path: Path) -> dict:
    """Ledger file shape: {project, _last_updated, _total_rows, rows}.
    A missing file is an empty ledger (projects bootstrap on first write)."""
    try:
        db = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"project": path.stem, "rows": []}
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({"status": "error",
                          "message": f"Ledger file unreadable: {path}: {e}"}))
        sys.exit(1)
    if not isinstance(db, dict) or not isinstance(db.get("rows", []), list):
        print(json.dumps({"status": "error",
                          "message": f"Ledger file malformed (need dict with rows list): {path}"}))
        sys.exit(1)
    db.setdefault("project", path.stem)
    db.setdefault("rows", [])
    return db


def save_ledger(path: Path, db: dict):
    db["_last_updated"] = now_iso()
    db["_total_rows"] = len(db["rows"])
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        tmp_path.replace(path)
    except OSError as e:
        tmp_path.unlink(missing_ok=True)
        print(json.dumps({"status": "error", "message": f"Failed to save ledger: {e}"}))
        sys.exit(1)


def next_gen_id(project: str, rows: list) -> str:
    nums = []
    for r in rows:
        m = GEN_ID_RE.match(r.get("id", ""))
        if m and m.group(1) == project:
            nums.append(int(m.group(2)))
    return f"{project}-{(max(nums) + 1) if nums else 1:04d}"


def validate_ledger_row(row: dict, project: str, prior_ids: set,
                        superseded_ids: set, model_ids: dict) -> list:
    """Schema check for one row. Returns a list of problem strings.

    `prior_ids` = ids of rows EARLIER in the same file (supersedes may only
    point backward); `superseded_ids` = ids already masked by an earlier
    row's supersedes (each id is maskable at most once — amend an amendment
    by superseding the previous amendment, never the original twice)."""
    problems = []
    rid = row.get("id", "?")

    missing = _LEDGER_REQUIRED - set(row)
    if missing:
        problems.append(f"{rid}: missing required field(s): {', '.join(sorted(missing))}")
    unknown = set(row) - _LEDGER_REQUIRED - _LEDGER_OPTIONAL
    if unknown:
        problems.append(f"{rid}: unknown field(s): {', '.join(sorted(unknown))}")

    m = GEN_ID_RE.match(str(row.get("id", "")))
    if not m or m.group(1) != project:
        problems.append(f"{rid}: id must match '{project}-NNNN'")

    outcome = row.get("outcome")
    if outcome not in OUTCOMES:
        problems.append(f"{rid}: outcome must be one of {sorted(OUTCOMES)}, got {outcome!r}")

    tags = row.get("shot_tags")
    if not isinstance(tags, list):
        problems.append(f"{rid}: shot_tags must be a list")
    else:
        bad = [t for t in tags if t not in SHOT_TAGS]
        if bad:
            problems.append(f"{rid}: shot_tags not in vocabulary: {', '.join(bad)} "
                            f"(allowed: {', '.join(sorted(SHOT_TAGS))})")
        lo = 0 if outcome == "flagged" else 1
        if not lo <= len(tags) <= 3:
            problems.append(f"{rid}: shot_tags needs {lo}..3 entries, got {len(tags)}")

    model = row.get("model")
    if model_ids:
        if model not in model_ids:
            problems.append(f"{rid}: model {model!r} not in specs/model-specs.json")
        elif model_ids[model] != model:
            problems.append(f"{rid}: model {model!r} is an alias — store the "
                            f"canonical id {model_ids[model]!r}")

    if outcome == "rejected":
        reason = row.get("reject_reason")
        if reason not in REJECT_REASONS:
            problems.append(f"{rid}: rejected rows need reject_reason from "
                            f"{', '.join(sorted(REJECT_REASONS))}; got {reason!r}")
    elif row.get("reject_reason") is not None and outcome in OUTCOMES:
        problems.append(f"{rid}: reject_reason only belongs on rejected rows")

    if not isinstance(row.get("draft_tier"), bool):
        problems.append(f"{rid}: draft_tier must be true/false")

    sup = row.get("supersedes")
    if sup is not None:
        if sup not in prior_ids:
            problems.append(f"{rid}: supersedes {sup!r} — no earlier row with that "
                            "id in this ledger (corrections point backward, same file)")
        elif sup in superseded_ids:
            problems.append(f"{rid}: supersedes {sup!r} which is already superseded — "
                            "amend the latest amendment instead")
    return problems


def resolve_effective(rows: list) -> list:
    """Append-only resolution: a row referenced by any supersedes is masked."""
    masked = {r.get("supersedes") for r in rows if r.get("supersedes")}
    return [r for r in rows if r.get("id") not in masked]


def project_ledger_files() -> list:
    """All real project ledgers. Underscore-prefixed names are reserved
    (_global generated view, _demo test fixture) and excluded."""
    if not LEDGER_DIR.is_dir():
        return []
    return sorted(p for p in LEDGER_DIR.glob("*.json")
                  if not p.name.startswith("_"))


def build_global() -> dict:
    """The _global.json view: raw rows from every project ledger, each
    annotated with its project. Generated, never hand-written; consumers
    re-run supersedes resolution (ids are project-prefixed, so masks
    cannot cross projects). Deterministic: filename order, then file order."""
    rows = []
    sources = []
    for path in project_ledger_files():
        db = load_ledger(path)
        sources.append(path.name)
        for r in db["rows"]:
            rows.append({**r, "project": db["project"]})
    return {
        "_generated": "by higgsfield_memory.py — DO NOT HAND-EDIT; "
                      "underscore-prefixed ledgers are excluded by design",
        "generated_from": sources,
        "_total_rows": len(rows),
        "rows": rows,
    }


def write_global():
    fresh = build_global()
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    tmp = GLOBAL_LEDGER.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(fresh, f, indent=2, ensure_ascii=False)
        tmp.replace(GLOBAL_LEDGER)
    except OSError as e:
        tmp.unlink(missing_ok=True)
        print(json.dumps({"status": "error", "message": f"Failed to write _global: {e}"}))
        sys.exit(1)

# ── Commands ───────────────────────────────────────────────────────────────────

def add_filter(entry_json: str):
    """Add a content filter block entry."""
    db = load_db(FILTER_DB)
    try:
        entry = json.loads(entry_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "message": f"Invalid JSON: {e}"}))
        return

    # Required fields with defaults
    entry.setdefault("id", next_id(db["entries"], "F"))
    entry.setdefault("date_added", now_iso())
    entry.setdefault("outcome", "unknown")       # unknown | fixed | workaround | still-blocked
    entry.setdefault("fix_confirmed", False)
    entry.setdefault("tags", [])
    entry.setdefault("blocked_terms", [])        # specific words/phrases that triggered the block
    entry.setdefault("substitution", None)        # what was used instead
    entry.setdefault("substitution_worked", None) # True | False | None (untested)
    entry.setdefault("notes", "")

    db["entries"].append(entry)
    save_db(FILTER_DB, db)
    print(json.dumps({"status": "ok", "id": entry["id"], "total": len(db["entries"])}))


def add_quality(entry_json: str):
    """Add a quality failure entry."""
    db = load_db(QUALITY_DB)
    try:
        entry = json.loads(entry_json)
    except json.JSONDecodeError as e:
        print(json.dumps({"status": "error", "message": f"Invalid JSON: {e}"}))
        return

    entry.setdefault("id", next_id(db["entries"], "Q"))
    entry.setdefault("date_added", now_iso())
    entry.setdefault("outcome", "unknown")        # unknown | improved | still-failing
    entry.setdefault("fix_confirmed", False)
    entry.setdefault("tags", [])
    entry.setdefault("model_used", None)
    entry.setdefault("improved_prompt", None)     # the prompt that fixed it
    entry.setdefault("improvement_confirmed", None)
    entry.setdefault("notes", "")

    db["entries"].append(entry)
    save_db(QUALITY_DB, db)
    print(json.dumps({"status": "ok", "id": entry["id"], "total": len(db["entries"])}))


def query_filter(search_terms: str, top_n: int = 5):
    """Return top N most relevant filter entries for the given search terms."""
    db = load_db(FILTER_DB)
    if not db["entries"]:
        print(json.dumps({"results": [], "total_in_db": 0}))
        return

    query_tokens = tokenize(search_terms)
    scored = [(relevance_score(e, query_tokens), e) for e in db["entries"]]
    scored.sort(key=lambda x: (x[0], x[1].get("date_added", "")), reverse=True)

    results = [e for score, e in scored if score > 0][:top_n]
    print(json.dumps({
        "results": results,
        "total_in_db": len(db["entries"]),
        "query": search_terms
    }, indent=2))


def query_quality(search_terms: str, top_n: int = 5):
    """Return top N most relevant quality entries for the given search terms."""
    db = load_db(QUALITY_DB)
    if not db["entries"]:
        print(json.dumps({"results": [], "total_in_db": 0}))
        return

    query_tokens = tokenize(search_terms)
    scored = [(relevance_score(e, query_tokens), e) for e in db["entries"]]
    scored.sort(key=lambda x: (x[0], x[1].get("date_added", "")), reverse=True)

    results = [e for score, e in scored if score > 0][:top_n]
    print(json.dumps({
        "results": results,
        "total_in_db": len(db["entries"]),
        "query": search_terms
    }, indent=2))


def update_filter(entry_id: str, outcome: str, notes: str = ""):
    """Update the outcome of a filter entry after testing a substitution."""
    if outcome not in FILTER_OUTCOMES:
        print(json.dumps({"status": "error",
                          "message": f"Invalid outcome '{outcome}'. Expected one of: {sorted(FILTER_OUTCOMES)}"}))
        return
    db = load_db(FILTER_DB)
    for entry in db["entries"]:
        if entry.get("id") == entry_id:
            entry["outcome"] = outcome
            entry["fix_confirmed"] = outcome in ("fixed", "workaround")
            entry["substitution_worked"] = outcome == "fixed"
            if notes:
                entry["notes"] = notes
            entry["date_updated"] = now_iso()
            save_db(FILTER_DB, db)
            print(json.dumps({"status": "ok", "id": entry_id, "outcome": outcome}))
            return
    print(json.dumps({"status": "error", "message": f"Entry {entry_id} not found"}))


def update_quality(entry_id: str, outcome: str, improved_prompt: str = "", notes: str = ""):
    """Update the outcome of a quality entry after testing an improved prompt."""
    if outcome not in QUALITY_OUTCOMES:
        print(json.dumps({"status": "error",
                          "message": f"Invalid outcome '{outcome}'. Expected one of: {sorted(QUALITY_OUTCOMES)}"}))
        return
    db = load_db(QUALITY_DB)
    for entry in db["entries"]:
        if entry.get("id") == entry_id:
            entry["outcome"] = outcome
            entry["fix_confirmed"] = outcome == "improved"
            entry["improvement_confirmed"] = outcome == "improved"
            if improved_prompt:
                entry["improved_prompt"] = improved_prompt
            if notes:
                entry["notes"] = notes
            entry["date_updated"] = now_iso()
            save_db(QUALITY_DB, db)
            print(json.dumps({"status": "ok", "id": entry_id, "outcome": outcome}))
            return
    print(json.dumps({"status": "error", "message": f"Entry {entry_id} not found"}))


def stats():
    """Print summary statistics for both databases."""
    f_db = load_db(FILTER_DB)
    q_db = load_db(QUALITY_DB)

    f_entries = f_db["entries"]
    q_entries = q_db["entries"]

    f_fixed = sum(1 for e in f_entries if e.get("fix_confirmed"))
    f_unknown = sum(1 for e in f_entries if e.get("outcome") == "unknown")

    q_fixed = sum(1 for e in q_entries if e.get("fix_confirmed"))
    q_unknown = sum(1 for e in q_entries if e.get("outcome") == "unknown")

    # Most common filter categories
    categories = {}
    for e in f_entries:
        cat = e.get("category", "uncategorized")
        categories[cat] = categories.get(cat, 0) + 1

    print(json.dumps({
        "filter_memory": {
            "total_entries": len(f_entries),
            "fixes_confirmed": f_fixed,
            "still_unknown": f_unknown,
            "last_updated": f_db.get("_last_updated"),
            "categories": categories
        },
        "quality_memory": {
            "total_entries": len(q_entries),
            "improvements_confirmed": q_fixed,
            "still_unknown": q_unknown,
            "last_updated": q_db.get("_last_updated")
        }
    }, indent=2))


def build_summary() -> str:
    """Render the markdown summary of both databases (no file writes).

    Split out from export_summary so validate.py can compare a fresh render
    against db/memory-summary.md without side effects."""
    f_db = load_db(FILTER_DB)
    q_db = load_db(QUALITY_DB)

    lines = ["# Higgsfield Memory Summary\n"]
    lines.append(f"Generated: {now_iso()}\n")

    lines.append("\n## Content Filter Memory\n")
    lines.append(f"Total entries: {len(f_db['entries'])}\n")
    for e in f_db["entries"]:
        lines.append(f"\n### {e['id']} — {e.get('category', 'uncategorized')}")
        lines.append(f"- **Date:** {e.get('date_added', 'unknown')}")
        lines.append(f"- **Failed prompt:** {e.get('failed_prompt', '')[:200]}")
        lines.append(f"- **Error:** {e.get('error_message', 'not recorded')}")
        lines.append(f"- **Blocked terms:** {', '.join(e.get('blocked_terms', []))}")
        lines.append(f"- **Substitution:** {e.get('substitution', 'none')}")
        lines.append(f"- **Outcome:** {e.get('outcome', 'unknown')}")
        lines.append(f"- **Notes:** {e.get('notes', '')}")

    lines.append("\n---\n\n## Quality Memory\n")
    lines.append(f"Total entries: {len(q_db['entries'])}\n")
    for e in q_db["entries"]:
        lines.append(f"\n### {e['id']} — {e.get('failure_type', 'unknown')}")
        lines.append(f"- **Date:** {e.get('date_added', 'unknown')}")
        lines.append(f"- **Model:** {e.get('model_used', 'unknown')}")
        lines.append(f"- **Original prompt:** {e.get('original_prompt', '')[:200]}")
        lines.append(f"- **What was wrong:** {e.get('failure_description', '')}")
        lines.append(f"- **Improved prompt:** {e.get('improved_prompt', 'not yet found')[:200]}")
        lines.append(f"- **Outcome:** {e.get('outcome', 'unknown')}")
        lines.append(f"- **Notes:** {e.get('notes', '')}")

    return "\n".join(lines)


def export_summary():
    """Write the markdown summary of both databases to db/memory-summary.md."""
    summary = build_summary()
    DB_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DB_DIR / "memory-summary.md"
    tmp_path = out_path.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(summary)
        tmp_path.replace(out_path)
    except OSError as e:
        tmp_path.unlink(missing_ok=True)
        print(json.dumps({"status": "error", "message": f"Failed to write summary: {e}"}))
        sys.exit(1)
    f_db = load_db(FILTER_DB)
    q_db = load_db(QUALITY_DB)
    print(json.dumps({"status": "ok", "path": str(out_path), "filter_entries": len(f_db["entries"]), "quality_entries": len(q_db["entries"])}))


def health():
    """Run a quick integrity check on both database files."""
    issues = []
    results = {}

    for label, path in [("filter", FILTER_DB), ("quality", QUALITY_DB)]:
        if not path.exists():
            issues.append(f"{label}: file missing ({path})")
            results[label] = {"ok": False, "reason": "file missing"}
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                db = json.load(f)
        except json.JSONDecodeError as e:
            issues.append(f"{label}: corrupted JSON — {e}")
            results[label] = {"ok": False, "reason": f"corrupted JSON: {e}"}
            continue

        entry_count = len(db.get("entries", []))
        declared = db.get("_total_entries", -1)
        count_ok = entry_count == declared
        if not count_ok:
            issues.append(f"{label}: _total_entries mismatch (declared {declared}, actual {entry_count})")

        results[label] = {
            "ok": count_ok,
            "entries": entry_count,
            "declared_total": declared,
            "last_updated": db.get("_last_updated"),
        }

    print(json.dumps({
        "status": "ok" if not issues else "issues_found",
        "databases": results,
        "issues": issues,
    }, indent=2))


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Global --project option: redirect both DBs to a per-project namespace
    # under db/projects/ so production-specific lessons stay scoped.
    if "--project" in sys.argv:
        idx = sys.argv.index("--project")
        if idx + 1 >= len(sys.argv):
            print(json.dumps({"status": "error",
                              "message": "--project requires a project name"}))
            sys.exit(1)
        project = sys.argv[idx + 1]
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", project):
            print(json.dumps({"status": "error",
                              "message": f"Invalid project name: {project!r} "
                                         "(alphanumeric, dash, underscore)"}))
            sys.exit(1)
        del sys.argv[idx:idx + 2]
        PROJECT_MODE = True
        FILTER_DB = DB_DIR / "projects" / f"{project}-filter-memory.json"
        QUALITY_DB = DB_DIR / "projects" / f"{project}-quality-memory.json"

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "add-filter" and len(sys.argv) >= 3:
        add_filter(sys.argv[2])
    elif cmd == "add-quality" and len(sys.argv) >= 3:
        add_quality(sys.argv[2])
    elif cmd == "query-filter" and len(sys.argv) >= 3:
        try:
            top_n = int(sys.argv[3]) if len(sys.argv) >= 4 else 5
        except ValueError:
            print(json.dumps({"status": "error", "message": f"top_n must be an integer, got: {sys.argv[3]}"}))
            sys.exit(1)
        query_filter(sys.argv[2], top_n)
    elif cmd == "query-quality" and len(sys.argv) >= 3:
        try:
            top_n = int(sys.argv[3]) if len(sys.argv) >= 4 else 5
        except ValueError:
            print(json.dumps({"status": "error", "message": f"top_n must be an integer, got: {sys.argv[3]}"}))
            sys.exit(1)
        query_quality(sys.argv[2], top_n)
    elif cmd == "update-filter" and len(sys.argv) >= 4:
        notes = sys.argv[4] if len(sys.argv) >= 5 else ""
        update_filter(sys.argv[2], sys.argv[3], notes)
    elif cmd == "update-quality" and len(sys.argv) >= 4:
        improved = sys.argv[4] if len(sys.argv) >= 5 else ""
        notes = sys.argv[5] if len(sys.argv) >= 6 else ""
        update_quality(sys.argv[2], sys.argv[3], improved, notes)
    elif cmd == "stats":
        stats()
    elif cmd == "export-summary":
        export_summary()
    elif cmd == "health":
        health()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)
