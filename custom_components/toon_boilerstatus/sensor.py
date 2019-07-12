"""
Support for reading opentherm boilerstatus data through Eneco's Toon thermostats.
Only works for rooted Toon where ToonStore and the BoilerStatus app are installed.

configuration.yaml

sensor:
  - platform: toon_boilerstatus
    host: IP_ADDRESS
    port: 10080
    scan_interval: 10
    resources:
      - boilersetpoint
      - boilerintemp
      - boilerouttemp
      - boilerpressure
      - boilermodulationlevel
      - roomtemp
      - roomtempsetpoint
"""
import logging
from datetime import timedelta
import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, CONF_RESOURCES)
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

BASE_URL = 'http://{0}:{1}{2}'
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=10)

SENSOR_PREFIX = 'Toon '

SENSOR_TYPES = {
    'boilersetpoint': ['Boiler SetPoint', '°C', 'mdi:thermometer'],
    'boilerintemp': ['Boiler InTemp', '°C', 'mdi:thermometer'],
    'boilerouttemp': ['Boiler OutTemp', '°C', 'mdi:thermometer'],
    'boilerpressure': ['Boiler Pressure', 'Bar', 'mdi:gauge'],
    'boilermodulationlevel': ['Boiler Modulation', '%', 'mdi:fire'],
    'roomtemp': ['Room Temp', '°C', 'mdi:thermometer'],
    'roomtempsetpoint': ['Room Temp SetPoint', '°C', 'mdi:thermometer'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=10800): cv.positive_int,
    vol.Required(CONF_RESOURCES, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the Toon smartmeter sensors."""
    scan_interval = config.get(CONF_SCAN_INTERVAL)
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)

    try:
        data = ToonData(host, port)
    except requests.exceptions.HTTPError as error:
        _LOGGER.error(error)
        return False

    entities = []

    for resource in config[CONF_RESOURCES]:
        sensor_type = resource.lower()

        if sensor_type not in SENSOR_TYPES:
            SENSOR_TYPES[sensor_type] = [
                sensor_type.title(), '', 'mdi:flash']

        entities.append(ToonBoilerStatusSensor(data, sensor_type))

    add_entities(entities)


# pylint: disable=abstract-method
class ToonData(object):
    """Representation of a Toon thermostat."""

    def __init__(self, host, port):
        """Initialize the thermostat."""
        self._host = host
        self._port = port
        self.data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Update the data from the thermostat."""
        response = requests.get(BASE_URL.format(self._host, self._port, '/boilerstatus/boilervalues.txt'), timeout=5, headers={'accept-encoding': None})
        _LOGGER.debug("Data = %s", response)

        if response:
          self.data = response.json()
        else:
          _LOGGER.warning("Empty response for command: %s", self._command_state)
          self.data = None
 
class ToonBoilerStatusSensor(Entity):
    """Representation of a OpenTherm Boiler connected to Toon."""

    def __init__(self, data, sensor_type):
        """Initialize the sensor."""
        self.data = data
        self.type = sensor_type
        self._last_updated = None
        self._name = SENSOR_PREFIX + SENSOR_TYPES[self.type][0]
        self._unit = SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][2]
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    @property
    def device_state_attributes(self):
        """Return the state attributes of this device."""
        attr = {}
        if self._last_updated is not None:
            attr['Last Updated'] = self._last_updated
        return attr

    def update(self):
        """Get the latest data and use it to update our sensor state."""
        self.data.update()
        if self.data.data is None:
            _LOGGER.error("Empty response for boilerstatus")
            return None
        else:
          boilerstatus = self.data.data
  
          if 'sampleTime' in boilerstatus:
              self._last_updated = boilerstatus["sampleTime"]
  
          if self.type == 'boilersetpoint':
              if 'boilerSetpoint' in boilerstatus:
                  self._state = float(boilerstatus["boilerSetpoint"])
  
          elif self.type == 'boilerintemp':
              if 'boilerInTemp' in boilerstatus:
                  self._state = float(boilerstatus["boilerInTemp"])
  
          elif self.type == 'boilerouttemp':
              if 'boilerOutTemp' in boilerstatus:
                  self._state = float(boilerstatus["boilerOutTemp"])
  
          elif self.type == 'boilerpressure':
              if 'boilerPressure' in boilerstatus:
                  self._state = float(boilerstatus["boilerPressure"])
  
          elif self.type == 'boilermodulationlevel':
              if 'boilerModulationLevel' in boilerstatus:
                  self._state = float(boilerstatus["boilerModulationLevel"])
  
          elif self.type == 'roomtemp':
              if 'roomTemp' in boilerstatus:
                  self._state = float(boilerstatus["roomTemp"])
  
          elif self.type == 'roomtempsetpoint':
              if 'roomTempSetpoint' in boilerstatus:
                  self._state = float(boilerstatus["roomTempSetpoint"])
  