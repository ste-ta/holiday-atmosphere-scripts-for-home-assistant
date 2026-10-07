from pathlib import Path

from homeassistant.components.blueprint import BLUEPRINT_SCHEMA
from homeassistant.components.blueprint.models import Blueprint, BlueprintInputs
from homeassistant.components.script.config import SCRIPT_ENTITY_SCHEMA
from homeassistant.helpers.script import Script, async_validate_actions_config
from homeassistant.util import yaml as ha_yaml

ROOT = Path(__file__).resolve().parents[1]


def substitute(inputs):
    path = ROOT / "blueprints/script/holiday_atmosphere.yaml"
    blueprint = Blueprint(ha_yaml.load_yaml(str(path)), expected_domain="script", schema=BLUEPRINT_SCHEMA)
    supplied = BlueprintInputs(blueprint, {"use_blueprint": {"path": path.name, "input": inputs}})
    supplied.validate()
    return supplied.async_substitute()


async def test_native_blueprint_import_and_substitution(show):
    SCRIPT_ENTITY_SCHEMA(substitute({"default_lights": ["light.one"]}))


async def test_one_imported_script_starts_switches_and_restores_without_dependencies(show):
    config = SCRIPT_ENTITY_SCHEMA(substitute({"default_lights": ["light.one"], "default_effect": "xmas_fireplace"}))
    sequence = await async_validate_actions_config(show.hass, config["sequence"])
    show.scripts["holiday_atmosphere"] = Script(
        show.hass, sequence, "Holiday atmosphere", "script", script_mode=config["mode"],
        variables=config["variables"],
    )
    await show.run(brightness_max=100)
    assert show.commands
    assert all(data["brightness"] <= 100 for _, _, data in show.commands)
    await show.run(effect="hell", brightness_max=100)
    assert show.capture_count == 1
    await show.run(effect="stop")
    assert show.hass.states.get("light.one").attributes["brightness"] == 80
    assert not show.snapshots
    # No script or input_text services exist in this harness.
    assert not show.hass.services.has_service("input_text", "set_value")
    assert not show.hass.services.has_service("script", "turn_on")


async def test_installer_can_choose_any_script_name(show):
    config = SCRIPT_ENTITY_SCHEMA(substitute({"default_lights": ["light.one"]}))
    sequence = await async_validate_actions_config(show.hass, config["sequence"])
    show.scripts["living_room_holidays"] = Script(
        show.hass, sequence, "Living room holidays", "script", script_mode=config["mode"],
        variables=config["variables"],
    )
    show.hass.states.async_set("script.living_room_holidays", "off")
    await show.run("living_room_holidays")
    assert "scene.holiday_atmosphere_backup_living_room_holidays" in show.snapshots
    await show.run("living_room_holidays", effect="stop")
    assert show.hass.states.get("light.one").attributes["brightness"] == 80
    assert not show.snapshots
