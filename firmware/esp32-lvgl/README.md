# ESP32 + LVGL

Firmware de referência para ESP32 DevKit, display SPI ST7789 320x240 e LVGL 9. Ele desenha uma tela de temperatura/umidade e publica JSON no tópico `home/telemetry/esp32-quarto`.

## Build e gravação

1. Instale PlatformIO (VS Code ou `python -m pip install platformio`).
2. Ajuste os pinos/controlador do display em `platformio.ini` para a sua placa.
3. Copie `include/secrets.h.example` para `include/secrets.h` e informe Wi-Fi/MQTT. Nunca faça commit de credenciais.
4. Coloque um sensor analógico adequado no GPIO34 ou troque `publishReading()` por leitura real I²C (por exemplo, SHT31/BME280). O mapeamento analógico atual é apenas um sinal de demonstração, não mede temperatura ou umidade real.
5. Compile com `pio run`; grave com `pio run -t upload`; monitor serial com `pio device monitor`.

**Validação:** compilado com PlatformIO para `esp32dev`/Arduino e LVGL 9.6.0 usando a partição `huge_app` (o layout padrão reserva pouco espaço para LVGL). Não foi gravado nem verificado numa placa física nesta entrega. O LVGL/TFT dependem do controlador e da fiação da placa concreta. Trate o resultado como referência de firmware, não como firmware certificado.
