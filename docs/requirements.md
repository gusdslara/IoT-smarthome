# Matriz de requisitos e critérios de aceite

Esta matriz compara o pedido completo ao código existente. Compilação não comprova operação física. "Planejado" significa que não existe implementação funcional desse recurso.

| Requisito | Situação | Evidência necessária para aceite completo |
|---|---|---|
| PWA Svelte responsiva | Implementado; build validado | Ensaio visual desktop/mobile e instalação HTTPS em cliente LAN |
| Orange Pi como servidor | Compose preparado | Subir stack em Orange Pi ARM64 e validar reinício/volumes |
| URL local | Caddy/DNS documentados | DNS do roteador, certificado confiável e acesso em dois clientes |
| ESP32 com LVGL | Compilável; não testado em placa | Display ST7789 correto, Wi-Fi, MQTT e leitura física |
| Temperatura/umidade por MQTT | Ingestão e testes automatizados | Broker e ESP32 reais publicando durante perda/reconexão |
| Cadastro manual e cômodos | Planejado | CRUD persistente e configuração de capacidades |
| Sensores Zigbee | Planejado | Coordenador identificado, Zigbee2MQTT e mapeamento de mensagens |
| Tuya Wi-Fi/Zigbee/BLE | Planejado | Modelos, conta/hub e integração compatível; validação por aparelho |
| Bluetooth/cadeado | Planejado | Protocolo suportado, autenticação e confirmação física |
| Lâmpadas/tomadas | Controle simulado e publicação de comando MQTT | Driver físico, confirmação de estado, offline e timeout |
| Energia por dispositivo/cômodo/total | Watts simulados agregados pela API | Medidores reais, integração kWh no tempo, tarifas e calibração |
| Câmera ESP32/Tuya/videoporteiro | Planejado | Stream autenticado, vídeo no navegador e comandos suportados |
| Cultivo/altura/cor/estágio/pragas | Telemetria simulada; visão planejada | Imagens com escala/iluminação e conjunto de avaliação por tarefa |
| Queda/ferimento/grito/pedido de ajuda | Planejado | Pipeline audiovisual, confirmação humana e avaliação de falsos positivos/negativos |
| Usuários/permissões/notificações PWA | Planejado | Autenticação, autorização, entrega e revogação de acesso |
| WhatsApp configurável | Planejado | API oficial configurada, destinatário autorizado e teste de entrega |
| HD/SSD/retenção de gravações | Planejado | Volumes configuráveis, quota, retenção e recuperação após reinício |
| Buscar chave em gravações com IA | Planejado | Indexação local, orçamento de inferência e progresso/resultados verificáveis |
| OpenAI/Gemini/Claude/Ollama | Planejado | Adaptadores, credenciais, limites, falhas e testes de contrato |
| Comandos/respostas por voz | Planejado | STT/TTS, microfone/alto-falante e seleção de destino |
| Alexa/dispositivos de áudio Tuya | Planejado | API/skill e capacidades reais de cada equipamento |
| Música/vídeo local/Spotify/YouTube | Planejado | Player, provedores, autenticação e dispositivos de reprodução |
| Download de mídia | Planejado | Fontes autorizadas e implementação de transferência |
| TV/Miracast/espelhamento | Planejado | Host e receptor compatíveis com protocolo específico |
| GitHub/CI/documentação | Preparados | Executar Actions após publicar; não há remoto configurado |

## Limites operacionais atuais

O registro e o histórico ficam em memória e são perdidos ao reiniciar. Não há login nem autorização. O broker de laboratório aceita conexões anônimas. Os indicadores de cultivo e consumo são dados simulados. A interface mostra snapshots recebidos; não há trilha de auditoria persistente. Não há streaming, gravação, envio de imagens a IA ou disparo de emergência no código atual.

## Ordem de implementação

1. Persistência, cadastro de dispositivos, cômodos, autenticação e ACL MQTT.
2. Adaptadores MQTT/Zigbee2MQTT e Tuya com confirmação de estado e dispositivos reais.
3. Câmeras ONVIF/RTSP, armazenamento e política de retenção.
4. Provedores de IA e busca indexada com limites de orçamento.
5. Alertas, usuários, WhatsApp e confirmação de pedido de ajuda.
6. Voz, players e integrações de telas/alto-falantes.

Não existe garantia de funcionamento pleno dos recursos classificados como planejados. Aprovar a plataforma exige testes de integração e de hardware além dos testes automatizados deste repositório.
