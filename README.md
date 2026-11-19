<div align="center">

# IoT Smarthome

**Painel residencial local-first: sensores, tomadas, lâmpadas e energia numa única interface, rodando na sua rede.**

![Svelte 5](https://img.shields.io/badge/Svelte-5-FF3E00?logo=svelte&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![MQTT](https://img.shields.io/badge/MQTT-Mosquitto-660066?logo=eclipsemosquitto&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32-LVGL-E7352C?logo=espressif&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

</div>

Plataforma residencial **local-first** para acompanhar sensores e controlar dispositivos de diferentes tecnologias numa única interface. O repositório inclui uma PWA Svelte, uma API Python, MQTT/Mosquitto, um simulador para demonstração sem hardware e um firmware de referência para ESP32 com UI em LVGL.

> **Estado atual:** aplicação web, API e simulador demonstráveis no PC. Firmware ESP32/LVGL compilado; execução em placa ainda não validada. Tuya, Zigbee real, câmeras, voz, IA e mídia ainda não implementados. Consulte a [matriz completa de requisitos](docs/requirements.md) antes de avaliar ou instalar.

## Sumário

- [Status por componente](#status-por-componente)
- [Início rápido](#início-rápido)
- [O que já dá para demonstrar](#o-que-já-dá-para-demonstrar)
- [Arquitetura](#arquitetura)
- [Rodar no PC (modo demonstração)](#rodar-no-pc-modo-demonstração)
- [Rodar a stack local com Docker](#rodar-a-stack-local-com-docker)
- [Acessar por nome na rede local](#acessar-por-nome-na-rede-local)
- [Orange Pi e operação física](#orange-pi-e-operação-física)
- [Integrações planejadas e limites](#integrações-planejadas-e-limites)
- [Protocolo MQTT](#protocolo-mqtt)

## Status por componente

| Componente | Tecnologia | Status |
|---|---|---|
| Painel web (PWA) | Svelte 5 + TypeScript + Vite | ✅ Funcional |
| API + simulador | FastAPI + paho-mqtt | ✅ Funcional, com testes |
| Broker | Mosquitto (Docker) | ✅ Funcional (config de laboratório) |
| Proxy HTTPS na LAN | Caddy com CA local | ✅ Funcional |
| Firmware | ESP32 + LVGL + MQTT (PlatformIO) | 🟡 Compila; não validado em placa |
| Zigbee | Zigbee2MQTT | ⏳ Planejado |
| Tuya, câmeras, voz, IA | — | ⏳ Planejado |

## Início rápido

```bash
git clone https://github.com/gusdslara/IoT-smarthome.git
cd IoT-smarthome
docker compose up --build
```

Abra `https://localhost` para o painel e `http://localhost:8000/docs` para a API. Sem Docker, siga [Rodar no PC](#rodar-no-pc-modo-demonstração).

## O que já dá para demonstrar

Consulte também as [evidências de validação executadas](docs/validation.md). O simulador é de dispositivos na API; não é um emulador eletrônico do ESP32.

- Painel web com temperatura, umidade, estado de lâmpadas/tomadas, energia estimada e área de cultivo.
- Simulação contínua de sensores e consumo, com controle de dispositivos virtuais.
- API REST documentada automaticamente em `/docs`.
- MQTT local com tópicos de telemetria e comandos; Mosquitto no Docker Compose.
- PWA instalável em navegadores compatíveis, acessível na LAN por HTTPS local.
- Firmware de referência que publica telemetria MQTT e mostra temperatura/umidade/estado em display LVGL.
- Ambiente Docker para Orange Pi ou computador Linux com Docker.

## Arquitetura

```text
 Zigbee ── coordenador USB ── Zigbee2MQTT ──┐
 Tuya Wi-Fi/cloud ou integração local ──────┤
 ESP32 (MQTT) ───────────────────────────────┤── Mosquitto ── API ── PWA Svelte
 Câmeras ONVIF/RTSP ── adaptador futuro ────┤                 └── regras/automação
 Bluetooth ── proxy ESP32/integração futura ┘
```

O Home Assistant pode ser adicionado como adaptador/integrador para equipamentos suportados. A API deste projeto não substitui os protocolos: ela normaliza dados e oferece uma interface própria. MQTT é o barramento para os dispositivos que o suportam; não é um conversor automático de Zigbee, Tuya ou Bluetooth.

### Estrutura do repositório

```text
apps/api/                 API FastAPI, simulador e integração MQTT
apps/web/                 PWA Svelte + TypeScript + Vite
firmware/esp32-lvgl/      firmware de referência ESP32 + LVGL + MQTT
infra/mosquitto/          configuração do broker MQTT
docs/                     arquitetura, hardware e plano de integração
```

## Rodar no PC (modo demonstração)

Requisitos: Node.js 20+, Python 3.11+ e npm. Para a demonstração sem broker, a API usa o simulador e mantém comandos em memória.

### 1. Iniciar a API

PowerShell:

```powershell
cd apps/api
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Linux/macOS:

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Iniciar a PWA

Em outro terminal:

```bash
cd apps/web
npm install
npm run dev -- --host 0.0.0.0
```

Abra o endereço mostrado pelo Vite (normalmente `http://localhost:5173`). API: `http://localhost:8000`; documentação interativa: `http://localhost:8000/docs`.

## Rodar a stack local com Docker

Requer Docker com Compose. Na raiz do projeto:

```bash
docker compose up --build
```

Abra `https://localhost` (ou `https://casa.home.arpa`) e `http://localhost:8000/docs`. Isso inicia Mosquitto, API, PWA e proxy HTTPS local. A API começa publicando as leituras simuladas em `home/telemetry/<device_id>`.

O Caddy cria uma autoridade certificadora local. Para remover o aviso de certificado nos dispositivos da casa, exporte o certificado raiz do servidor com `docker compose cp caddy:/data/caddy/pki/authorities/local/root.crt ./root.crt` e instale-o como autoridade confiável nos dispositivos que acessarão o painel. Não publique esse certificado nem o use fora da sua rede. A PWA e a API funcionam na rede local sem serviços externos; o primeiro `docker compose up` precisa baixar as imagens e dependências.

Para construir apenas os artefatos web e validar os testes da API:

```bash
cd apps/web && npm install && npm run build
cd ../api && python -m pip install -r requirements-dev.txt && python -m unittest discover -s tests -v
```

## Acessar por nome na rede local

O Compose publica o Caddy nas portas 80 e 443 do host. Para usar um nome em vez do IP, crie uma reserva DHCP para o Orange Pi e cadastre um DNS local no roteador, por exemplo `casa.home.arpa` apontando para o IP reservado. Acesse `https://casa.home.arpa`.

Um nome DNS local no roteador costuma ser mais previsível do que `.local`, cuja resolução varia entre sistemas e redes. Não existe uma URL LAN universal sem configurar DNS ou mDNS.

## Orange Pi e operação física

Em Orange Pi compatível com Docker, use uma imagem 64-bit suportada pela placa, instale Docker/Compose e siga a seção de Compose. Um dongle Zigbee conectado ao Orange Pi pode ser exposto como dispositivo ao Zigbee2MQTT; configure o caminho serial real em `infra/zigbee2mqtt/configuration.yaml` antes de habilitar o serviço opcional.

Para ESP32, veja [`firmware/esp32-lvgl/README.md`](firmware/esp32-lvgl/README.md). Placa, display, pinos, controlador SPI e calibração de energia variam; confira a configuração do display antes de ligar. Sensores de rede elétrica devem usar módulo isolado e instalação apropriada.

## Integrações planejadas e limites

- **Zigbee:** Zigbee2MQTT com coordenador compatível; parear dispositivos reais e verificar o suporte de cada modelo.
- **Tuya:** integração oficial normalmente vinculada à conta/serviço Tuya; integração local tem compatibilidade por modelo. Não suponha que um hub Tuya Bluetooth controla qualquer cadeado BLE.
- **Câmeras:** priorizar ONVIF/RTSP local. Câmera Tuya pode depender de nuvem, firmware e modelo; o vídeo ainda não é exibido neste MVP.
- **Energia:** os valores do simulador são fictícios. Consumo real por circuito/dispositivo exige tomada medidora ou medidor elétrico compatível; total por cômodo é soma dos dispositivos associados.
- **Cultivo:** painel e telemetria são demonstrativos. Avaliar altura, cor, estágio, saúde ou pragas requer câmera, iluminação/escala calibradas e pipeline de visão ainda não implementado.
- **Queda, grito e cuidado:** não implementado. Não use este MVP como sistema de emergência ou monitoramento médico. Detecção confiável exige desenho, ensaios e validação próprios.
- **WhatsApp, usuários e permissões:** não implementados. Alertas locais podem ser adicionados primeiro; entrega pelo WhatsApp depende de API/conta e conectividade externa.
- **Voz, música, YouTube/Spotify, downloads e espelhamento:** não implementados. Integrações dependem de APIs, dispositivos e termos dos serviços; nenhuma ferramenta de download está incluída.
- **IA agnóstica:** arquitetura prevê um serviço de visão/assistente desacoplado para provedor local (por exemplo, Ollama) ou remoto. Não há chamadas a modelos nem envio de imagens neste MVP.

## Protocolo MQTT

- Telemetria: `home/telemetry/<device_id>` (JSON)
- Comandos: `home/command/<device_id>` (JSON)
- Estado normalizado: `home/state/<device_id>` (JSON)

Exemplo de telemetria:

```json
{"device_id":"esp32-quarto","temperature_c":25.1,"humidity_pct":58.0,"ts":"2026-01-01T12:00:00Z"}
```

Exemplo de comando:

```json
{"action":"set_power","value":true}
```

Em instalação real, não exponha o broker sem autenticação, use credenciais únicas e ACLs, segmente IoT em VLAN quando possível e proteja o acesso remoto por VPN. Este Compose é para laboratório/LAN confiável e usa configuração simples de desenvolvimento.

## Licença

MIT. Consulte [`LICENSE`](LICENSE).
