This repo contains my Home Assistant configuration. Home Assistant is open source home automation that puts local control and privacy first. More information can be found at their website, https://www.home-assistant.io.

I started with Home Assistant in 2018, running it in a [Python venv](https://www.home-assistant.io/installation) directly on Raspbian. I ran into all kinds of compatibility issues over time, so I switched to a [Docker based setup](https://www.home-assistant.io/installation) in July 2019. Ever since starting my home automation project, I've been making changes weekly and sometimes daily. However, I do not always commit directly to GitHub (sorry...), so changes may flow in a bit slower. In April 2020 I completely rebuilt my Lovelace setup, and summer 2024 brought a complete new UI setup.

[![Home Assistant dashboard tour video](https://img.youtube.com/vi/Gfjz0f2YXJs/0.jpg)](https://www.youtube.com/watch?v=Gfjz0f2YXJs)

# My Home Automation Vision

My vision is that my Home Automation should always work, even when the internet is down, and should always have a manual backup. The house should still be fully functional for me, the others living with me, and my non-tech grandma. That results in choosing solutions that do not use cloud services if not necessary and that all lights can always be switched manually.

# Current Setup

- Runtime: Home Assistant in Docker
- Host: Linux
- UI: custom Lovelace dashboards
- Key areas: Woonkamer, Salon, Eetkamer, Keuken, Kantoor, Master bedroom, Slaapkamer T/M, Tuin

# Structure

- `automations.yaml`, `scripts.yaml`: core automations and scripts
- `packages/`: feature-focused Home Assistant packages
- `dashboards/`: Lovelace YAML dashboards
- `custom_components/`: HACS and local custom integrations
- `blueprints/`: automation and script blueprints
- Dashboards are split into multiple YAML files (0-main, living room, energy, etc.)

# Core Integrations and Devices

- Climate: Tado integration, multi-room airco units, warm water
- Power/EV: Zonneplan, EV Smart Charging
- Weather: KNMI, NL Weather
- Zigbee: Zigbee2MQTT devices and light groups
- Sensors: room temp/humidity, plant sensors, door/window/motion
- Media: TVs, soundbar, speakers, kiosk tablets
- Extras: Awtrix display, Rocky vacuum, Xiaomi air purifier

# Notes

- This repo is a living system; not every change is immediately pushed.
