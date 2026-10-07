import asyncio
import json
from pathlib import Path

import pytest
import yaml
from homeassistant.components.script.config import SCRIPT_ENTITY_SCHEMA
from homeassistant.exceptions import HomeAssistantError
from homeassistant.core import Context
from homeassistant.helpers.entity import entity_sources

ROOT = Path(__file__).resolve().parents[1]
BACKUP = "scene.holiday_atmosphere_backup"


async def test_all_scripts_pass_ha_schema(show):
    package = yaml.safe_load((ROOT / "packages/holiday_atmosphere.yaml").read_text())
    for script in package["script"].values():
        SCRIPT_ENTITY_SCHEMA(script)


async def test_switch_preserves_original_and_stop_restores(show):
    await show.run("halloween_atmosphere", lights=["light.one", "light.two"], effect="hell")
    await show.settle()
    await show.run("christmas_atmosphere", lights=["light.two", "light.one"], effect="xmas_tree")
    await show.settle()
    assert show.capture_count == 1
    assert len(show.scripts["holiday_atmosphere_runner"]._runs) == 1
    await show.run("newyear_atmosphere", effect="stop")
    assert show.hass.states.get("light.one").attributes["brightness"] == 80
    assert show.hass.states.get("light.two").state == "off"
    assert BACKUP not in show.snapshots


async def test_changed_targets_restore_old_lights_and_start_new_session(show):
    await show.run(effect="hell", lights="light.one")
    await show.settle()
    await show.run(effect="xmas_tree", lights="light.two")
    assert show.hass.states.get("light.one").attributes["brightness"] == 80
    assert show.capture_count == 2
    assert list(show.snapshots[BACKUP]) == ["light.two"]
    await show.run(effect="stop")
    assert show.hass.states.get("light.two").state == "off"


@pytest.mark.parametrize("data", [
    {"effect": "bad", "lights": ["light.one"]},
    {"effect": "hell", "lights": []},
    {"effect": "hell"},
    {"effect": "hell", "lights": ["light.missing"]},
    {"effect": "hell", "lights": [42]},
    {"effect": "hell", "lights": {"light.one": 1}},
    {"effect": "hell", "lights": ["light.one"], "brightness_max": 256},
    {"effect": "hell", "lights": ["light.one"], "speed": 0},
    {"effect": "hell", "lights": ["light.one"], "pacing": "unsafe"},
    {"effect": "lightning", "lights": ["light.one"], "gentle": True},
    {"effect": "hell", "lights": ["light.one"], "restore_on_stop": "false"},
    {"effect": "nye_countdown", "lights": ["light.one"], "countdown_target": "yesterday"},
    {"effect": "nye_countdown", "lights": ["light.one"], "countdown_target": "2027-01-01T00:00:00"},
    {"effect": "hell", "lights": ["light.one"], "brightness_max": True},
    {"effect": "hell", "lights": ["light.one"], "duration": float("inf")},
])
async def test_invalid_requests_do_not_interrupt_active_show(show, data):
    await show.run(effect="xmas_tree", lights="light.one")
    await show.settle()
    snapshot = show.snapshots[BACKUP].copy()
    token = show.hass.states.get("input_text.holiday_atmosphere_session").state
    # HA's stop/error action marks the trace as aborted rather than raising to the caller.
    await show.run(**data)
    assert show.scripts["holiday_atmosphere_runner"].is_running
    assert show.snapshots[BACKUP] == snapshot
    assert show.hass.states.get("input_text.holiday_atmosphere_session").state == token


async def test_restore_error_retains_backup_for_retry(show):
    await show.run(effect="hell", lights="light.one")
    await show.settle()
    show.restore_error = True
    with pytest.raises(HomeAssistantError):
        await show.run(effect="stop")
    assert BACKUP in show.snapshots
    assert not show.scripts["holiday_atmosphere_runner"].is_running
    show.restore_error = False
    await show.run(effect="stop")
    assert show.hass.states.get("light.one").attributes["brightness"] == 80
    assert BACKUP not in show.snapshots


async def test_capture_failure_never_changes_lights(show):
    show.capture_error = True
    with pytest.raises(HomeAssistantError):
        await show.run(effect="hell", lights="light.one")
    assert not show.commands
    assert not show.scripts["holiday_atmosphere_runner"].is_running


async def test_unavailable_saved_light_retains_backup(show):
    await show.run(effect="hell", lights="light.one")
    await show.settle()
    show.hass.states.async_set("light.one", "unavailable")
    await show.run(effect="stop")
    assert BACKUP in show.snapshots
    show.light("light.one")
    await show.run(effect="stop")
    assert show.hass.states.get("light.one").attributes["brightness"] == 80


async def test_deduplication_groups_and_unavailable_targets(show):
    entity_sources(show.hass)["light.room"] = {"domain": "group"}
    show.hass.states.async_set("light.room", "on", {"entity_id": ["light.one", "light.two"], "supported_color_modes": ["xy"]})
    show.hass.states.async_set("light.two", "unavailable")
    await show.run(effect="hell", lights=["light.room", "light.one"])
    await show.settle()
    assert list(show.snapshots[BACKUP]) == ["light.one"]
    assert all(targets == ["light.one"] for _, targets, _ in show.commands)
    await show.run(effect="stop")


