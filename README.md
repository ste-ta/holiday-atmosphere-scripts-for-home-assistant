# 🎄🎃🎆 Holiday Atmosphere for Home Assistant — v2.1.0

Sixteen Halloween, Christmas, and New Year lighting effects with one shared controller. Switch effects without losing the original lighting state, cap brightness, choose command pacing, and optionally stop after a set duration.

Requires Home Assistant **2025.1.4 or newer**, color-capable lights, and all six scripts plus the session helper. The regression suite covers Home Assistant 2025.1.4 and 2026.10.0. Physical bulb and bridge compatibility remains installation-dependent.

## Install or upgrade

**Version 2.1 uses one active show globally**, across all three holidays. Starting an effect in another room replaces the current show and restores the old room first. Independent concurrent room shows are not supported.

The holiday files now call shared scripts and **cannot be installed alone**. Their historical filenames and public entity IDs remain unchanged.

### Install with links (no YAML editing)

For a new installation, use Home Assistant's native blueprint importer:

1. Create a **Text helper** in Settings → Devices & services → Helpers. Set maximum length to 255, entity ID to `input_text.holiday_atmosphere_session`, and value to `{}`.
2. Import each shared-core blueprint below. For each, select **Create script**, save using the indicated name, and verify its entity ID. Create only one instance of each core script.

   | Create script named | Required entity ID | Import |
   | --- | --- | --- |
   | Holiday Atmosphere Light Step | `script.holiday_atmosphere_light_step` | [Import Light Step](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fste-ta%2Fholiday-atmosphere-scripts-for-home-assistant%2Fblob%2Fmain%2Fblueprints%2Fscript%2Fholiday_atmosphere_light_step.yaml) |
   | Holiday Atmosphere Runner | `script.holiday_atmosphere_runner` | [Import Runner](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fste-ta%2Fholiday-atmosphere-scripts-for-home-assistant%2Fblob%2Fmain%2Fblueprints%2Fscript%2Fholiday_atmosphere_runner.yaml) |
   | Holiday Atmosphere Controller | `script.holiday_atmosphere_controller` | [Import Controller](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fste-ta%2Fholiday-atmosphere-scripts-for-home-assistant%2Fblob%2Fmain%2Fblueprints%2Fscript%2Fholiday_atmosphere_controller.yaml) |

3. [Import the room-preset blueprint](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fste-ta%2Fholiday-atmosphere-scripts-for-home-assistant%2Fblob%2Fmain%2Fblueprints%2Fscript%2Fholiday_preset.yaml), select **Create script**, choose lights and an effect in the form, then save. Create a second preset with `effect: stop` for your Stop button.

This path needs no configuration-file edit or restart. It installs three shared scripts and any presets you create, rather than the three legacy holiday entry points. Run your preset's own script entity from buttons/automations. To keep existing `script.halloween_atmosphere`, `script.christmas_atmosphere`, and `script.newyear_atmosphere` calls, also install/update the holiday entry points through the UI as described below.

If Home Assistant assigns an entity ID with a suffix such as `_2`, resolve the existing duplicate and set the exact core ID before continuing. Re-import blueprints to get updates, reload scripts, and verify the core IDs again. Import links pointing at `main` become available after the v2.1 PR is merged.

### Complete package (alternative)

