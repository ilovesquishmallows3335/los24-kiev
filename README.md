# kiev: LineageOS 24.0 (Android 17) via GitHub Actions

Motorola moto g 5G / one 5G ace (kiev, SM7225). Official LineageOS support currently goes up to
23.2 (Android 16), so this is a rebase of those trees onto `lineage-24.0`.

## Use

1. Create a repo, add these files, push.
2. Actions tab > "Build LineageOS 24.0 (Android 17) for kiev" > Run workflow.
   - First run: target `bootimage`, tree branch `lineage-23.2`.
3. Download the artifacts (images, `kiev-build-logs`) from the run page.
4. Re-run to continue: ccache carries over between runs (max about 9 GB cached).

## Make it finish

- Free runners have about 16 GB RAM and 6 h limits; expect several runs for a cold build.
  Set the repo variable `RUNNER_LABEL` to a larger runner label if you have one.
- Fix breakages in your own fork of the device tree (branch `lineage-24.0`), then run the
  workflow with `device_repo` set to your fork and `tree_branch` to `lineage-24.0`.
- For small fixes to other repos, put them in `patches/apply.sh`.

## Where it will break (Android 16 -> 17)

sepolicy denials and neverallows, VINTF manifest and compatibility matrix mismatches,
HAL version bumps, and any blobs that no longer load. Read `out/error.log` first.

Flash with the steps on the LineageOS kiev install page; bootloader unlock is required.
