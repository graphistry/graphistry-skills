#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REF_DIR="${ROOT_DIR}/.agents/skills/pygraphistry/references"

DOCS_HOME_URL="https://pygraphistry.readthedocs.io/en/latest/"
SITEMAP_URL="https://pygraphistry.readthedocs.io/sitemap.xml"
ROBOTS_URL="https://pygraphistry.readthedocs.io/robots.txt"

SITEMAP_SNAPSHOT="${REF_DIR}/pygraphistry-readthedocs-sitemap.xml"
TOPLEVEL_TSV="${REF_DIR}/pygraphistry-readthedocs-top-level.tsv"
TOC_MD="${REF_DIR}/pygraphistry-readthedocs-toc.md"

OUTPUT_DIR="${REF_DIR}"
TIMESTAMP_OVERRIDE=""

usage() {
  cat <<'USAGE'
Usage: ./scripts/refresh_pygraphistry_docs_toc.sh [options]

Options:
  --output-dir DIR   Write outputs into DIR instead of default refs directory
  --timestamp ISO    Override generated timestamp string (for deterministic CI)
  -h, --help         Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --timestamp)
      TIMESTAMP_OVERRIDE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

mkdir -p "${OUTPUT_DIR}"

SITEMAP_SNAPSHOT="${OUTPUT_DIR}/pygraphistry-readthedocs-sitemap.xml"
TOPLEVEL_TSV="${OUTPUT_DIR}/pygraphistry-readthedocs-top-level.tsv"
TOC_MD="${OUTPUT_DIR}/pygraphistry-readthedocs-toc.md"

tmp_dir="$(mktemp -d)"
trap 'rm -rf "${tmp_dir}"' EXIT

index_html="${tmp_dir}/index.html"
timestamp="${TIMESTAMP_OVERRIDE:-$(date -u +"%Y-%m-%dT%H:%M:%SZ")}"

curl --retry 3 --retry-all-errors --retry-delay 2 -fsSL "${SITEMAP_URL}" > "${SITEMAP_SNAPSHOT}"
curl --retry 3 --retry-all-errors --retry-delay 2 -fsSL "${DOCS_HOME_URL}" > "${index_html}"

perl -ne 'while (/<li class="toctree-l1[^>]*><a class="reference internal" href="([^"]+)">([^<]+)/g) { print "$1\t$2\n" }' \
  "${index_html}" > "${TOPLEVEL_TSV}"

{
  echo "# PyGraphistry Docs TOC (ReadTheDocs)"
  echo
  echo "Snapshot generated (UTC): \`${timestamp}\`"
  echo "Snapshot source alias: \`latest\` (rolling)"
  echo
  echo "## Live Indexes"
  echo "- Docs home: ${DOCS_HOME_URL}"
  echo "- Version sitemap (ReadTheDocs): ${SITEMAP_URL}"
  echo "- Robots (points to sitemap): ${ROBOTS_URL}"
  echo
  echo "Note: ReadTheDocs \`sitemap.xml\` here is a **version-level index** (latest + historical versions), not a per-page sitemap for \`/en/latest/\`."
  echo
  echo "Freshness guidance:"
  echo "- Use local snapshots for fast lookup."
  echo "- If user asks for newest/recent/latest updates, verify against live web pages."
  echo
  echo "## Top-Level Docs Sections (latest)"
  sed 's/&amp;/\&/g' "${TOPLEVEL_TSV}" \
    | awk -F '\t' '{printf "- [%s](https://pygraphistry.readthedocs.io/en/latest/%s)\n", $2, $1}'
  echo
  echo "## RTD -> GitHub Translation (Best Effort)"
  echo "- Source repo: https://github.com/graphistry/pygraphistry"
  echo "- For \`/en/latest/<path>.html\`, try \`docs/source/<path>.rst\`, then \`docs/source/<path>.md\`."
  echo "- For \`/en/latest/demos/<path>.html\`, try \`demos/<path>.ipynb\`, then \`demos/<path>.html\`."
  echo "- Some Sphinx-generated pages do not map 1:1 to a single repo file."
  echo
  echo "## Saved Snapshots"
  echo "- Version sitemap snapshot: \`pygraphistry-readthedocs-sitemap.xml\`"
  echo "- Top-level TOC extraction snapshot: \`pygraphistry-readthedocs-top-level.tsv\`"
  echo
  echo "## Refresh"
  echo '```bash'
  echo './scripts/refresh_pygraphistry_docs_toc.sh'
  echo '```'
} > "${TOC_MD}"

echo "Refreshed:"
echo "- ${SITEMAP_SNAPSHOT}"
echo "- ${TOPLEVEL_TSV}"
echo "- ${TOC_MD}"
