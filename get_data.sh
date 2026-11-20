#!/usr/bin/env bash
# The case data is already committed in data/ (copy of https://github.com/Fa-Bee/sprintd-basel-green-ai-data).
# Only needed if data/ is missing: fetches a fresh copy.
set -e
if [ -f data/README.md ]; then echo "data/ already present"; exit 0; fi
git clone --depth 1 https://github.com/Fa-Bee/sprintd-basel-green-ai-data data && rm -rf data/.git
