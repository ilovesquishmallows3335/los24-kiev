#!/usr/bin/env python3
"""Build a repo local manifest for kiev from the device tree's lineage.dependencies.

Run from the tree root after `repo init`. Env vars:
  DEVICE_REPO  e.g. LineageOS/android_device_motorola_kiev (or your fork)
  DEVICE_PATH  e.g. device/motorola/kiev
  TREE_BRANCH  branch to pull the trees from (e.g. lineage-23.2)
"""
import json
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

out_path = sys.argv[1]
device_repo = os.environ.get("DEVICE_REPO", "LineageOS/android_device_motorola_kiev")
device_path = os.environ.get("DEVICE_PATH", "device/motorola/kiev")
branch = os.environ["TREE_BRANCH"]


def sh(*args, **kw):
    return subprocess.run(args, check=False, capture_output=True, text=True, **kw)


def has_branch(repo, br):
    r = sh("git", "ls-remote", "--heads", f"https://github.com/{repo}", br)
    return r.returncode == 0 and bool(r.stdout.strip())


def pick_branch(repo, preferred, fallback=None):
    for b in (preferred, fallback):
        if b and has_branch(repo, b):
            return b
    sys.exit(f"ERROR: no usable branch for {repo} (tried {preferred}, {fallback})")


# Paths/names already in the default manifest must not be added again.
merged = sh("repo", "manifest")
if merged.returncode != 0:
    sys.exit("ERROR: `repo manifest` failed. Run repo init first.\n" + merged.stderr)
existing = set()
for p in ET.fromstring(merged.stdout).iter("project"):
    existing.add(p.get("path") or p.get("name"))

projects = []  # (name, path, revision)

dev_branch = pick_branch(device_repo, branch)
projects.append((device_repo, device_path, dev_branch))

with tempfile.TemporaryDirectory() as tmp:
    r = sh("git", "clone", "--depth=1", "-b", dev_branch,
           f"https://github.com/{device_repo}", tmp + "/dev")
    if r.returncode != 0:
        sys.exit("ERROR: cannot clone device tree:\n" + r.stderr)
    dep_file = os.path.join(tmp, "dev", "lineage.dependencies")
    deps = json.load(open(dep_file)) if os.path.exists(dep_file) else []

for d in deps:
    name = d["repository"]
    if "/" not in name:
        name = "LineageOS/" + name
    path = d["target_path"]
    if path in existing:
        print(f"skip {path}: already in default manifest")
        continue
    rev = pick_branch(name, branch, d.get("branch"))
    projects.append((name, path, rev))

# Vendor blobs (TheMuppets). Adjust if your device uses a different vendor repo.
vendor = "TheMuppets/proprietary_vendor_motorola"
if "vendor/motorola" not in existing and not any(p[1] == "vendor/motorola" for p in projects):
    try:
        projects.append((vendor, "vendor/motorola", pick_branch(vendor, branch)))
    except SystemExit as e:
        print(f"WARNING: {e}. Add your own vendor tree to the manifest.", file=sys.stderr)

root = ET.Element("manifest")
ET.SubElement(root, "remote", name="gh", fetch="https://github.com/")
for name, path, rev in projects:
    ET.SubElement(root, "project", name=name, path=path, remote="gh", revision=rev)
ET.indent(root)
ET.ElementTree(root).write(out_path, encoding="utf-8", xml_declaration=True)
print(f"wrote {out_path} with {len(projects)} projects")
