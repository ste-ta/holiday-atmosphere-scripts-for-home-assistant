# Changelog

## 2.1.0

- Install one self-contained script for all 16 holiday effects through a single blueprint import link, or paste one YAML file. No helpers, companion scripts, package configuration, fixed entity IDs, or restart required.
- Choose default lights and effect when creating the script; override them for individual runs.
- Preserve the original lighting scene across effect and holiday switches. Restore old targets before changing rooms.
- Retain the backup when restoration raises an error or a saved bulb is unavailable, allowing Stop to be retried.
- Reject missing/empty/invalid targets, unsupported effects and controls without overwriting the original backup. Native restart mode stops an active run before validating the next call.
- Expand Home Assistant light groups, deduplicate targets, skip unavailable bulbs, and pace attempts even when all targets become unavailable.
- Add brightness ceiling, effect speed, duration, pacing profiles, gentle mode, restoration control, and optional shared frame updates.
- Schedule ten accelerating countdown beats against a duration or timezone-aware timestamp, with expired phases skipped rather than queued late.
- Keep effect execution and natural cleanup in the same run, so replacing a timed effect cancels its cleanup as well.
- Consolidate palette cycling and frame updates within the script, with special lightning, heartbeat, dinner highlights, party modes, countdown, and midnight fade patterns.
- Replace unrestricted XY jitter with bounded palettes.
- Update installation, usage, migration, effect descriptions, and hardware limitations.
- Add Home Assistant script-engine regression tests and CI for 2025.1.4 and 2026.10.0, including single-blueprint import and execution without any companion services.

### Upgrade notes

Stop existing effects before upgrading. Import the single replacement script, update dashboard/automation calls to its entity ID, then remove the old holiday script definitions. Direct calls now wait for the effect to finish; use `script.turn_on` with `data.variables` to start in the background. Stop before renaming the replacement script because its temporary backup follows its entity ID. Pacing and some palette timings change in this release.

## 2.0.0 (2025)

- Split the original combined script into separate Halloween, Christmas, and New Year scripts.

## 1.0.0 (2025)

- Initial release.
