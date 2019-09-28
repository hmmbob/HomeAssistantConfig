"""
Support for TOON thermostat.
Only the rooted version.

configuration.yaml

climate:
  - platform: toon_climate
    name: TOON Thermostat
    host: <IP_ADDRESS>
    port: 10080
    scan_interval: 10
"""
import logging
import json
import requests
import voluptuous as vol
from typing import Any, Dict, List, Optional

from homeassistant.components.climate import (ClimateDevice, PLATFORM_SCHEMA)
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_HOME,
    PRESET_SLEEP,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
)

from homeassistant.const import (
    CONF_NAME,
    CONF_HOST,
    CONF_PORT,
    TEMP_CELSIUS,
    ATTR_TEMPERATURE,
)

from homeassistant.helpers.typing import HomeAssistantType
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE
SUPPORT_PRESETS = [PRESET_AWAY, PRESET_COMFORT, PRESET_HOME, PRESET_SLEEP]
SUPPORT_MODES = [HVAC_MODE_HEAT, HVAC_MODE_OFF]

DEFAULT_NAME = 'TOON Thermostat'
DEFAULT_TIMEOUT = 5
DEFAULT_MAX_TEMP = 30.0
DEFAULT_MIN_TEMP = 6.0
BASE_URL = 'http://{0}:{1}{2}'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=10800): cv.positive_int,
})

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Toon thermostat."""
    add_devices([ThermostatDevice(config.get(CONF_NAME), config.get(CONF_HOST),
                            config.get(CONF_PORT))])

# pylint: disable=abstract-method
# pylint: disable=too-many-instance-attributes
class ThermostatDevice(ClimateDevice):
    """Representation of a TOON climate device."""

    def __init__(self, name, host, port) -> None:
        """Initialize the TOON climate device."""
        self._data = None
        self._name = name
        self._host = host
        self._port = port

        self._current_temperature = None
        self._target_temperature = None
        self._heating = False
        self._burner_info = None
        self._modulation_level = None
        self._program_state = None
        self._hvac_mode = HVAC_MODE_HEAT
        self._preset = None
        self.update()

    @staticmethod
    def do_api_request(url):
        """Does an API request."""
        req = requests.get(url, timeout=DEFAULT_TIMEOUT)
        _LOGGER.debug("API request %s", url)
        if req.status_code != requests.codes.ok:
            _LOGGER.exception("API request returned error %d", req.status_code)
        else:
            _LOGGER.debug("API request returned OK %d", req.status_code)

        """Fix invalid JSON output"""
        reqinvalid = req.text
        reqvalid = reqinvalid.replace('",}', '"}')

        return json.loads(req.text)

    @property
    def should_poll(self):
        """Polling needed for thermostat."""
        return True

    def update(self) -> None:
        """Update local data with thermostat data."""
        _LOGGER.debug("Update called")
        self._data = self.do_api_request(BASE_URL.format(
            self._host,
            self._port,
            '/happ_thermstat?action=getThermostatInfo'))
        self._current_temperature = int(self._data['currentTemp'])/100
        self._target_temperature = int(self._data['currentSetpoint'])/100
        self._program_state = int(self._data['programState'])
        self._burner_info = int(self._data['burnerInfo'])
        self._modulation_level = int(self._data['currentModulationLevel'])

        state = int(self._data['activeState'])
        if state == 0:
            self._preset = PRESET_COMFORT
        elif state == 1:
            self._preset = PRESET_HOME
        elif state == 2:
            self._preset = PRESET_SLEEP
        elif state == 3:
            self._preset = PRESET_AWAY
        else:
            self._preset = None

        self._heating = self._burner_info == 1

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def name(self) -> str:
        """Return the name of the thermostat."""
        return self._name

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        """Return the current state of the burner."""
        return {"burner_info": self._burner_info, "modulation_level": self._modulation_level}

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self) -> Optional[float]:
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self) -> Optional[float]:
        """Return the temperature we try to reach."""
        return self._target_temperature

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return DEFAULT_MIN_TEMP

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return DEFAULT_MAX_TEMP

    def set_preset_mode(self, preset_mode) -> None:
        """Set HVAC mode (comfort, home, sleep, away)."""
        if preset_mode == "comfort":
            state = 0
        elif preset_mode == "home":
            state = 1
        elif preset_mode == "sleep":
            state = 2
        elif preset_mode == "away":
            state = 3
        else:
            state = -1

        self._data = self.do_api_request(BASE_URL.format(
            self._host,
            self._port,
            '/happ_thermstat?action=changeSchemeState'
            '&state=2&temperatureState='+str(state)))
        _LOGGER.debug("Set TOON preset mode to %s (value %s)", str(preset_mode),
                      str(state))
        self._preset = preset_mode
        

    def set_temperature(self, **kwargs) -> None:
        """Set target temperature."""
        target_temperature = kwargs.get(ATTR_TEMPERATURE)
        if target_temperature  is None:
            return
        else:
            value = target_temperature*100
            self._data = self.do_api_request(BASE_URL.format(
                self._host,
                self._port,
                '/happ_thermstat?action=setSetpoint&Setpoint='+str(value)))
            _LOGGER.debug("Set TOON target temp to %s°C (value %s)", str(target_temperature), str(value))
        self._target_temperature = target_temperature

    @property
    def hvac_mode(self) -> str:
        """Return the current operation mode."""
        return self._hvac_mode

    @property
    def hvac_modes(self) -> List[str]:
        """Return the list of available hvac operation modes."""
        return SUPPORT_MODES

    @property
    def hvac_action(self) -> Optional[str]:
        """Return the current running hvac operation."""
        if self._heating:
            return CURRENT_HVAC_HEAT
        if self._program_state == 0:
            return CURRENT_HVAC_OFF
        else:
            return CURRENT_HVAC_IDLE

    @property
    def preset_mode(self) -> Optional[str]:
        """Return the current preset mode, e.g., home, away, temp."""
        if self._preset is not None:
            return self._preset.lower()
        return None

    @property
    def preset_modes(self) -> List[str]:
        """List of available preset modes."""
        return SUPPORT_PRESETS

    def set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        _LOGGER.debug("Set TOON hvac mode to %s", str(hvac_mode))

        """Turn off/on TOON heating program."""
        if hvac_mode == 'off':
            self._data = self.do_api_request(BASE_URL.format(
                self._host,
                self._port,
                '/happ_thermstat?action=changeSchemeState'
                '&state=0'))
            self._hvac_mode = HVAC_MODE_OFF
        elif hvac_mode == 'heat':
            self._data = self.do_api_request(BASE_URL.format(
                self._host,
                self._port,
                '/happ_thermstat?action=changeSchemeState'
                '&state=1'))
            self._hvac_mode = HVAC_MODE_HEAT
