#!/usr/bin/env bash
# Runs from the workflow after `repo sync`. $1 = tree root (/mnt/aosp).
# Put your Android 16 -> 17 fixes here, e.g.:
#   cd "$1/device/motorola/kiev" && git apply "$GITHUB_WORKSPACE/patches/0001-sepolicy.patch"
#   cd "$1/vendor/lineage"       && git apply "$GITHUB_WORKSPACE/patches/0002-vendor-lineage.patch"
set -euo pipefail
cd "$1"
echo "patches/apply.sh: nothing to apply yet"
