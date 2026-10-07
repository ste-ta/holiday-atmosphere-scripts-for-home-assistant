# 🎄🎃🎆 Holiday Atmosphere — v2.1.0

**One script. All 16 effects. No helpers or companion scripts.**

## Install

[![Import blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fste-ta%2Fholiday-atmosphere-scripts-for-home-assistant%2Fblob%2Fmain%2Fblueprints%2Fscript%2Fholiday_atmosphere.yaml)

1. Click **Import blueprint** above.
2. Select **Create script**, choose your lights and a default effect, then **Save**.
3. Run your new script.

That is the entire setup. No configuration-file edits, restart, packages, fixed entity IDs, or helper creation. The import link becomes available on `main` after the v2.1 PR is merged; the PR description includes a preview link you can use before merging.

Requires Home Assistant **2025.1.4 or newer** and color-capable lights. Tested with the Home Assistant 2025.1.4 and 2026.10.0 script engines; physical bulb behavior depends on your integration and hardware.

Prefer pasting YAML? Create one script in Settings → Automations & scenes → Scripts, open **Edit in YAML**, paste [`holiday-atmosphere.yaml`](holiday-atmosphere.yaml), and save. Choose your lights when running it, or set `default_lights` and `default_effect` under its `variables:` to save your usual settings. You only need this one file.

## Use

Run the saved script to use your default lights and effect. In Home Assistant's Actions tool or an automation, choose the script itself to see its fields. Override **Effect** to switch between Halloween, Christmas, and New Year patterns. Choose **stop** to stop updates and restore the original lighting.

Each new call replaces the current run. Switching effects on the same lights preserves the original scene. Changing lights restores the old lights first, then captures a new scene. The script creates and deletes its temporary backup automatically.

To start it from an automation without waiting for an indefinitely running effect:

```yaml
action: script.turn_on
target:
  entity_id: script.holiday_atmosphere  # Use your saved script's actual entity ID.
data:
  variables:
    effect: xmas_fireplace
    brightness_max: 150
    duration: 1800
```

Stop using the same script, with no light list needed:

```yaml
action: script.turn_on
target:
  entity_id: script.holiday_atmosphere
data:
  variables:
    effect: stop
```

A direct `action: script.holiday_atmosphere` call waits until the effect finishes or is stopped. Use `script.turn_on` when an automation should continue immediately, with values under `data.variables`. There is no `wait` option. See [Home Assistant's script calling documentation](https://www.home-assistant.io/actions/script.turn_on/).

For a dashboard button, select your saved script as its action. Calling it without parameters runs the default preset you chose when installing. A custom Stop button can use:

```yaml
type: button
name: Stop holiday lights
tap_action:
  action: perform-action
  perform_action: script.turn_on
  target:
    entity_id: script.holiday_atmosphere
  data:
    variables:
      effect: stop
```

## Optional controls

Defaults work without changing these settings.

| Field | Default | Behavior |
| --- | --- | --- |
| `lights` | Saved lights | One light ID or a list; overrides your saved selection. Home Assistant light groups expand to individual members. |
| `effect` | Saved effect | One of the 16 effects below, or `stop`. |
| `brightness_max` | 255 | Brightness ceiling, 1–255. Applies to effects, not restoration. |
| `speed` | 1 | 0.25–4; higher is faster. Scales ambient holds and transitions, but never bypasses command pacing or countdown deadlines. |
| `duration` | 0 | Maximum effect duration in seconds, up to 86400. Zero means unlimited for repeating effects. |
| `pacing` | balanced | Minimum delay after a light action: conservative 1000 ms, balanced 250 ms, fast 100 ms. These are tuning profiles, not hardware guarantees. |
| `gentle` | false | Rejects flashing effects. Choose an ambient effect instead. |
| `restore_on_stop` | true | Restore on natural completion or explicit Stop. False deliberately leaves the effect's final state and discards the backup. Target changes always restore old targets. |
| `group_updates` | false | Send one shared frame to all available targets instead of randomized individual frames. Physical synchronization depends on the integration. |
| `countdown_seconds` | 10 | Length of `nye_countdown`, 1–86400 seconds. |
| `countdown_target` | empty | Future ISO 8601 timestamp including timezone; overrides countdown length. Only for `nye_countdown`. |

An explicit Stop defaults to restoration even if the previous run was started with `restore_on_stop: false`; pass false with Stop too if you intend to discard the backup.

Example countdown ending at midnight:

```yaml
action: script.turn_on
target:
  entity_id: script.holiday_atmosphere
data:
  variables:
    effect: nye_countdown
    countdown_target: '2027-01-01T00:00:00+01:00'
    group_updates: true
    restore_on_stop: false
```

Ten beats accelerate toward the timestamp. Expired phases are skipped rather than queued late when pacing or action latency cannot fit them. Use a separate midnight automation to switch to `nye_midnight_flash` or `nye_confetti`; an expired timestamp cannot be reused. Device delivery is not a precision clock.

## Effects

Ranges below describe programmed values at `speed: 1` before brightness capping. Pacing, light count, action overhead, and device support affect what you see. Ambient holds start after frame updates and last at least the longest transition requested for that frame.

| Holiday | Effect | Pattern | Brightness | Transition / hold (seconds) |
| --- | --- | --- | --- | --- |
| Halloween | `hell` | Random fire reds and oranges | 100–255 | 2 or 3 / 4 or 6 |
| Halloween | `lightning` | Dim white followed by 4–9 bright/dim flash pairs | 3–9, 255 | 0 for flashes; variable short holds |
| Halloween | `graveyard` | Low green, teal, and blue fog | 30–60 | 5 or 9 / 6 or 13 |
| Halloween | `halloween` | Orange, purple, and green cycling | 150–220 | 3 or 5 / 4 or 8 |
| Halloween | `blood` | Two red pulses followed by darkness | 5–199 | 0.3–0.8 / double-pulse holds, then 2 or 3 |
| Christmas | `xmas_tree` | Red, green, and white cycling | 110–179 | 2 / 6 or 9 |
| Christmas | `xmas_snowfall` | Blue and cool-white variation | 40–149 | 1 or 3 / 1 or 2 |
| Christmas | `xmas_fireplace` | Bounded warm amber/orange palette | 90–199 | 1 or 2.5 / 1 or 2 |
| Christmas | `xmas_santa` | Red, white, and green variation | 140–199 | 1.5 or 2.5 / 2 or 3 |
| Christmas | `xmas_dinner` | Champagne glow; 30% chance per cycle of a highlight frame | 95–124; 140–169 highlights | 5 or 7; highlights 4 or 5 / base 4 or 6, highlights 8 or 11 |
| Christmas | `xmas_party` | Random strobe, three-color cycle, red strobe, and dim-background solo spotlight; eight beats per mode | 20–255 | 0 / 0.3 or 0.7 |
| New Year | `nye_countdown` | Ten accelerating bright/dim beats; finite | 5, 255 | 0 / scheduled deadline |
| New Year | `nye_confetti` | Rapid red, green, purple, white, and amber cycling | 200–254 | 0 / pacing only |
| New Year | `nye_midnight_flash` | Bright white, then fade to 120; finite | 255, 120 | 0, then 4 / 1, then 4 |
| New Year | `nye_sparkler` | Rapid variation around cool white | 180–254 | 0 / pacing only |
| New Year | `nye_champagne` | Warm golden cycling | 30–139 | 2 or 5 / 2 or 5 |

Gentle mode excludes `lightning`, `blood`, `xmas_party`, `nye_countdown`, `nye_confetti`, `nye_midnight_flash`, and `nye_sparkler`. Gentle mode is a pattern filter, not a medical guarantee.

## Restoration and limits

The script snapshots the original lights once and preserves that scene across effect switches. It retains the backup if a restore action raises an error or a saved bulb is unavailable. Bring the bulb back online and run `effect: stop` again. Restoration success means the action returned successfully; it is not proof that every physical bulb reached its exact original color or brightness.

Home Assistant's `restart` mode stops the current run **before validating the next call**. An invalid effect, target, or control therefore stops updates, but cannot overwrite the original backup. Correct the call to resume, or use Stop to restore. Single-script installation deliberately uses this native behavior.

Existing bulbs that are unavailable at startup are excluded from that session; later-unavailable bulbs are skipped and the script continues to wait between attempts. Light action failures appear in traces/logs and do not stop the effect. No automatic retry or recovery from frozen bulbs is claimed.

Dynamic scenes disappear on Home Assistant restart or scene reload. Script reloads and `script.turn_off` stop execution without automatic restoration. Use `effect: stop` for normal shutdown; after a restart, activate your preferred normal scene if needed. Stop before renaming/deleting this script, because its backup name follows its entity ID.

Install one instance for one active show. If you intentionally create multiple copies, use disjoint bulbs: copies cannot coordinate ownership of overlapping targets. No fixed script entity ID is required.

Pacing is per Home Assistant action. Group updates may fan out to multiple device commands, while individual sweeps grow with light count. Test on a small set of bulbs first. `duration` bounds new commands, but an in-flight action, its pacing delay, and restoration can finish later. This is not a hard real-time timeout.

For device-native animation, evaluate [WLED presets/effects](https://www.home-assistant.io/integrations/wled/) or [Hue scenes](https://www.home-assistant.io/integrations/hue/). They are alternatives; this script does not automatically select them.

## Upgrade

From version 2.0, Stop each running holiday script first. Import this one replacement script, then update your dashboard/automation calls to its entity ID. It includes all three holidays, so you can remove the three old scripts after updating their callers. A backup already overwritten by 2.0 may need manual restoration of your preferred scene.

If you tried an earlier revision of the v2.1 PR with shared scripts and a Text helper, Stop that show through its old entry point before switching. Those shared scripts, room-preset blueprints, package, and helper are no longer required; remove the old definitions after updating callers. Install the single blueprint or standalone file, not both.

To update the blueprint later, re-import it from the same link and reload scripts. Stop the current effect before updating. Your saved blueprint inputs remain your default lights/effect.

## Develop

Edit [`holiday-atmosphere.yaml`](holiday-atmosphere.yaml), then regenerate the standalone blueprint:

```sh
python tools/build_blueprint.py
python tools/build_blueprint.py --check
```

Regression tests execute this script in Home Assistant's real script engine with simulated device services and accelerated time. They cover restoration, target changes, concurrent calls, rejected inputs, unavailable bulbs, command errors, pacing, brightness caps, countdown deadlines, every effect, and single-blueprint import with saved defaults. The fixture registers no helper or companion-script services. Physical devices are not certified by these tests.

```sh
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python --prerelease=allow -r requirements-test.txt
.venv/bin/python -m pytest -q
```

CI covers Home Assistant 2025.1.4 / Python 3.13 and 2026.10.0 / Python 3.14. See [CHANGELOG.md](CHANGELOG.md) for release history.

## License

These projects are provided as-is for personal and commercial use. Feel free to modify and redistribute.
