#!/usr/bin/env bash
# Optional: mirror the CDN runtime locally for sandboxed agents without CDN access.
# Browser QA and release_pdf.py use .cache/cdn-mirror automatically when it exists,
# or any folder named by IE_QA_CDN_MIRROR. Requires npm and registry access.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MIRROR="${IE_QA_CDN_MIRROR:-${ROOT_DIR}/.cache/cdn-mirror}"
mkdir -p "${MIRROR}"
npm install --prefix "${MIRROR}" --no-audit --no-fund reveal.js@5.2.1 katex@0.16 @fontsource/montserrat@5
echo "Offline CDN mirror ready: ${MIRROR}"
