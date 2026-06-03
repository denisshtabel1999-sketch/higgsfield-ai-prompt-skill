#!/usr/bin/env python3
"""
validate.py
===========
Pre-release health check for the Higgsfield AI Prompt Skill repo.

Checks:
  - All SKILL.md files exist and have required frontmatter fields
  - Relative path references inside SKILL.md files resolve to real files
  - JSON databases are valid and schema-complete
  - Entry counts match _total_entries declarations
  - Root SKILL.md version/updated agree with the README badge + footer

Usage:
  python validate.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DB_FILES = {
    "filter": ROOT / "db/filter-memory.json",
    "quality": ROOT / "db/quality-memory.json",
}
FILTER_REQUIRED_FIELDS = {"id", "category", "blocked_terms", "error_message",
                           "substitution", "fix_confirmed", "substitution_worked", "tags"}
QUALITY_REQUIRED_FIELDS = {"id", "failure_type", "model_used", "original_prompt",
                            "failure_description", "outcome", "fix_confirmed",
                            "improvement_confirmed", "tags"}
# Supported top-level SKILL.md frontmatter attributes (tags now lives inside metadata)
FRONTMATTER_REQUIRED = {"name", "description", "user-invocable"}

PASS = "\033[32m✓\033[0m"
FAIL = "\033[31m✗\033[0m"
WARN = "\033[33m⚠\033[0m"

issues = []
warnings = []


def check(ok: bool, label: str, detail: str = "") -> bool:
    symbol = PASS if ok else FAIL
    suffix = f"  ({detail})" if detail else ""
    print(f"  {symbol} {label}{suffix}")
    if not ok:
        issues.append(f"{label}{suffix}")
    return ok


def warn(label: str, detail: str = ""):
    print(f"  {WARN} {label}" + (f"  ({detail})" if detail else ""))
    warnings.append(label)


def check_frontmatter(skill_file: Path):
    text = skill_file.read_text(encoding="utf-8")
    # Extract YAML frontmatter between --- delimiters
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        check(False, f"{skill_file.relative_to(ROOT)}: missing frontmatter")
        return
    fm = match.group(1)
    for field in FRONTMATTER_REQUIRED:
        present = re.search(rf"^{field}:", fm, re.MULTILINE) is not None
        if not present:
            check(False, f"{skill_file.relative_to(ROOT)}: missing frontmatter field '{field}'")
    # tags should be nested inside metadata, not at the top level
    if re.search(r"^tags:", fm, re.MULTILINE):
        check(False, f"{skill_file.relative_to(ROOT)}: tags should be inside metadata, not at top level")


def check_relative_paths(skill_file: Path):
    text = skill_file.read_text(encoding="utf-8")
    # Find all relative paths referenced with backticks or markdown links
    # Matches: `../../../vocab.md` or `skills/higgsfield-prompt/SKILL.md`
    refs = re.findall(r'`((?:\.\.\/|[\w-]+\/)[\w./%-]+\.(?:md|py|json))`', text)
    for ref in refs:
        target = (skill_file.parent / ref).resolve()
        exists = target.exists()
        label = f"{skill_file.relative_to(ROOT)}: ref '{ref}'"
        check(exists, label, "" if exists else f"resolves to {target} — not found")


def check_json_db(label: str, path: Path, required_fields: set):
    print(f"\n  Checking {label} database ({path.relative_to(ROOT)})...")
    if not check(path.exists(), f"{label}: file exists"):
        return

    try:
        with open(path, encoding="utf-8") as f:
            db = json.load(f)
    except json.JSONDecodeError as e:
        check(False, f"{label}: valid JSON", str(e))
        return

    check(True, f"{label}: valid JSON")

    entries = db.get("entries", [])
    declared = db.get("_total_entries", -1)
    check(len(entries) == declared,
          f"{label}: entry count matches _total_entries",
          f"declared={declared}, actual={len(entries)}")

    for entry in entries:
        eid = entry.get("id", "?")
        for field in required_fields:
            if field not in entry:
                check(False, f"{label} entry {eid}: missing field '{field}'")


def check_version_consistency():
    """Cross-check the single-source version/date in root SKILL.md against the
    README badge and footer. Catches drift like a stale frontmatter `updated:`
    that the per-file frontmatter check can't see (it validates one file at a
    time)."""
    skill = ROOT / "SKILL.md"
    readme = ROOT / "README.md"
    if not check(skill.exists(), "SKILL.md exists") or not check(readme.exists(), "README.md exists"):
        return

    fm_match = re.match(r"^---\n(.*?)\n---", skill.read_text(encoding="utf-8"), re.DOTALL)
    if not fm_match:
        check(False, "SKILL.md frontmatter parses")
        return
    fm = fm_match.group(1)
    readme_text = readme.read_text(encoding="utf-8")

    # SKILL.md version/updated live nested under `metadata:` — allow indentation.
    skill_version = re.search(r"^\s*version:\s*([0-9]+\.[0-9]+\.[0-9]+)", fm, re.MULTILINE)
    skill_updated = re.search(r"^\s*updated:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", fm, re.MULTILINE)
    # README badge: .../badge/version-3.8.1-blue
    badge_version = re.search(r"badge/version-([0-9]+\.[0-9]+\.[0-9]+)-", readme_text)
    # README footer: ... v3.8.1 (updated 2026-06-03) ...
    footer = re.search(r"v([0-9]+\.[0-9]+\.[0-9]+)\s*\(updated\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\)", readme_text)

    if not check(bool(skill_version), "SKILL.md frontmatter has a version"):
        return
    if not check(bool(skill_updated), "SKILL.md frontmatter has an updated date"):
        return
    if not check(bool(badge_version), "README has a version badge"):
        return
    if not check(bool(footer), "README footer has 'vX.Y.Z (updated YYYY-MM-DD)'"):
        return

    sv, su = skill_version.group(1), skill_updated.group(1)
    bv = badge_version.group(1)
    fv, fu = footer.group(1), footer.group(2)

    check(sv == bv, "SKILL.md version matches README badge",
          "" if sv == bv else f"SKILL.md={sv}, badge={bv}")
    check(sv == fv, "SKILL.md version matches README footer",
          "" if sv == fv else f"SKILL.md={sv}, footer={fv}")
    check(su == fu, "SKILL.md updated date matches README footer",
          "" if su == fu else f"SKILL.md={su}, footer={fu}")


def main():
    print(f"\nHiggsfield Skill Repo — Validation Report")
    print(f"Root: {ROOT}\n")

    # ── 1. Find all SKILL.md files ──────────────────────────────────────────
    print("[ SKILL.md FILES ]")
    skill_files = list(ROOT.rglob("SKILL.md"))
    print(f"  Found {len(skill_files)} SKILL.md files")

    for sf in sorted(skill_files):
        print(f"\n  — {sf.relative_to(ROOT)}")
        check_frontmatter(sf)
        check_relative_paths(sf)

    # ── 2. JSON databases ───────────────────────────────────────────────────
    print("\n[ JSON DATABASES ]")
    check_json_db("filter-memory", DB_FILES["filter"], FILTER_REQUIRED_FIELDS)
    check_json_db("quality-memory", DB_FILES["quality"], QUALITY_REQUIRED_FIELDS)

    # ── 3. Key root files present ───────────────────────────────────────────
    print("\n[ ROOT FILES ]")
    expected_root_files = [
        "SKILL.md", "README.md", "CHANGELOG.md", "DISCIPLINE.md",
        "model-guide.md", "image-models.md", "vocab.md",
        "prompt-examples.md", "photodump-presets.md",
        "production-benchmarks.md",
        "higgsfield_memory.py",
        "db/filter-memory.json", "db/quality-memory.json",
    ]
    for name in expected_root_files:
        path = ROOT / name
        check(path.exists(), name)

    # ── 4. Version / date consistency ───────────────────────────────────────
    print("\n[ VERSION / DATE CONSISTENCY ]")
    check_version_consistency()

    # ── 5. PDF dry-run smoke check ──────────────────────────────────────────
    print("\n[ PDF DRY-RUN SMOKE ]")
    import subprocess
    try:
        result = subprocess.run(
            ["python3", str(ROOT / "generate_user_guide.py"), "--dry-run"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        check(False, "generate_user_guide.py --dry-run", "timeout after 60s")
    else:
        if result.returncode == 0:
            check(True, "generate_user_guide.py --dry-run", "exit 0")
        else:
            stderr_lines = result.stderr.strip().splitlines() if result.stderr else []
            stderr_excerpt = stderr_lines[0] if stderr_lines else "(no stderr output)"
            check(
                False,
                "generate_user_guide.py --dry-run",
                f"exit {result.returncode}; stderr: {stderr_excerpt[:150]}",
            )

    # ── Summary ─────────────────────────────────────────────────────────────
    print(f"\n{'='*50}")
    if issues:
        print(f"\033[31m  FAILED — {len(issues)} issue(s) found:\033[0m")
        for i in issues:
            print(f"    • {i}")
        sys.exit(1)
    else:
        print(f"\033[32m  ALL CHECKS PASSED\033[0m" +
              (f" ({len(warnings)} warning(s))" if warnings else ""))
        sys.exit(0)


if __name__ == "__main__":
    main()
