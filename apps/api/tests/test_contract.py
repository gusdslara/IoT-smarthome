"""HTTP contracts and regressions; no broker, external account or hardware required."""
import asyncio
import copy
import os
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import main


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.saved = copy.deepcopy(main.DEVICES)
        self.environment = patch.dict(os.environ, {"SIMULATOR_ENABLED": "false", "MQTT_HOST": ""})
        self.environment.start()
        self.client = TestClient(main.app)

    def tearDown(self):
        self.client.close()
        self.environment.stop()
        main.DEVICES.clear()
        main.DEVICES.update(self.saved)

    def test_switch_command_and_energy(self):
        response = self.client.post('/api/devices/sala-lamp/command', json={"action": "set_power", "value": False})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['power_w'], 0)
        summary = self.client.get('/api/summary').json()
        self.assertAlmostEqual(summary['power_w'], sum(summary['power_by_room_w'].values()), places=1)

    def test_sensor_rejects_power_command(self):
        response = self.client.post('/api/devices/quarto-sensor/command', json={"action": "set_power", "value": True})
        self.assertEqual(response.status_code, 422)

    def test_unknown_action_and_device(self):
        self.assertEqual(self.client.post('/api/devices/sala-lamp/command', json={"action": "unlock", "value": True}).status_code, 422)
        self.assertEqual(self.client.post('/api/devices/missing/command', json={"action": "set_power", "value": True}).status_code, 404)

    def test_physical_command_does_not_invent_confirmation(self):
        main.DEVICES['physical'] = {"id": "physical", "kind": "plug", "protocol": "mqtt", "on": False}
        with patch.object(main, 'MQTT_CLIENT', None):
            response = self.client.post('/api/devices/physical/command', json={"action": "set_power", "value": True})
        self.assertEqual(response.status_code, 503)
        self.assertFalse(main.DEVICES['physical']['on'])

    def test_malformed_and_out_of_range_telemetry(self):
        main.ingest_mqtt('home/telemetry/real', b'{"temperature_c": 23, "humidity_pct": 120, "power_w": -3}')
        device = main.DEVICES['real']
        self.assertEqual(device['temperature_c'], 23)
        self.assertNotIn('humidity_pct', device)
        self.assertNotIn('power_w', device)
        main.ingest_mqtt('home/telemetry/bad', b'{broken')
        self.assertNotIn('bad', main.DEVICES)

    def test_simulator_preserves_physical_sensor(self):
        main.ingest_mqtt('home/telemetry/real', b'{"temperature_c": 23}')
        before = copy.deepcopy(main.DEVICES['real'])
        async def step():
            task = asyncio.create_task(main.simulate())
            await asyncio.sleep(0.01)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        asyncio.run(step())
        self.assertEqual(main.DEVICES['real'], before)

    def test_read_models_are_snapshots(self):
        devices = main.list_devices()
        devices[0]['name'] = 'modified'
        self.assertNotEqual(main.list_devices()[0]['name'], 'modified')
