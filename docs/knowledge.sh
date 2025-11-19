#!/usr/bin/env bash
set -euo pipefail

# Config
REPO_ROOT="$(git rev-parse --show-toplevel)"
DOC="$REPO_ROOT/docs/knowledge.md"
FRONTEND_DIR="$REPO_ROOT/frontend"
BACKEND_DIR="$REPO_ROOT/backend"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
STRUCT_DEPTH="${STRUCT_DEPTH:-ALL}"
FRONT_SRC="$FRONTEND_DIR/src"
FOCUS_APPS="${FOCUS_APPS:-}"

should_process_app() {
  # si FOCUS_APPS est vide => on prend tout
  local app="$1"
  [ -z "$FOCUS_APPS" ] && return 0
  local IFS=','; for a in $FOCUS_APPS; do [ "$a" = "$app" ] && return 0; done
  return 1
}

# -------- Helpers --------
has() { command -v "$1" >/dev/null 2>&1; }

gen_tree() {
  local dir="$1"; local depth="${2:-$STRUCT_DEPTH}"
  if [ ! -d "$dir" ]; then echo "(absent) $dir"; return 0; fi

  # Exclusions communes
  local IGNORE='htmlcov|node_modules|.git|.venv|venv|__pycache__|dist|build|.next|.pytest_cache|.mypy_cache|.idea|.vscode|.DS_Store'

  if has tree; then
    if [ "$depth" = "ALL" ]; then
      tree -a -I "$IGNORE"
    else
      tree -a -L "$depth" -I "$IGNORE"
    fi
  else
    # Fallback portable
    (
      cd "$dir"
      if [ "$depth" = "ALL" ]; then
        find . -mindepth 1 \
          -not -path '*/node_modules/*' \
          -not -path '*/htmlcov/*' \
          -not -path '*/.git/*' \
          -not -path '*/.venv/*' -not -path '*/venv/*' \
          -not -path '*/__pycache__/*' \
          -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/.next/*' \
          -not -path '*/.pytest_cache/*' -not -path '*/.mypy_cache/*' \
          -not -path '*/.idea/*' -not -path '*/.vscode/*' \
          -not -name '.DS_Store' \
        | sort
      else
        find . -mindepth 1 -maxdepth "$depth" \
          -not -path '*/node_modules/*' \
          -not -path '*/htmlcov/*' \
          -not -path '*/.git/*' \
          -not -path '*/.venv/*' -not -path '*/venv/*' \
          -not -path '*/__pycache__/*' \
          -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/.next/*' \
          -not -path '*/.pytest_cache/*' -not -path '*/.mypy_cache/*' \
          -not -path '*/.idea/*' -not -path '*/.vscode/*' \
          -not -name '.DS_Store' \
        | sort
      fi
    )
  fi
}
now_paris() {
  TZ=Europe/Paris date '+%Y-%m-%d %H:%M:%S %Z'
}

# -------- Generate sections --------

# 1) Project structure (single unified tree)
{
  echo '```text'
  gen_tree "$REPO_ROOT" "ALL"
  echo '```'
} > "$TMP_DIR/PROJECT_STRUCTURE.md"

# 2) package.json summaries (name, version, scripts keys, deps counts, top deps)
gen_pkg_summary() {
  local pkg="$1"
  if [ ! -f "$pkg" ]; then echo "_No package.json found at ${pkg}_"; return; fi

  if has jq; then
    local name version scripts_count deps_count devdeps_count
    name=$(jq -r '.name // "-" ' "$pkg")
    version=$(jq -r '.version // "-" ' "$pkg")
    scripts_count=$(jq '(.scripts // {}) | length' "$pkg")
    deps_count=$(jq '(.dependencies // {}) | length' "$pkg")
    devdeps_count=$(jq '(.devDependencies // {}) | length' "$pkg")

    echo "**name**: \`$name\`  •  **version**: \`$version\`"
    echo "**scripts**: $scripts_count  •  **dependencies**: $deps_count  •  **devDependencies**: $devdeps_count"
    echo
    echo "<details><summary>Top dependencies</summary>"
    echo
    jq -r '(.dependencies // {}) | to_entries | sort_by(.key) | .[0:20][] | "- \(.key): \(.value)"' "$pkg"
    echo
    echo "</details>"
    echo
    echo "<details><summary>Scripts</summary>"
    echo
    jq -r '(.scripts // {}) | to_entries[] | "- \(.key): \(.value)"' "$pkg"
    echo
    echo "</details>"
  else
    # Fallback Python
    python3 - "$pkg" <<'PY'
import json, sys, itertools
p=sys.argv[1]
data=json.load(open(p, encoding="utf-8"))
name=data.get("name","-"); version=data.get("version","-")
scripts=data.get("scripts",{}) or {}; deps=data.get("dependencies",{}) or {}; dev=data.get("devDependencies",{}) or {}
print(f"**name**: `{name}`  •  **version**: `{version}`")
print(f"**scripts**: {len(scripts)}  •  **dependencies**: {len(deps)}  •  **devDependencies**: {len(dev)}\n")
print("<details><summary>Top dependencies</summary>\n")
for k in list(sorted(deps.keys()))[:20]:
    print(f"- {k}: {deps[k]}")
print("\n</details>\n")
print("<details><summary>Scripts</summary>\n")
for k,v in scripts.items():
    print(f"- {k}: {v}")
print("\n</details>")
PY
  fi
}

{
  echo "Path: \`$FRONTEND_DIR/package.json\`"
  gen_pkg_summary "$FRONTEND_DIR/package.json"
} > "$TMP_DIR/FRONTEND_PACKAGE_JSON.md"

{
  echo "Path: \`$BACKEND_DIR/package.json\`"
  gen_pkg_summary "$BACKEND_DIR/package.json"
} > "$TMP_DIR/BACKEND_PACKAGE_JSON.md"

# 3) Django models scan
python3 - "$BACKEND_DIR" > "$TMP_DIR/DJANGO_MODELS.md" <<'PY'
import re, sys, pathlib
root = pathlib.Path(sys.argv[1])
apps_dir = root / "apps"
paths = list(apps_dir.rglob("models.py")) if apps_dir.exists() else list(root.rglob("models.py"))
pattern = re.compile(r"^class\s+([A-Za-z0-9_]+)\s*\(\s*(?:models\.)?Model\s*\)\s*:", re.M)
rows = []
for p in sorted(paths):
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    classes = pattern.findall(text)
    if classes:
        rel = p.as_posix().split("/backend/")[-1] if "/backend/" in p.as_posix() else p.as_posix()
        for c in classes:
            rows.append((c, rel))
if not rows:
    print("_No Django models found (searched **backend/**). Adjust the path if needed._")
else:
    print("| Model | File |")
    print("|---|---|")
    for c, rel in rows:
        print(f"| `{c}` | `{rel}` |")
PY

# 4) Last updated block
{
  echo "_Updated_: **$(now_paris)**"
} > "$TMP_DIR/LAST_UPDATED.md"

# -------- Replace blocks in docs/knowledge.md --------
python3 - "$DOC" "$TMP_DIR" <<'PY'
import sys, pathlib, re

doc_path = pathlib.Path(sys.argv[1])
tmp = pathlib.Path(sys.argv[2])

def replace_block(text, key, new_content):
    start = f"<!-- BEGIN AUTO: {key} -->"
    end = f"<!-- END AUTO: {key} -->"
    pattern = re.compile(rf"({re.escape(start)})(.*?){re.escape(end)}", re.S)
    repl = start + "\n" + new_content.rstrip() + "\n" + f"<!-- END AUTO: {key} -->"
    if not pattern.search(text):
        raise SystemExit(f"[knowledge.sh] Missing markers for {key} in {doc_path}")
    return pattern.sub(repl, text, count=1)

text = doc_path.read_text(encoding="utf-8")

sections = {
    "PROJECT_STRUCTURE": (tmp / "PROJECT_STRUCTURE.md").read_text(),
    "FRONTEND_PACKAGE_JSON": (tmp / "FRONTEND_PACKAGE_JSON.md").read_text(),
    "BACKEND_PACKAGE_JSON": (tmp / "BACKEND_PACKAGE_JSON.md").read_text(),
    "DJANGO_MODELS": (tmp / "DJANGO_MODELS.md").read_text(),
    "LAST_UPDATED": (tmp / "LAST_UPDATED.md").read_text(),
}

for k, v in sections.items():
    text = replace_block(text, k, v)

doc_path.write_text(text, encoding="utf-8")
PY

# Stage if changed (so the commit capte la MAJ)
if ! git diff --quiet -- "$DOC"; then
  git add "$DOC"
fi

echo "[knowledge.sh] docs/knowledge.md updated."
