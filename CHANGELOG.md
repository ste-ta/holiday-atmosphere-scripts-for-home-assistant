# Changelog

## 2.1.0

- One controller and runner now manage all three holidays, with one active show globally.
- Preserve the original lighting snapshot across effect and holiday switches; restore old targets before changing rooms.
- Retain the backup when restoration raises an error or a saved bulb is unavailable, allowing stop to be retried.
- Reject missing/empty/invalid targets, unsupported effects and controls before interrupting an active show; expand light groups, deduplicate targets, and skip unavailable bulbs.
- Add brightness ceiling, effect speed, duration, pacing profiles, gentle mode, restore-on-completion, and optional shared frame updates.
- Replace the bulb-index countdown with ten accelerating beats scheduled against a deadline; add countdown length and target timestamp controls.
- Guard automatic completion with session tokens so stale timers cannot stop a newer effect.
- Consolidate palette cycling and paced light updates. Keep lightning, heartbeat, dinner highlights, party modes, countdown, and midnight fade patterns.
- Replace unrestricted XY jitter with bounded color palettes.
- Supply a complete Home Assistant package, migration instructions, corrected effect documentation, and explicit hardware limitations.
- Add native import links for all three shared-core scripts and a room-preset script blueprint; new installs can use links plus one Text helper without editing YAML.
- Add regression tests executing the shipped YAML in Home Assistant's script engine, plus schema checks and CI for 2025.1.4 and 2026.10.0.

### Upgrade notes

The three holiday files now call the shared controller and cannot be installed alone. Install all shared scripts and the session helper, preferably using `packages/holiday_atmosphere.yaml`. Keep the existing holiday entity IDs when updating through the UI, and do not install duplicate copies via both UI and packages. Stop version 2.0 effects before upgrading to restore their lights. Command pacing and some palette timings change in this release.

## 2.0.0 (2025)

- Split the original combined script into separate Halloween, Christmas, and New Year scripts.

## 1.0.0 (2025)

- Initial release.
