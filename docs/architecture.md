# Architecture and integration plan

## Boundaries

The web app speaks HTTP to the API. The API owns normalized device records, command validation, and MQTT publish/subscribe adapters. Drivers translate vendor/protocol payloads into normalized entities; they should not be embedded in the Svelte UI.

Suggested normalized entity fields: `id`, `name`, `room`, `kind`, `protocol`, `online`, `updated_at`, and capability-specific values. Commands should be capability checked (for example, only a switch/light accepts `set_power`). Persist state and history in SQLite first; use PostgreSQL/Timescale only if retention or query load requires it.

## Planned adapters

1. MQTT/ESPHome: topic parser and command publisher; this repository has the demo publish path.
2. Zigbee: run Zigbee2MQTT as a separate service with its own coordinator and map its MQTT discovery/state into normalized devices.
3. Tuya: select official cloud integration or a model-supported local driver. Keep credentials outside source control.
4. Cameras: ONVIF discovery/RTSP stream proxy, with per-camera authorization and retention controls.
5. Bluetooth: ESPHome proxy or a supported vendor integration. Proxy presence alone does not imply control API compatibility.
6. Energy: capture meter readings and cumulative kWh, then aggregate by room and period. Instantaneous watts in the demo are not billed-energy data.
7. Cultivation: sensor calibration, scheduled camera capture, image store, and optional vision provider interface.

## LAN naming and remote access

For a stable local URL, reserve the server IP and create a router DNS record (for example `casa.home.arpa`). mDNS `.local` can be a convenience but is not uniform across all networks. Remote access should use a VPN; this starter does not expose a public service.

## Safety boundaries

This system is a hobby/portfolio project, not a certified alarm, medical device, access-control safety system, or emergency dispatch service. Do not use an experimental fall/scream classifier to decide whether an older adult or child is safe. Camera and microphone processing must be consent-based, visible to household members, and protected by access controls. Do not store smart-lock credentials in the browser.
