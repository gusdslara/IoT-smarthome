# Registro de validação — 12/11/2026

Ambiente: Windows, Node.js/Vite, Python 3.14, PlatformIO 6.2.0. Este registro descreve somente verificações executadas, não certifica hardware.

| Verificação | Resultado |
|---|---|
| `python -m unittest discover -s tests -v` em `apps/api` | 11 testes passaram, incluindo contratos HTTP com TestClient |
| `npm run build` em `apps/web` | Build de produção gerado com sucesso |
| `python -m platformio run` em `firmware/esp32-lvgl` | SUCCESS; ESP32 DevKit, Arduino 3.3.12, LVGL 9.6.0 |
| Firmware RAM | 123.368 / 327.680 bytes (37,6%) |
| Firmware flash | 1.680.792 / 3.145.728 bytes (53,4%, partição huge_app) |
| Docker Compose | Configuração validada na entrega inicial; stack completa ainda não ensaiada |

## Regressões cobertas

- Comando de desligar lâmpada simulada zera watts imediatamente.
- Sensores rejeitam comandos de alimentação; ações desconhecidas são rejeitadas pelo contrato HTTP.
- Dispositivo desconhecido retorna 404.
- Dispositivo físico não recebe confirmação inventada quando o broker está indisponível (503).
- JSON MQTT inválido e medidas fora de faixa são rejeitados.
- O simulador preserva leituras de dispositivos físicos, inclusive sensores com capacidades parciais.
- Consultas retornam cópias do registro; alterações no retorno não alteram os dispositivos.
- A soma de watts por cômodo corresponde ao total.

## Correções de firmware

Relógio LVGL ligado a `millis()`. Removidas esperas infinitas de conexão na inicialização e no retry MQTT. Tentativas passam a ocorrer em intervalos; a operação TCP ainda é síncrona e não tem garantia de tempo real. Configuração sem credenciais reais permanece compilável usando placeholders.

Persistem avisos de compilação sobre touchscreen não configurado e o identificador de guarda de configuração LVGL. O firmware não implementa touchscreen. A entrada analógica continua sendo uma demonstração: não é um sensor calibrado de temperatura/umidade.

## O que estas evidências não validam

Não houve gravação em ESP32, simulação eletrônica da placa, execução em Orange Pi, teste de instalação da PWA em celular, integração com broker real ou teste de equipamentos Tuya/Zigbee/Bluetooth/câmeras. TestClient executa a API em memória; não ensaia DNS, HTTPS, rede ou proxy reverso. A suíte também não cobre os módulos ainda não implementados listados em [requirements.md](requirements.md).

Para reproduzir os testes da API, instale `apps/api/requirements-dev.txt`. O workflow GitHub Actions executa testes/build web/build firmware, mas só terá uma execução verificável após publicar o repositório.
