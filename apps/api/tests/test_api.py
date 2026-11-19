import unittest

from fastapi import HTTPException

from app.main import command, health, ingest_mqtt, list_devices, summary, DeviceCommand


class ApiTests(unittest.TestCase):
    def test_health_and_devices(self):
        self.assertEqual(health()["status"], "ok")
        self.assertGreaterEqual(len(list_devices()), 4)
        self.assertGreater(summary()["power_w"], 0)

    def test_device_command(self):
        response = command("sala-lamp", DeviceCommand(action="set_power", value=False))
        self.assertFalse(response["on"])

    def test_unknown_device(self):
        with self.assertRaises(HTTPException) as error:
            command("inexistente", DeviceCommand(action="set_power", value=True))
        self.assertEqual(error.exception.status_code, 404)

    def test_mqtt_telemetry_creates_sensor(self):
        ingest_mqtt("home/telemetry/test-esp32", b'{"temperature_c":22.5,"humidity_pct":51}')
        device = next(item for item in list_devices() if item["id"] == "test-esp32")
        self.assertEqual(device["temperature_c"], 22.5)
        self.assertEqual(device["protocol"], "mqtt")


if __name__ == "__main__":
    unittest.main()

