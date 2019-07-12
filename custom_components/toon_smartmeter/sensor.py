"""
Support for reading SmartMeter data through Eneco's Toon thermostats.
Only works for rooted Toon.

configuration.yaml

sensor:
  - platform: toon_smartmeter
    host: IP_ADDRESS
    port: 10080
    scan_interval: 10
    resources:
      - gasused
      - gasusedcnt
      - elecusageflowpulse
      - elecusagecntpulse
      - elecusageflowlow
      - elecusagecntlow
      - elecusageflowhigh
      - elecusagecnthigh
      - elecprodflowlow
      - elecprodcntlow
      - elecprodflowhigh
      - elecprodcnthigh
      - elecsolar
      - elecsolarcnt
      - heat
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
    'gasused': ['Gas Used Last Hour', 'm3', 'mdi:fire'],
    'gasusedcnt': ['Gas Used Cnt', 'm3', 'mdi:fire'],
    'elecusageflowpulse': ['Power Use', 'Watt', 'mdi:flash'],
    'elecusageflowlow': ['P1 Power Use Low', 'Watt', 'mdi:flash'],
    'elecusageflowhigh': ['P1 Power Use High', 'Watt', 'mdi:flash'],
    'elecprodflowlow': ['P1 Power Prod Low', 'Watt', 'mdi:flash'],
    'elecprodflowhigh': ['P1 Power Prod High', 'Watt', 'mdi:flash'],
    'elecusagecntpulse': ['Power Use Cnt', 'kWh', 'mdi:flash'],
    'elecusagecntlow': ['P1 Power Use Cnt Low', 'kWh', 'mdi:flash'],
    'elecusagecnthigh': ['P1 Power Use Cnt High', 'kWh', 'mdi:flash'],
    'elecprodcntlow': ['P1 Power Prod Cnt Low', 'kWh', 'mdi:flash'],
    'elecprodcnthigh': ['P1 Power Prod Cnt High', 'kWh', 'mdi:flash'],
    'elecsolar': ['P1 Power Solar', 'Watt', 'mdi:weather-sunny'],
    'elecsolarcnt': ['P1 Power Solar Cnt', 'kWh', 'mdi:weather-sunny'],
    'heat': ['P1 Heat', '', 'mdi:fire'],
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

        entities.append(ToonSmartMeterSensor(data, sensor_type))

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
        try:
            self.data = requests.get(BASE_URL.format(self._host, self._port, '/hdrv_zwave?action=getDevices.json'), timeout=5).json()
            _LOGGER.debug("Data = %s", self.data)
        except requests.exceptions.RequestException:
            _LOGGER.error("Error occurred while fetching data.")
            self.data = None
            return False

 
class ToonSmartMeterSensor(Entity):
    """Representation of a SmartMeter connected to Toon."""

    def __init__(self, data, sensor_type):
        """Initialize the sensor."""
        self.data = data
        self.type = sensor_type
        self._name = SENSOR_PREFIX + SENSOR_TYPES[self.type][0]
        self._unit = SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][2]
        self._state = None

        self._discovery = False
        self._dev_id = {}

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
        """Return the state of the sensor. (total/current power consumption/production or total gas used)"""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    def update(self):
        """Get the latest data and use it to update our sensor state."""
        self.data.update()
        energy = self.data.data

        if self._discovery == False:

            for key in energy:
                dev = energy[key]

                if dev['type'] in ['gas', 'HAE_METER_v2_1', 'HAE_METER_v3_1']:
                    self._dev_id['gasused'] = key
                    self._dev_id['gasusedcnt'] = key

                if dev['type'] in ['elec_delivered_lt', 'HAE_METER_v2_5', 'HAE_METER_v3_6']:
                    self._dev_id['elecusageflowlow'] = key
                    self._dev_id['elecusagecntlow'] = key

                if dev['type'] in ['elec_delivered_nt', 'HAE_METER_v2_3', 'HAE_METER_v3_4']:
                    self._dev_id['elecusageflowhigh'] = key
                    self._dev_id['elecusagecnthigh'] = key

                if dev['type'] in ['elec_received_lt', 'HAE_METER_v2_6']:
                    self._dev_id['elecprodflowlow'] = key
                    self._dev_id['elecprodcntlow'] = key

                if dev['type'] in ['elec_received_nt', 'HAE_METER_v2_4']:
                    self._dev_id['elecprodflowhigh'] = key
                    self._dev_id['elecprodcnthigh'] = key

            self._discovery = True

        """Go to http://toon.ip:port/hdrv_zwave?action=getDevices.json and search for dev_"""
        if self.type == 'gasused':
            if self.type in self._dev_id:
                self._state = float(energy[self._dev_id[self.type]]["CurrentGasFlow"])/1000

        elif self.type == 'gasusedcnt':
            if self.type in self._dev_id:
                self._state = float(energy[self._dev_id[self.type]]["CurrentGasQuantity"])/1000

        elif self.type == 'elecusageflowpulse':
            if 'dev_3.2' in energy:
                self._state = energy["dev_3.2"]["CurrentElectricityFlow"]
            elif 'dev_2.2' in energy:
                self._state = energy["dev_2.2"]["CurrentElectricityFlow"]
            elif 'dev_2.6' in energy:
                self._state = energy["dev_2.6"]["CurrentElectricityFlow"]
            elif 'dev_4.2' in energy:
                self._state = energy["dev_4.2"]["CurrentElectricityFlow"]

        elif self.type == 'elecusagecntpulse':
            if 'dev_3.2' in energy:
                self._state = float(energy["dev_3.2"]["CurrentElectricityQuantity"])/1000
            elif 'dev_2.2' in energy:
                self._state = float(energy["dev_2.2"]["CurrentElectricityQuantity"])/1000
            elif 'dev_2.6' in energy:
                self._state = float(energy["dev_2.6"]["CurrentElectricityQuantity"])/1000
            elif 'dev_4.2' in energy:
                self._state = float(energy["dev_4.2"]["CurrentElectricityQuantity"])/1000

        elif self.type == 'elecusageflowlow':
            if self.type in self._dev_id:
                self._state = energy[self._dev_id[self.type]]["CurrentElectricityFlow"]

        elif self.type == 'elecusagecntlow':
            if self.type in self._dev_id:
                self._state = float(energy[self._dev_id[self.type]]["CurrentElectricityQuantity"])/1000

        elif self.type == 'elecusageflowhigh':
            if self.type in self._dev_id:
                self._state = energy[self._dev_id[self.type]]["CurrentElectricityFlow"]

        elif self.type == 'elecusagecnthigh':
            if self.type in self._dev_id:
                self._state = float(energy[self._dev_id[self.type]]["CurrentElectricityQuantity"])/1000

        elif self.type == 'elecprodflowlow':
            if self.type in self._dev_id:
                self._state = energy[self._dev_id[self.type]]["CurrentElectricityFlow"]

        elif self.type == 'elecprodcntlow':
            if self.type in self._dev_id:
                self._state = float(energy[self._dev_id[self.type]]["CurrentElectricityQuantity"])/1000

        elif self.type == 'elecprodflowhigh':
            if self.type in self._dev_id:
                self._state = energy[self._dev_id[self.type]]["CurrentElectricityFlow"]

        elif self.type == 'elecprodcnthigh':
            if self.type in self._dev_id:
                self._state = float(energy[self._dev_id[self.type]]["CurrentElectricityQuantity"])/1000

        elif self.type == 'elecsolar':
            if 'dev_2.3' in energy:
                self._state = energy["dev_2.3"]["CurrentElectricityFlow"]
            elif 'dev_4.3' in energy:
                self._state = energy["dev_4.3"]["CurrentElectricityFlow"]

        elif self.type == 'elecsolarcnt':
            if 'dev_2.3' in energy:
                self._state = float(energy["dev_2.3"]["CurrentElectricityQuantity"])/1000
            elif 'dev_4.3' in energy:
                self._state = float(energy["dev_4.3"]["CurrentElectricityQuantity"])/1000

        elif self.type == 'heat':
            if 'dev_2.8' in energy:
                self._state = float(energy["dev_2.8"]["CurrentHeatQuantity"])/1000
            elif 'dev_4.8' in energy:
                self._state = float(energy["dev_4.8"]["CurrentHeatQuantity"])/1000
