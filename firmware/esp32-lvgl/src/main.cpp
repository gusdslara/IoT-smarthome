#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <TFT_eSPI.h>
#include <lvgl.h>

// Copy secrets.h.example to secrets.h and set your Wi-Fi/MQTT values.
#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.h.example"
#endif

static constexpr int SENSOR_PIN = 34; // Example analog input; replace with your calibrated sensor.
static constexpr uint32_t SAMPLE_MS = 3000;
TFT_eSPI tft;
WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
lv_obj_t *temperatureLabel;
lv_obj_t *humidityLabel;
lv_obj_t *networkLabel;
uint32_t lastSample = 0;
uint32_t lastReconnect = 0;
float temperatureC = 24.0f;
float humidityPct = 55.0f;

static void flushDisplay(lv_display_t *display, const lv_area_t *area, uint8_t *pixels) {
  const uint32_t width = area->x2 - area->x1 + 1;
  const uint32_t height = area->y2 - area->y1 + 1;
  tft.startWrite();
  tft.setAddrWindow(area->x1, area->y1, width, height);
  tft.pushColors(reinterpret_cast<uint16_t *>(pixels), width * height, true);
  tft.endWrite();
  lv_display_flush_ready(display);
}

static void connectMqtt() {
  if (WiFi.status() != WL_CONNECTED || millis() - lastReconnect < 5000) return;
  lastReconnect = millis();
  mqtt.connect("esp32-bedroom", MQTT_USER, MQTT_PASSWORD);
  if (networkLabel) lv_label_set_text(networkLabel, mqtt.connected() ? "Wi-Fi + MQTT conectados" : "MQTT offline");
}

static void publishReading() {
  // Replace the demo values with real I2C sensor readings and calibration.
  const int raw = analogRead(SENSOR_PIN);
  temperatureC = 23.0f + (raw % 30) / 10.0f;
  humidityPct = 48.0f + (raw % 300) / 10.0f;
  char payload[160];
  snprintf(payload, sizeof(payload), "{\"device_id\":\"esp32-quarto\",\"temperature_c\":%.1f,\"humidity_pct\":%.1f,\"ts_ms\":%lu}", temperatureC, humidityPct, millis());
  mqtt.publish("home/telemetry/esp32-quarto", payload, true);
  char text[48];
  snprintf(text, sizeof(text), "%.1f °C", temperatureC);
  lv_label_set_text(temperatureLabel, text);
  snprintf(text, sizeof(text), "%.1f %%", humidityPct);
  lv_label_set_text(humidityLabel, text);
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  tft.begin();
  tft.setRotation(1);
  lv_init();
  lv_tick_set_cb([]() -> uint32_t { return millis(); });
  static uint8_t drawBuffer[240 * 20 * 2];
  lv_display_t *display = lv_display_create(320, 240);
  lv_display_set_flush_cb(display, flushDisplay);
  lv_display_set_buffers(display, drawBuffer, nullptr, sizeof(drawBuffer), LV_DISPLAY_RENDER_MODE_PARTIAL);

  lv_obj_t *screen = lv_screen_active();
  lv_obj_set_style_bg_color(screen, lv_color_hex(0x101610), 0);
  lv_obj_t *title = lv_label_create(screen);
  lv_label_set_text(title, "CASA / VIVA");
  lv_obj_set_style_text_color(title, lv_color_hex(0xB8F05D), 0);
  lv_obj_align(title, LV_ALIGN_TOP_LEFT, 14, 12);
  temperatureLabel = lv_label_create(screen);
  lv_obj_set_style_text_color(temperatureLabel, lv_color_white(), 0);
  lv_obj_set_style_text_font(temperatureLabel, &lv_font_montserrat_14, 0);
  lv_obj_align(temperatureLabel, LV_ALIGN_CENTER, 0, -22);
  humidityLabel = lv_label_create(screen);
  lv_obj_set_style_text_color(humidityLabel, lv_color_hex(0x87C9D7), 0);
  lv_obj_align(humidityLabel, LV_ALIGN_CENTER, 0, 10);
  networkLabel = lv_label_create(screen);
  lv_obj_set_style_text_color(networkLabel, lv_color_hex(0x98A391), 0);
  lv_obj_align(networkLabel, LV_ALIGN_BOTTOM_LEFT, 14, -12);
  lv_label_set_text(networkLabel, "Conectando...");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  WiFi.setAutoReconnect(true);
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setSocketTimeout(1);
  connectMqtt();
  publishReading();
}

void loop() {
  lv_timer_handler();
  if (WiFi.status() == WL_CONNECTED && !mqtt.connected()) connectMqtt();
  mqtt.loop();
  if (millis() - lastSample >= SAMPLE_MS) {
    lastSample = millis();
    publishReading();
  }
  delay(5);
}
