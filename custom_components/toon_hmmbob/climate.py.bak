"""
Support for Eneco's Toon thermostats.
Only the rooted version.

configuration.yaml

climate:
  - platform: toon
    name: Toon Thermostat
    host: IP_ADDRESS
    port: 10080
    scan_interval: 10
"""
import logging
import json
import voluptuous as vol
import requests

from homeassistant.components.climate import (ClimateDevice, PLATFORM_SCHEMA)
from homeassistant.components.climate.const import (
    STATE_AUTO, STATE_COOL, STATE_ECO, STATE_HEAT,
    SUPPORT_OPERATION_MODE, SUPPORT_TARGET_TEMPERATURE,
    STATE_MANUAL, SUPPORT_HOLD_MODE, ATTR_HOLD_MODE)
from homeassistant.const import (
    ATTR_TEMPERATURE, CONF_NAME, CONF_HOST, CONF_PORT, TEMP_CELSIUS,
    PRECISION_HALVES, STATE_OFF)
import homeassistant.helpers.config_validation as cv

SUPPORT_FLAGS = (SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE | SUPPORT_HOLD_MODE)

HA_TOON = {
    STATE_AUTO: 'Comfort',
    STATE_HEAT: 'Home',
    STATE_COOL: 'Sleep',
    STATE_ECO: 'Away',
    STATE_MANUAL: "Manual"
}
TOON_HA = {value: key for key, value in HA_TOON.items()}

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Toon Thermostat'
DEFAULT_TIMEOUT = 5
BASE_URL = 'http://{0}:{1}{2}'

ATTR_MODE = 'mode'
ATTR_BURNER_INFO = 'burner_info'

MIN_TEMPERATURE = 6
MAX_TEMPERATURE = 30

TEMPERATURE_HOLD = 'temp'
VACATION_HOLD = 'vacation'
AWAY_MODE = 'away'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=10800): cv.positive_int,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Toon thermostat."""
    add_devices([ThermostatDevice(config.get(CONF_NAME), config.get(CONF_HOST),
                            config.get(CONF_PORT))])

class ThermostatDevice(ClimateDevice):
    """Representation of a Toon thermostat."""

    def __init__(self, name, host, port):
        """Initialize the thermostat."""
        self._data = None
        self._name = name
        self._host = host
        self._port = port

        self._state = 1
        self._temperature = None
        self._setpoint = None
        self._burnerinfo = None
        self._operation_list = [
            STATE_AUTO,
            STATE_HEAT,
            STATE_COOL,
            STATE_ECO,
            STATE_MANUAL
        ]
        self._operation_mode = STATE_HEAT
        _LOGGER.debug("Init called")
        self.update()

    @staticmethod
    def do_api_request(url):
        """Does an API request."""
        req = requests.get(url, timeout=DEFAULT_TIMEOUT)
        if req.status_code != requests.codes.ok:
            _LOGGER.exception("Error doing API request")
        else:
            _LOGGER.debug("API request ok %d", req.status_code)

        """Fixes invalid JSON output by TOON"""
        reqinvalid = req.text
        reqvalid = reqinvalid.replace('",}', '"}')
        return json.loads(req.text)
        
    @property
    def state(self):
        """Return the current state."""
        return self._operation_mode

    @property
    def _current_hold_mode(self):
        return 'away'

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return MIN_TEMPERATURE

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return MAX_TEMPERATURE

    @property
    def precision(self):
        """Return the precision of the system."""
        return PRECISION_HALVES

    @property
    def should_poll(self):
        """Polling needed for thermostat."""
        _LOGGER.debug("Should_Poll called")
        return True

    def update(self):
        """Update the data from the thermostat."""
        self._data = self.do_api_request(BASE_URL.format(
            self._host,
            self._port,
            '/happ_thermstat?action=getThermostatInfo'))
        self._setpoint = int(self._data['currentSetpoint'])/100
        self._temperature = int(self._data['currentTemp'])/100
        self._state = int(self._data['activeState'])
        self._burner_info = int(self._data['burnerInfo'])
        if self._state == -1:
            self._operation_mode = STATE_MANUAL
        else:
            self._operation_mode = self._operation_list[self._state]
        _LOGGER.debug("Update called")

    @property
    def operation_list(self):
        """List of available operation modes."""
        return self._operation_list

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def name(self):
        """Return the name of the thermostat."""
        return self._name

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        return {
            ATTR_MODE: self._operation_mode,
            "climate_list": {"away","home","holiay", "comfort"},
            ATTR_HOLD_MODE: "away",
            ATTR_BURNER_INFO: self._burner_info
        }
        
    @property
    def current_hold_mode(self):
        """Return current hold mode."""
        return AWAY_MODE
        
    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._setpoint

    @property
    def current_operation(self):
        """Return the current state of the thermostat."""
        _LOGGER.debug("current operation mode %s, %s", self._state, self._operation_list[self._state])
        return self._operation_list[self._state]

    def set_hold_mode(self, hold_mode):
        """Set hold mode (away, home, temp, sleep, etc.)."""

    def set_operation_mode(self, operation_mode):
        """Set HVAC mode (comfort, home, sleep, away)."""
        set_op_mode = HA_TOON[operation_mode]
        self._operation_mode = operation_mode
        _LOGGER.debug("set operation mode %s %s", set_op_mode, operation_mode)
        if set_op_mode == "Comfort":
            mode = 0
        elif set_op_mode == "Home":
            mode = 1
        elif set_op_mode == "Sleep":
            mode = 2
        elif set_op_mode == "Away":
            mode = 3
        self._data = self.do_api_request(BASE_URL.format(
            self._host,
            self._port,
            '/happ_thermstat?action=changeSchemeState'
            '&state=2&temperatureState='+str(mode)))

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)*100
        if temperature is None:
            return
        else:
            self._operation_mode = STATE_MANUAL
            self._data = self.do_api_request(BASE_URL.format(
                self._host,
                self._port,
                '/happ_thermstat?action=setSetpoint'
                '&Setpoint='+str(temperature)))
            _LOGGER.debug("Set temperature=%s", str(temperature))