async def test_obsolete_timer_does_not_stop_new_effect(show):
    # Multiple starts from the same automation inherit the same HA context.
    context = Context()
    await show.run(effect="hell", lights="light.one", _context=context)
    await show.settle()
    old_token = json.loads(show.hass.states.get("input_text.holiday_atmosphere_session").state)["token"]
    await show.run(effect="xmas_tree", lights="light.one", _context=context)
    await show.run(effect="stop", expected_session=old_token)
    assert show.scripts["holiday_atmosphere_runner"].is_running
    assert BACKUP in show.snapshots
    await show.run(effect="stop")


async def test_duration_brightness_cap_and_pacing(show):
    start = show.time.timestamp()
    await show.run(effect="nye_sparkler", lights="light.one", duration=3, brightness_max=50, pacing="conservative", speed=4)
    await show.complete()
    assert all(data["brightness"] <= 50 for _, _, data in show.commands)
    times = [t for t, _, _ in show.commands]
    assert all(b - a >= 1 for a, b in zip(times, times[1:]))
    assert times[-1] < start + 3
    assert show.hass.states.get("light.one").attributes["brightness"] == 80
    assert BACKUP not in show.snapshots


async def test_completion_can_leave_effect_state(show):
    await show.run(effect="nye_confetti", lights="light.one", duration=1, restore_on_stop=False)
    await show.complete()
    assert show.hass.states.get("light.one").attributes["brightness"] >= 200
    assert BACKUP not in show.snapshots


@pytest.mark.parametrize("targets", [["light.one"], ["light.one", "light.two"]])
async def test_countdown_accelerates_and_ends_at_timestamp(show, targets):
    start = show.time.timestamp()
    end = start + 20
    await show.run(effect="nye_countdown", lights=targets, countdown_target=show.time.replace(minute=59, second=20).isoformat(), group_updates=True, pacing="fast", restore_on_stop=False)
    await show.complete()
    bright = [t for t, _, data in show.commands if data["brightness"] == 255]
    assert len(bright) == 10
    intervals = [b - a for a, b in zip(bright, bright[1:])]
    assert all(b < a for a, b in zip(intervals, intervals[1:]))
    assert show.time.timestamp() == pytest.approx(end, abs=0.002)


async def test_concurrent_holiday_requests_share_one_runner(show):
    await asyncio.gather(
        show.run("halloween_atmosphere", lights="light.one", effect="hell"),
        show.run("christmas_atmosphere", lights="light.one", effect="xmas_tree"),
        show.run("newyear_atmosphere", lights="light.one", effect="nye_champagne"),
    )
    await show.settle()
    assert len(show.scripts["holiday_atmosphere_runner"]._runs) == 1
    assert show.capture_count == 1
    await show.run(effect="stop")


@pytest.mark.parametrize("effect", [
    "hell", "lightning", "graveyard", "halloween", "blood", "xmas_tree",
    "xmas_snowfall", "xmas_fireplace", "xmas_santa", "xmas_dinner", "xmas_party",
    "nye_countdown", "nye_confetti", "nye_midnight_flash", "nye_sparkler", "nye_champagne",
])
async def test_every_effect_runs_and_completes_without_template_errors(show, effect):
    await show.run(effect=effect, lights=["light.one", "light.two"], duration=15, pacing="fast")
    await show.complete()
    assert show.commands
    assert BACKUP not in show.snapshots


async def test_light_service_errors_do_not_crash_timed_show(show):
    show.light_error = True
    await show.run(effect="hell", lights="light.one", duration=3)
    await show.complete()
    assert show.commands
    assert BACKUP not in show.snapshots


async def test_party_reaches_all_modes_including_solo(show):
    await show.run(effect="xmas_party", lights=["light.one", "light.two"], duration=50, pacing="fast", group_updates=True)
    await show.complete()
    assert any(data["brightness"] == 20 and len(targets) == 2 for _, targets, data in show.commands)
    assert any(data["brightness"] == 255 and len(targets) == 1 for _, targets, data in show.commands)


async def test_dinner_highlights_and_base_glow(show, monkeypatch):
    monkeypatch.setattr("random.choice", lambda values: values[0])
    await show.run(effect="xmas_dinner", lights="light.one", duration=20, pacing="fast")
    await show.complete()
    brightness = [data["brightness"] for _, _, data in show.commands]
    assert 140 in brightness and 95 in brightness


async def test_all_lights_becoming_unavailable_still_obey_pacing(show):
    await show.run(effect="nye_sparkler", lights="light.one", duration=10, pacing="conservative")
    await show.settle(rounds=10)
    show.hass.states.async_set("light.one", "unavailable")
    await show.complete()
    assert BACKUP in show.snapshots  # Automatic restoration was deferred.
    assert any(delay == 1 for delay in show.delays)
    assert len(show.delays) < 30


async def test_manual_stop_can_discard_and_is_idempotent(show):
    await show.run(effect="nye_confetti", lights="light.one")
    await show.settle()
    await show.run(effect="stop", restore_on_stop=False)
    assert show.hass.states.get("light.one").attributes["brightness"] >= 200
    assert not show.snapshots
    await show.run(effect="stop")
    assert not show.snapshots
