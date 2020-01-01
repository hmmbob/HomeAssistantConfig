"""
Support for reading Smart Meter data using TOON thermostats meteradapter.
Only works for rooted TOON.

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

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, CONF_RESOURCES
    )
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

BASE_URL = 'http://{0}:{1}/hdrv_zwave?action=getDevices.json'
_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=10)

SENSOR_PREFIX = 'TOON '
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
    vol.Required(CONF_RESOURCES, default=list(SENSOR_TYPES)):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the TOON Smart Meter sensors."""

    scan_interval = config.get(CONF_SCAN_INTERVAL)
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)

    data = ToonSmartMeterData(host, port)

    try:
        await data.async_update()
    except ValueError as err:
        _LOGGER.error("Error while fetching data from TOON: %s", err)
        return

    entities = []
    for resource in config[CONF_RESOURCES]:
        sensor_type = resource.lower()
        name = SENSOR_PREFIX + SENSOR_TYPES[resource][0]
        unit = SENSOR_TYPES[resource][1]
        icon = SENSOR_TYPES[resource][2]

        _LOGGER.debug("Adding TOON Smart Meter sensor: {}, {}, {}, {}".format(sensor_type, name, unit, icon))
        entities.append(ToonSmartMeterSensor(data, sensor_type, name, unit, icon))

    async_add_entities(entities, True)

# pylint: disable=abstract-method
class ToonSmartMeterData(object):
    """Handle TOON object and limit updates."""

    def __init__(self, host, port):
        """Initialize the data object."""
        self._host = host
        self._port = port

    def _build_url(self):
        """Build the URL for the requests."""
        url = BASE_URL.format(self._host, self._port)
        _LOGGER.debug("TOON fetch URL: %s", url)
        return url

    @property
    def latest_data(self):
        """Return the latest data object."""
        if self._data:
            return self._data
        return None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Update the data from TOON."""
        try:
            self._data =requests.get(self._build_url(), timeout=10).json()
            _LOGGER.debug("TOON fetched data = %s", self._data)
        except (requests.exceptions.RequestException) as error:
            _LOGGER.error("Unable to connect to TOON: %s", error)
            self._data = None

class ToonSmartMeterSensor(Entity):
    """Representation of a Smart Meter connected to TOON."""

    def __init__(self, data, sensor_type, name, unit, icon):
        """Initialize the sensor."""
        self._data = data
        self._type = sensor_type
        self._name = name
        self._unit = unit
        self._icon = icon

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

    async def async_update(self):
        """Get the latest data and use it to update our sensor state."""

        await self._data.async_update()
        if not self._data:
            _LOGGER.error("Didn't receive data from TOON")
            return
        
        energy = self._data.latest_data

        if self._discovery == False:
            
            _LOGGER.debug("Doing discovery")

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

        if self._type == 'gasused':
            if self._type in self._dev_id:
                self._state = float(energy[self._dev_id[self._type]]["CurrentGasFlow"])/1000

        elif self._type == 'gasusedcnt':
            if self._type in self._dev_id:
                self._state = float(energy[self._dev_id[self._type]]["CurrentGasQuantity"])/1000

        elif self._type == 'elecusageflowpulse':
            if 'dev_3.2' in energy:
                self._state = energy["dev_3.2"]["CurrentElectricityFlow"]
            elif 'dev_2.2' in energy:
                self._state = energy["dev_2.2"]["CurrentElectricityFlow"]
            elif 'dev_4.2' in energy:
                self._state = energy["dev_4.2"]["CurrentElectricityFlow"]

        elif self._type == 'elecusagecntpulse':
            if 'dev_3.2' in energy:
                self._state = float(energy["dev_3.2"]["CurrentElectricityQuantity"])/1000
            elif 'dev_2.2' in energy:
                self._state = float(energy["dev_2.2"]["CurrentElectricityQuantity"])/1000
            elif 'dev_4.2' in energy:
                self._state = float(energy["dev_4.2"]["CurrentElectricityQuantity"])/1000

        elif self._type == 'elecusageflowlow':
            if self._type in self._dev_id:
                self._state = energy[self._dev_id[self._type]]["CurrentElectricityFlow"]

        elif self._type == 'elecusagecntlow':
            if self._type in self._dev_id:
                self._state = float(energy[self._dev_id[self._type]]["CurrentElectricityQuantity"])/1000

        elif self._type == 'elecusageflowhigh':
            if self._type in self._dev_id:
                self._state = energy[self._dev_id[self._type]]["CurrentElectricityFlow"]

        elif self._type == 'elecusagecnthigh':
            if self._type in self._dev_id:
                self._state = float(energy[self._dev_id[self._type]]["CurrentElectricityQuantity"])/1000

        elif self._type == 'elecprodflowlow':
            if self._type in self._dev_id:
                self._state = energy[self._dev_id[self._type]]["CurrentElectricityFlow"]

        elif self._type == 'elecprodcntlow':
            if self._type in self._dev_id:
                self._state = float(energy[self._dev_id[self._type]]["CurrentElectricityQuantity"])/1000

        elif self._type == 'elecprodflowhigh':
            if self._type in self._dev_id:
                self._state = energy[self._dev_id[self._type]]["CurrentElectricityFlow"]

        elif self._type == 'elecprodcnthigh':
            if self._type in self._dev_id:
                self._state = float(energy[self._dev_id[self._type]]["CurrentElectricityQuantity"])/1000

        elif self._type == 'elecsolar':
            if 'dev_2.3' in energy:
                self._state = energy["dev_2.3"]["CurrentElectricityFlow"]
            elif 'dev_4.3' in energy:
                self._state = energy["dev_4.3"]["CurrentElectricityFlow"]

        elif self._type == 'elecsolarcnt':
            if 'dev_2.3' in energy:
                self._state = float(energy["dev_2.3"]["CurrentElectricityQuantity"])/1000
            elif 'dev_4.3' in energy:
                self._state = float(energy["dev_4.3"]["CurrentElectricityQuantity"])/1000

        elif self._type == 'heat':
            if 'dev_2.8' in energy:
                self._state = float(energy["dev_2.8"]["CurrentHeatQuantity"])/1000
            elif 'dev_4.8' in energy:
                self._state = float(energy["dev_4.8"]["CurrentHeatQuantity"])/1000

        _LOGGER.debug("Device: {} State: {}".format(self._type, self._state))