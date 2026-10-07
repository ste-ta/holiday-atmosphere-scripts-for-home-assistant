from pathlib import Path

import pytest
from homeassistant.components.blueprint import BLUEPRINT_SCHEMA
from homeassistant.components.blueprint.models import Blueprint, BlueprintInputs
from homeassistant.components.script.config import SCRIPT_ENTITY_SCHEMA
from homeassistant.core import Context
from homeassistant.helpers.script import Script, async_validate_actions_config
from homeassistant.util import yaml as ha_yaml

ROOT = Path(__file__).resolve().parents[1]


def substitute(path, inputs):
    blueprint = Blueprint(ha_yaml.load_yaml(str(path)), expected_domain="script", schema=BLUEPRINT_SCHEMA)
    supplied = BlueprintInputs(blueprint, {"use_blueprint": {"path": path.name, "input": inputs}})
    supplied.validate()
    return supplied.async_substitute()


@pytest.mark.parametrize("file", [
    "holiday_atmosphere_controller.yaml", "holiday_atmosphere_runner.yaml",
    "holiday_atmosphere_light_step.yaml", "holiday_preset.yaml",
])
async def test_native_blueprint_import_and_substitution(show, file):
    config = substitute(ROOT / "blueprints/script" / file, {"lights": ["light.one"]} if file == "holiday_preset.yaml" else {})
    SCRIPT_ENTITY_SCHEMA(config)


async def test_imported_preset_starts_and_stop_preset_restores(show):
    async def preset(inputs):
        config = SCRIPT_ENTITY_SCHEMA(substitute(ROOT / "blueprints/script/holiday_preset.yaml", inputs))
        sequence = await async_validate_actions_config(show.hass, config["sequence"])
        script = Script(show.hass, sequence, "Room preset", "script", script_mode=config["mode"])
        return await script.async_run({}, Context())

    await preset({"lights": ["light.one"], "effect": "xmas_fireplace", "brightness_max": 100})
    await show.settle()
    assert show.commands
    assert all(data["brightness"] <= 100 for _, _, data in show.commands)
    await preset({"effect": "stop"})
    assert show.hass.states.get("light.one").attributes["brightness"] == 80
    assert not show.snapshots
