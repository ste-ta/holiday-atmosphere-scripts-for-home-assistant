"""Execute the shipped YAML in HA's real script engine with simulated devices/time."""

import asyncio
from copy import deepcopy
from datetime import datetime, timedelta, UTC
from pathlib import Path

import pytest_asyncio
import yaml
from homeassistant.core import HomeAssistant, Context
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.script_variables import ScriptVariables
from homeassistant.helpers.script import Script, _ScriptRun, async_validate_actions_config
from homeassistant.util import dt as dt_util

ROOT = Path(__file__).resolve().parents[1]


class ShowHarness:
    def __init__(self, hass):
        self.hass = hass
        self.time = datetime(2026, 12, 31, 22, 59, 0, tzinfo=UTC)
        self.scripts = {}
        self.tasks = []
        self.snapshots = {}
        self.commands = []
        self.capture_count = 0
        self.restore_error = False
        self.capture_error = False
        self.light_error = False
        self.delays = []

    def light(self, name, state="on", brightness=80):
        self.hass.states.async_set(name, state, {
            "brightness": brightness,
            "xy_color": [0.4, 0.4],
            "supported_color_modes": ["xy"],
            "supported_features": 32,
        })

    async def run(self, name="holiday_atmosphere", _context=None, **data):
        script = self.scripts[name]
        data["this"] = self.hass.states.get("script." + name)
        if data.get("effect") == "stop":
            return await script.async_run(data, _context or Context())
        task = asyncio.create_task(script.async_run(data, _context or Context()))
        self.tasks.append(task)
        await self.settle()
        if task.done() and not task.cancelled():
            return task.result()

    async def settle(self, rounds=40):
        for _ in range(rounds):
            await asyncio.sleep(0)

    async def complete(self):
        for _ in range(5000):
            await asyncio.sleep(0)
            if not any(s.is_running for s in self.scripts.values()) and all(t.done() for t in self.tasks):
                for task in self.tasks:
                    if not task.cancelled():
                        task.result()
                return
        raise AssertionError("Show did not complete")

    async def service(self, call):
        data = call.data
        entity_ids = data.get("entity_id", [])
        if isinstance(entity_ids, str):
            entity_ids = [entity_ids]
        if call.domain == "scene":
            if call.service == "create":
                if self.capture_error:
                    raise HomeAssistantError("Snapshot failed")
                name = "scene." + data["scene_id"]
                entities = data["snapshot_entities"]
                self.snapshots[name] = {
                    entity: (self.hass.states.get(entity).state, dict(self.hass.states.get(entity).attributes))
                    for entity in entities
                }
                self.hass.states.async_set(name, "unknown", {"entity_id": entities})
                self.capture_count += 1
            elif call.service == "turn_on":
                if self.restore_error:
                    raise HomeAssistantError("Restore failed")
                for entity, (state, attributes) in self.snapshots[entity_ids[0]].items():
                    self.hass.states.async_set(entity, state, deepcopy(attributes))
            elif call.service == "delete":
                del self.snapshots[entity_ids[0]]
                self.hass.states.async_remove(entity_ids[0])
        elif call.domain == "light":
            self.commands.append((self.time.timestamp(), list(entity_ids), dict(data)))
            if self.light_error:
                raise HomeAssistantError("Bulb unreachable")
            for entity in entity_ids:
                attributes = dict(self.hass.states.get(entity).attributes)
                attributes.update({key: data[key] for key in ("brightness", "xy_color")})
                self.hass.states.async_set(entity, "on", attributes)


@pytest_asyncio.fixture
async def show(tmp_path, monkeypatch):
    hass = HomeAssistant(str(tmp_path))
    harness = ShowHarness(hass)
    monkeypatch.setattr(dt_util, "utcnow", lambda: harness.time)
    monkeypatch.setattr(dt_util, "now", lambda time_zone=None: harness.time)

    async def delay(run):
        seconds = run._get_pos_time_period_template("delay").total_seconds()
        harness.delays.append(seconds)
        harness.time += timedelta(seconds=seconds)
        await asyncio.sleep(0)

    delay_method = "_async_delay_step" if hasattr(_ScriptRun, "_async_delay_step") else "_async_step_delay"
    monkeypatch.setattr(_ScriptRun, delay_method, delay)
    config = yaml.safe_load((ROOT / "holiday-atmosphere.yaml").read_text())
    sequence = await async_validate_actions_config(hass, cv.SCRIPT_SCHEMA(config["sequence"]))
    harness.scripts["holiday_atmosphere"] = Script(
        hass, sequence, "holiday_atmosphere", "script", script_mode=config["mode"],
        variables=ScriptVariables(config["variables"]),
    )
    hass.states.async_set("script.holiday_atmosphere", "off")
    for domain, services in {"scene": ["create", "turn_on", "delete"], "light": ["turn_on"]}.items():
        for service in services:
            hass.services.async_register(domain, service, harness.service)
    harness.light("light.one", brightness=80)
    harness.light("light.two", state="off", brightness=120)
    yield harness
    for script in harness.scripts.values():
        await script.async_stop()
    for task in harness.tasks:
        if not task.done():
            task.cancel()
    await asyncio.gather(*harness.tasks, return_exceptions=True)
    await hass.async_stop(force=True)
