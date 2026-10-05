# My Home Assistant configuration

This repository contains the YAML configuration behind my home: automations, scripts, helpers, dashboards, and shared templates for [Home Assistant](https://www.home-assistant.io/).

I started using Home Assistant in 2018, running it in a Python virtual environment on Raspbian. In July 2019 I moved to Docker, which remains the basis of the setup. The dashboards have evolved too, with major redesigns in 2020 and 2024 and ongoing changes since then.

## My home automation vision

The house should be easy to use for everyone who lives here and anyone visiting, including my non-technical grandma. Everyday controls should feel natural, and lights should always be usable with a physical switch.

I prefer local control wherever practical and want essential functions to keep working when the internet is down. Cloud services still have a place for things such as energy prices, weather forecasts, and connected services, but manual control and sensible fallback behavior remain priorities.

## Current setup

Home Assistant runs in Docker on Linux. Most YAML logic is organized into packages by floor, room, or household function. The interface uses custom YAML Lovelace dashboards, with Dutch labels throughout much of the configuration.

The setup covers lighting, heating and air conditioning, ventilation, energy management, EV charging, security, media, and everyday household reminders. Zigbee devices are connected through Zigbee2MQTT, alongside other local and cloud integrations.

## What the configuration does

A few examples worth exploring:

| Area | Examples | Configuration |
| --- | --- | --- |
| Lighting | Motion lighting, room groups, wake-up lights, and vacation lighting | [Room packages](packages/), [vacation mode](packages/9%20-%20General/vacation_mode.yaml) |
| Energy | Zonneplan electricity prices, GoodWe solar control based on negative prices and schedules, and dishwasher start-time advice based on its consumption profile | [Solar](packages/6%20-%20Outside/solar.yaml), [dishwasher](packages/0%20-%20Ground%20floor/Kitchen/notification_dishwasher_cheapest_time.yaml) |
| EV charging | EV Smart Charging with SmartEVSE, charging progress notifications, and monthly energy summaries | [EV package](packages/6%20-%20Outside/ev.yaml) |
| Climate | Air-conditioning sleep timers, setpoint limits, and switching off heating and cooling when everyone is away | [Climate package](packages/9%20-%20General/airco.yaml) |
| Ventilation | Scheduled ventilation with manual, humidity, and toilet boosts | [Ventilation package](packages/9%20-%20General/ventilation.yaml), [shared humidity logic](custom_templates/ventilation.jinja) |
| Household | Waste collection reminders, parcel-box tracking, Picnic delivery information, and vacuum reminders | [Waste](packages/6%20-%20Outside/trash.yaml), [parcels](packages/6%20-%20Outside/pakketbrievenbus.yaml), [Picnic](packages/9%20-%20General/picnic.yaml), [vacuums](packages/9%20-%20General/vacuum.yaml) |
| Notifications and media | Morning briefings, actionable phone notifications, spoken announcements, Sonos controls, and an AWTRIX display | [Morning briefing](packages/3%20-%20Mr/morning_briefing.yaml), [announcements](packages/9%20-%20General/tts_system.yaml), [AWTRIX](packages/1%20-%20First%20floor/Office/awtrix_ulanzi_tc001.yaml) |

## Dashboards

Four YAML dashboards are registered in [configuration.yaml](configuration.yaml):

- **Home** — room views and dedicated pages for energy, the car, plants, cameras, and the alarm. Entry point: [dashboards/ui-lovelace.yaml](dashboards/ui-lovelace.yaml).
- **Admin** — battery monitoring, system status, solar settings, air-conditioning controls, and development tools. This dashboard requires an administrator account. Entry point: [dashboards/admin/admin.yaml](dashboards/admin/admin.yaml).
- **Map** — household location overview. Entry point: [dashboards/map/map.yaml](dashboards/map/map.yaml).
- **TSV / kiosk** — tablet views, a calendar, and temporary delivery or order reminders. Entry point: [dashboards/tsv/tsv.yaml](dashboards/tsv/tsv.yaml).

Views are split into separate files, with reusable cards in `dashboards/common/` and `dashboards/tsv/common/`. The dashboards use custom frontend components such as Mushroom, UIX, Browser Mod, and Kiosk Mode.

I recently migrated my two kiosks from Fully Kiosk Browser to [Kiosk Satellite](https://github.com/jxlarrea/kiosk-satellite). Its ESPHome integration exposes screen and volume controls, buttons, and other features as Home Assistant entities. Camera handling, announcements, and URL overlays have moved over too, removing much of the old kiosk-specific logic and screensaver workarounds. Both kiosks are running well, and the configuration is considerably simpler.

[Watch the dashboard tour on YouTube](https://www.youtube.com/watch?v=Gfjz0f2YXJs). The configuration keeps evolving, so the video may differ from the current dashboards.

## Repository structure

| Path | Purpose |
| --- | --- |
| `configuration.yaml` | Main configuration, package loading, dashboard registration, and shared settings |
| `packages/` | Automations, scripts, helpers, and related configuration grouped by area or function |
| `dashboards/` | YAML dashboards, individual views, and reusable cards |
| `custom_templates/` | Shared Jinja macros for energy calculations, ventilation, dashboard helpers, and time formatting |
| `includes/` | Additional configuration included from the main file |
| `themes/` | Custom frontend theme |
| `automations.yaml`, `scripts.yaml` | Empty placeholders for the Home Assistant UI editors; the actual YAML automations and scripts live in `packages/` |

The running installation also has custom integrations and blueprints. These are not tracked in this repository.

## Using this repository

This is my personal configuration, shared as a source of ideas and examples. It is not a complete installation or a ready-to-use configuration for another home. Integrations and some helpers are configured through the Home Assistant UI, and their stored configuration is not included here. Custom integrations, frontend components, and referenced local assets may need to be installed or supplied separately.

When adapting an example, check its entity IDs, helper dependencies, templates, and service calls against your own installation. Values referenced through `!secret` need your own entries in `secrets.yaml`; credentials and private runtime data are excluded from this repository.

If you edit an included dashboard file, also update the modification time of its main dashboard YAML file, then refresh the browser page so Home Assistant picks up the change.

This is a living setup. I make changes regularly, and the running installation can be ahead of what has been pushed to GitHub.
