#!/usr/bin/env bash
# Clones the case data into data/ (kept out of git, see .gitignore)
set -e
[ -d data/.git ] && git -C data pull || git clone --depth 1 https://github.com/Fa-Bee/sprintd-basel-green-ai-data data
