This repo contains my Home Assistant configuration. Home Assistant is open source home automation that puts local control and privacy first. More information can be found at their website, https://www.home-assistant.io.

I started with Home Assistant back in 2018 somewhere, running it in a [Python venv](https://www.home-assistant.io/docs/installation/virtualenv/) directly at a Raspbian installation. I ran into all kind of compatibility issues in the long run, so I decided to switch to a [Docker based setup](https://www.home-assistant.io/docs/installation/docker/) in July 2019. Ever since starting with my home automation project, I've been making changes weekly and sometimes daily. However, I don't always commit directly to Github (sorry...) so changes may flow in a bit slower.

# My Home Automation Vision
My vision is that my Home Automation should always work, even when the internet is down and always should have a manual backup. The house should still be fully functional for me, the others living with me but also my non-tech grandma. That results into choosing solutions that don't use cloud services if not necesarry and that all lights still can always be switched manually. Therefore I use [Qubino Zwave modules](https://qubino.com/), enabling me to switch lights manually and 'smart', and some [ESPhome](https://esphome.io/) flashed [Sonoff modules](https://sonoff.itead.cc/en), which also come with a push button to switch the relays. A notable exception to this is the [Google Assistant integration](https://www.home-assistant.io/components/google_assistant/), which obviously requires a connection to Google.

# My Home Assistant Infrastructure
## Main Hub
### Hardware
- Raspberry Pi3B+
- [Z-Wave.Me ZME_UZB1 USB Stick](https://tweakers.net/pricewatch/434681/z-wave-punt-me-usb-stick-met-z-wave-plus/specificaties/)
- [CC2531 Zigbee stick](https://tweakers.net/aanbod/1992398/cc2531-zigbee-zigbee2mqtt-usb-stick.html) with [zigbee2mqtt](https://www.zigbee2mqtt.io/)

### Software
- [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) Buster
- [Docker](https://www.docker.com/)
  - [Home Assistant](https://hub.docker.com/r/homeassistant/raspberrypi3-homeassistant) as core
  - [Mosquitto](https://hub.docker.com/_/eclipse-mosquitto) as local MQTT server
  - [Traefik](https://hub.docker.com/_/traefik) as transparant reverse proxy, handling traffic to all containers and SSL termination
  - [ESPhome](https://hub.docker.com/r/esphome/esphome) to program my sonoff devices
  - [zigbee2mqtt](https://hub.docker.com/r/koenkk/zigbee2mqtt) running my zigbee network
  - [Duplicati](https://hub.docker.com/r/duplicati/duplicati) for encrypted backups of my config files to the cloud
  - [nginx](https://hub.docker.com/r/linuxserver/nginx) for some static file hosting.

## Connected devices
### Z-Wave
 - 2x [Qubino Flush Dimmer](https://tweakers.net/pricewatch/467913/qubino-flush-dimmer-z-wave+/specificaties/) 1 for dining room, 1 for window light in living room
 - 1x [NEO COOLCAM NAS-PD02Z Z-wave Plus PIR Motion Sensor](https://www.aliexpress.com/item/32796863408.html) in the living room - links to a V2 but I use the V1 which lacks temperature support
 - 1x [Qubino Flush 2 Relay](https://tweakers.net/pricewatch/474184/qubino-flush-2-relay-z-wave+/specificaties/) in the garden
 - 1x [Qubino Flush Shutter](https://tweakers.net/pricewatch/563345/qubino-flush-shutter-(zmnhcd1)/specificaties/) to control the cover on the attic windows
 
### Wifi Switches
 - 2x [Sonoff basic](https://www.aliexpress.com/item/32831445550.html) switches running ESPhome (so no connection with China!)
 - 2x [Sonoff S20](https://www.aliexpress.com/item/32846334606.html) switches also running ESPhome, 1 in use, 1 in spare for the Christmas lights.
 
### Zigbee sensors
 - 2x [Xiaomi mijia Temperature Humidity Sensor](https://www.aliexpress.com/item/32714410866.html), 1 in the attic, the other in the main bedroom
 - 2x [Xiaomi door Window Sensor](https://www.aliexpress.com/item/32714904459.html) (still on order), 1 is meant for the freezer upstairs because the kids tend to leave it not fully closed. For the other I have no purpose yet.
 
### Thermostat
 - Rooted Toon thermostat
   - Rooting enables local control of the thermostat, and prevents needing a subscription with Eneco. It requires a [custom_component](https://github.com/cyberjunky/home-assistant-toon_climate) (installed through [HACS](https://hacs.xyz/)).
   - Connecting to [emulated Hue on Home Assistant](https://github.com/hmmbob/HomeAssistantConfig/blob/master/includes/emulated_hue.yaml) for light switches.
 - The Toon Thermostat also provides information on my smartmeter, measuring electricity. It receives this information through the P1 port on the meter. This also requires a [custom component](https://github.com/cyberjunky/home-assistant-toon_smartmeter) to work (also easily installed through [HACS](https://hacs.xyz/)).
 
### Cast & Voice Control
- Google Home Hub in the living room
- AndroidTV platform in the living room TV
- LG SH-8 Soundbar with built-in cast in the living room
- Google Home in the study room
- 2x Google Home Mini upstairs
- Google Chromecast in my bedroom TV

# My actual Home Assistant configuration choices
## Presence detection
### Home Assistant Android App
I stepped away from using Owntracks in favor of the official [Home Assistant app](https://play.google.com/store/apps/details?id=io.homeassistant.companion.android) for myself and my wife. This has been working flawlessly so far! It connect directly to my own server, no cloud integration needed.



(readme is work in progress, I'll describe more on my setup later).