[Download the complete v2.1 package](https://raw.githubusercontent.com/ste-ta/holiday-atmosphere-scripts-for-home-assistant/main/packages/holiday_atmosphere.yaml)

1. Download [`packages/holiday_atmosphere.yaml`](packages/holiday_atmosphere.yaml) into your Home Assistant configuration's `packages` directory.
2. If packages are not already enabled, back up your configuration and add the following under your existing `homeassistant:` section. Merge with existing settings rather than adding a second `homeassistant:` key:

   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

3. Run Home Assistant's configuration check before restarting. The package defines the six scripts and `input_text.holiday_atmosphere_session`.
4. Confirm the following entity IDs exist. The internal script and helper IDs must match exactly:

   | Public entry points | Internal scripts/helper |
   | --- | --- |
   | `script.halloween_atmosphere` | `script.holiday_atmosphere_controller` |
   | `script.christmas_atmosphere` | `script.holiday_atmosphere_runner` |
   | `script.newyear_atmosphere` | `script.holiday_atmosphere_light_step` |
   | | `input_text.holiday_atmosphere_session` |

For Home Assistant's package-loading details, see the [official package documentation](https://www.home-assistant.io/docs/configuration/packages/).

### Install through the UI

If you prefer UI-managed scripts:

1. Create a **Text helper** in Settings → Devices & services → Helpers. Set its maximum length to 255, entity ID to `input_text.holiday_atmosphere_session`, and value to `{}`. Reserve it for the controller; its contents are session metadata.
2. Create each of the three internal scripts from its root YAML file, using the script editor's **Edit in YAML** option. Set their entity IDs to those in the table above.
3. Create or update the three holiday scripts from their root YAML files. Preserve their public entity IDs so existing buttons and automations keep working.

Install the shared core through links, pasted UI scripts, or the package, **not more than one method**. Package-managed scripts cannot be edited through the UI; edit their source and regenerate the package instead. Room-preset blueprints can be used with any of these methods.

### Create presets with an import link

After the shared scripts and helper are installed, import the room-preset blueprint:

[![Import blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fste-ta%2Fholiday-atmosphere-scripts-for-home-assistant%2Fblob%2Fmain%2Fblueprints%2Fscript%2Fholiday_preset.yaml)

Select **Create script**, choose your lights, effect, brightness, and pacing in the form, then save it as a preset such as “Living room fireplace.” Run that script from a dashboard button or automation. Create another preset with effect `stop` for a Stop button. The form includes all 16 effects and the same controls as the public entry points.

Blueprints create one script or automation; they cannot provision this package's additional scripts and helper. The preset checks for the shared controller and shows an error if it is missing. **Install the shared core once, then create presets through the import link.** Both download/import links above become available on `main` after the v2.1 PR is merged. Importing or updating a preset does not update the shared core.

The source is [`blueprints/script/holiday_preset.yaml`](blueprints/script/holiday_preset.yaml). For the native import/create workflow, see [Home Assistant's blueprint documentation](https://www.home-assistant.io/docs/blueprint/tutorial/).

### Upgrading from 2.0

Before replacing scripts, call each running 2.0 script with `effect: stop` to restore its lights. If you already switched effects in 2.0, its overwritten backup may require manually restoring your preferred scene.

For existing UI installations, updating those scripts in place and adding the shared scripts/helper is the simplest migration. To move to package installation, back up the existing script configurations, remove the old definitions, install the package, and verify that the public entity IDs in your dashboards and automations still match.

A previously installed script will not gain the shared dependencies just by pasting a new holiday file. Pacing and some effect timing/palettes also change in 2.1; see [the changelog](CHANGELOG.md).

## Start, switch, and stop

Run a holiday entry point from Home Assistant's Actions tool or an automation:

```yaml
action: script.christmas_atmosphere
data:
  lights:
    - light.living_room
    - light.hallway
  effect: xmas_fireplace
  brightness_max: 150
  pacing: conservative
  gentle: true
  duration: 1800
```

This starts the background runner and returns once the controller has processed the request. Calling any holiday entry point again replaces the current effect. The original scene is preserved when the expanded target list is unchanged. Changing targets restores the old scene before capturing a new one.

Stop from any holiday entry point; no light list is needed:

```yaml
action: script.halloween_atmosphere
data:
  effect: stop
```

Explicit Stop restores by default. To deliberately leave the current light state and discard the backup:

```yaml
action: script.christmas_atmosphere
data:
  effect: stop
  restore_on_stop: false
```

`restore_on_stop: false` when **starting** an effect applies to its automatic completion. A later explicit Stop still defaults to restoration unless you also pass false with that stop request.

### Controls

| Field | Default | Behavior |
| --- | --- | --- |
| `lights` | none | Required to start. One light ID or a nonempty list. Home Assistant light groups expand to individual members. Duplicate IDs are removed. |
| `effect` | none | Required on holiday entry points; choose from that holiday's menu. |
| `brightness_max` | 255 | Integer ceiling from 1–255. Applies to effect frames, not restoration. |
| `speed` | 1 | 0.25–4. Divides ambient holds and transition durations; higher values are faster. Does not reduce the pacing floor or change countdown deadlines. |
| `duration` | 0 | Maximum effect duration in seconds, up to 86400. Zero means unlimited for repeating effects. Finite effects still finish naturally. |
| `pacing` | balanced | Minimum delay after each light action: conservative = 1000 ms, balanced = 250 ms, fast = 100 ms. These are tuning profiles, not reliability guarantees. |
| `gentle` | false | Rejects flashing effects before interrupting an active show. Choose an ambient effect instead. |
| `restore_on_stop` | true | Restore on automatic completion; on explicit Stop, false deliberately discards the backup. Target changes always restore the old targets. |
| `group_updates` | false | One common frame per action for all available targets, instead of separate randomized per-bulb frames. Does not guarantee simultaneous physical updates or Zigbee groupcast. |
| `countdown_seconds` | 10 | New Year only. Countdown length from 1–86400 seconds, unless a target timestamp is provided. |
| `countdown_target` | empty | New Year countdown only. Future ISO 8601 timestamp including timezone, such as `2027-01-01T00:00:00+01:00`. Overrides countdown length. |

Invalid requests abort with a message in the script trace/log before stopping an active show. All requested entity IDs must exist; available selected bulbs must support a color mode. Unavailable bulbs are excluded from new snapshots and skipped during frame updates. Bulbs excluded at startup are not added to that session if they later recover.

### Dashboard button

```yaml
type: button
name: Christmas fireplace
tap_action:
  action: perform-action
  perform_action: script.christmas_atmosphere
  data:
    lights:
      - light.living_room
    effect: xmas_fireplace
    brightness_max: 150
    gentle: true
```

### Run a timed show from another script

```yaml
alias: Christmas evening
sequence:
  - action: script.christmas_atmosphere
    data:
      lights: [light.living_room]
      effect: xmas_tree
      duration: 180
  - delay: 180
  - action: script.christmas_atmosphere
    data:
      lights: [light.living_room]
      effect: xmas_snowfall
      duration: 180
```

The holiday entry points dispatch the shared background runner. `script.turn_on` is also supported, with parameters nested under `data.variables`; it returns immediately. There is **no `wait` option**. To wait for a show, check that the runner entity is off; allow the controller to process the start first. See [Home Assistant's script calling documentation](https://www.home-assistant.io/actions/script.turn_on/).

### Countdown ending at midnight

```yaml
action: script.newyear_atmosphere
data:
  lights: [light.party_room]
  effect: nye_countdown
  countdown_target: '2027-01-01T00:00:00+01:00'
  group_updates: true
  pacing: balanced
  restore_on_stop: false
```

The countdown schedules ten beats with decreasing periods against the timestamp. It is not a continuous ten-minute flashing loop. When hardware/action latency or pacing cannot fit a scheduled phase, the runner skips that expired phase instead of queuing increasingly late commands. Individual lights can therefore show fewer flashes than requested. Actual device delivery is not a precision clock.

Use a separate midnight automation to start `nye_midnight_flash` or `nye_confetti`. Give the countdown a concrete future date; do not reuse an expired timestamp. A session token prevents the old countdown's completion request from stopping the newer show.

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

## Restoration and reliability

The controller captures `scene.holiday_atmosphere_backup` once per target session. It serializes requests, stops the old runner before switching, and only removes the backup after the restore action returns successfully. If a saved light is unavailable or the restore action raises an error, the runner stops and the backup remains. Bring the bulb back online and retry `effect: stop`. Do not use `restore_on_stop: false` unless you intend to discard it.

Scene action success is not proof that every physical bulb reached the exact saved brightness or color; integrations can report success before device delivery. Inspect the lights after a failed connection or use your preferred normal scene as recovery.

Dynamic scenes disappear when Home Assistant restarts or scenes reload. The show also stops on a script reload/restart, and an interrupted runner cannot execute automatic cleanup. A manual `script.turn_off` stops updates without restoration. Use the public Stop action for normal shutdown; after a Home Assistant restart, restore a known normal scene if needed. Reserve the backup scene and session-helper entity IDs for this project.

The light-update action is best effort: individual action failures appear in traces/logs and do not end the show. There is no automatic retry or claim of recovering a frozen bulb. If all targets become unavailable during a show, the runner still waits between attempts rather than spinning in an empty loop.

Pacing is measured per Home Assistant action. Shared-frame actions can fan out into multiple device commands. More lights lengthen individual-frame sweeps; balanced pacing adds at least 2.5 seconds for ten individual updates. Start with a small set of lights, compare profiles, and record the bulb models, bridge/integration, Home Assistant version, and observed failures. This release has no physical-hardware qualification matrix and makes no universal Hue, Zigbee, or WLED reliability claim.

For device-native animation, consider integration-supported presets instead of rapid HA actions: [WLED presets and effects](https://www.home-assistant.io/integrations/wled/) and [Hue scenes](https://www.home-assistant.io/integrations/hue/) can move more animation work onto the device or bridge. They are alternatives to evaluate; this runner does not automatically select them.

`duration` bounds when new effect commands are sent. An in-flight action, its pacing delay, and restoration can finish later. It is not a hard real-time timeout.

## Customize and develop

Edit palettes and frame patterns in `holiday-atmosphere-runner.yaml`. Lifecycle handling belongs in `holiday-atmosphere-controller.yaml`; pacing and brightness capping belong in `holiday-atmosphere-light-step.yaml`. Add a new effect to the controller's allowed list, its holiday selector, and the runner. Mark flashing patterns in the controller's exclusion list.

The package and core blueprints are generated from the root script files. Regenerate them after changes:

```sh
python tools/build_package.py
python tools/build_package.py --check
```

For regression checks on the minimum supported engine:

```sh
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python --prerelease=allow -r requirements-test.txt
.venv/bin/python -m pytest -q
```

Tests execute the shipped YAML in Home Assistant's real script engine with simulated service responses and accelerated time. They cover restoration, target changes, cross-holiday concurrency, rejected inputs, pacing, brightness caps, stale completion requests, countdown deadlines, and every effect. They do not simulate Zigbee delivery or certify physical devices. CI also checks Home Assistant 2026.10.0 on Python 3.14.

See [CHANGELOG.md](CHANGELOG.md) for release history. Contributions should include a trace or reproduction, hardware/integration details where relevant, and regression coverage for behavior changes.

## License

These projects are provided as-is for personal and commercial use. Feel free to modify and redistribute.
