<script lang="ts">
  import { onMount } from 'svelte';

  type Device = { id: string; name: string; room: string; kind: string; protocol: string; online: boolean; on?: boolean; power_w?: number; temperature_c?: number; humidity_pct?: number; soil_pct?: number };
  type Summary = { device_count: number; online_count: number; power_w: number; sensors: Device[] };

  let devices: Device[] = $state([]);
  let summary: Summary | null = $state(null);
  let apiOnline = $state(false);
  let lastUpdate = $state('');
  let busy = $state('');
  let commandError = $state('');

  async function refresh() {
    try {
      const [d, s] = await Promise.all([fetch('/api/devices'), fetch('/api/summary')]);
      if (!d.ok || !s.ok) throw new Error('API indisponível');
      devices = await d.json(); summary = await s.json(); apiOnline = true;
      lastUpdate = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch { apiOnline = false; }
  }

  async function toggle(device: Device) {
    busy = device.id;
    commandError = '';
    try {
      const response = await fetch(`/api/devices/${device.id}/command`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'set_power', value: !device.on }) });
      if (!response.ok) throw new Error((await response.json()).detail || 'Falha no comando');
      await refresh();
    } catch (error) {
      commandError = error instanceof Error ? error.message : 'Falha de conexão';
    } finally { busy = ''; }
  }

  onMount(() => { refresh(); const timer = setInterval(refresh, 2500); return () => clearInterval(timer); });

  const clock = new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit' });
</script>

<svelte:head><meta name="apple-mobile-web-app-capable" content="yes" /></svelte:head>

<div class="shell">
  <aside class="sidebar">
    <a class="brand" href="/" aria-label="IoT Smarthome início"><span class="brand-mark">⌂</span><span>casa<span class="brand-light">/viva</span></span></a>
    <div class="nav-label">ESPAÇO</div>
    <button class="nav-item selected"><span>◫</span> Visão geral</button>
    <button class="nav-item" onclick={() => document.getElementById('devices')?.scrollIntoView()}><span>⌁</span> Dispositivos <small>{devices.length}</small></button>
    <button class="nav-item" onclick={() => document.getElementById('grow')?.scrollIntoView()}><span>♧</span> Cultivo <i class="soon">DEMO</i></button>
    <button class="nav-item" disabled><span>◉</span> Câmeras <i class="soon">BREVE</i></button>
    <button class="nav-item" disabled><span>⌁</span> Automações <i class="soon">BREVE</i></button>
    <div class="sidebar-bottom"><div class="avatar">G</div><div><strong>Casa local</strong><span>Administrador</span></div><span class="more">···</span></div>
  </aside>

  <main class="main">
    <header class="topbar"><div class="crumb">Minha casa <span>/</span> Visão geral</div><div class="top-actions"><span class:online={apiOnline} class="connection"><i></i>{apiOnline ? 'Tudo conectado' : 'Reconectando'}</span><button class="icon-button" aria-label="Notificações">♧<b></b></button><div class="avatar small">G</div></div></header>
    <section class="content">
      {#if commandError}<p role="alert">{commandError}</p>{/if}
      <p class="muted">Ambiente de demonstração. Câmeras, IA, voz e alertas externos ainda não implementados.</p>
      <div class="hero"><div><div class="eyebrow"><span class="sun">☼</span> {clock.format(new Date())} <span class="dot-sep">·</span> {new Intl.DateTimeFormat('pt-BR', { weekday: 'long', day: 'numeric', month: 'long' }).format(new Date())}</div><h1>Bom dia, Gustavo <span>✳</span></h1><p>Sua casa está tranquila. Aqui está o resumo de agora.</p></div><button class="add-button" onclick={refresh}>＋ <span>Atualizar painel</span></button></div>

      <div class="stats-grid">
        <article class="stat-card"><div class="stat-top"><span>ENERGIA AGORA</span><span class="stat-icon yellow">ϟ</span></div><div class="stat-value">{summary?.power_w ?? '—'} <small>W</small></div><div class="stat-foot"><span class="neutral-pill">SIMULADO</span><span>consumo instantâneo</span></div><div class="mini-bars">{#each [35,48,39,61,43,74,52,84,58,68,43,75,48,61,90,55,72,47,63,78,45,66,53,83] as height, i}<i style={`height:${height}%`} class:accent={i > 19}></i>{/each}</div></article>
        <article class="stat-card"><div class="stat-top"><span>DISPOSITIVOS ONLINE</span><span class="stat-icon green">⌁</span></div><div class="stat-value">{summary?.online_count ?? '—'}<small> / {summary?.device_count ?? '—'}</small></div><div class="stat-foot"><span class="live-dot"></span><span>Sincronizados localmente</span></div><div class="status-line"><div style={`width:${summary?.device_count ? (summary.online_count/summary.device_count)*100 : 0}%`}></div></div></article>
        <article class="stat-card environment"><div class="stat-top"><span>AMBIENTE · QUARTO</span><span class="stat-icon blue">⌖</span></div><div class="environment-row"><div><div class="stat-value">{devices.find(d => d.id === 'quarto-sensor')?.temperature_c ?? '—'}<small>°C</small></div><span class="muted">Temperatura</span></div><div class="env-divider"></div><div><div class="stat-value">{devices.find(d => d.id === 'quarto-sensor')?.humidity_pct ?? '—'}<small>%</small></div><span class="muted">Umidade</span></div></div><div class="stat-foot"><span class="live-dot"></span><span>Sensor atualiza a cada 3s</span></div></article>
      </div>

      <div class="section-heading"><div><h2>Seus dispositivos <span class="count">{devices.length}</span></h2><p>Controle rápido dos ambientes da sua casa</p></div><button class="text-button">Ver todos <span>→</span></button></div>
      <div class="devices-grid" id="devices">
        {#each devices.filter(d => d.kind !== 'sensor') as device}
          <article class="device-card"><div class="device-card-top"><div class="device-icon" class:light-icon={device.kind === 'light'} class:plug-icon={device.kind === 'plug'}>{device.kind === 'light' ? '☼' : 'ϟ'}</div><button class="switch" class:on={device.on} disabled={busy === device.id} onclick={() => toggle(device)} aria-label={`Alternar ${device.name}`}><i></i></button></div><div class="device-title">{device.name}</div><div class="device-room">{device.room} <span>·</span> {device.protocol}</div><div class="device-bottom"><span><i class="live-dot"></i> {device.on ? 'Ligado' : 'Desligado'}</span><b>{device.power_w} W</b></div></article>
        {/each}
        <button class="add-device" onclick={refresh}><span>↻</span><strong>Atualizar dispositivos</strong><small>Consultar estado na API</small></button>
      </div>

      <div class="lower-grid"><article class="panel grow-panel"><div class="panel-heading"><div><h2>Seu cultivo <span class="tiny-tag">SIMULADOR</span></h2><p>Monitoramento ambiental da horta</p></div><span class="plant">♧</span></div><div class="grow-content"><div class="plant-art"><span>♧</span><i></i></div><div class="grow-stats"><div><span>Temperatura</span><b>{devices.find(d => d.id === 'grow-sensor')?.temperature_c ?? '—'}°C</b></div><div><span>Umidade do ar</span><b>{devices.find(d => d.id === 'grow-sensor')?.humidity_pct ?? '—'}%</b></div><div><span>Umidade do solo</span><b>{devices.find(d => d.id === 'grow-sensor')?.soil_pct ?? '—'}%</b></div></div></div><div class="demo-note">Dados simulados · análise de imagem ainda não conectada</div></article>
        <article class="panel activity-panel" id="grow"><div class="panel-heading"><div><h2>Estado recebido</h2><p>Última consulta à API</p></div></div><div class="activity-list">{#each devices as device}<div class="activity"><span class="activity-icon cool">⌖</span><div><b>{device.name}</b><small>{device.room} · {device.protocol} · {device.online ? 'Online' : 'Offline'}</small></div><time>{lastUpdate || '—'}</time></div>{/each}</div></article></div>
      <footer>IoT Smarthome <span>·</span> painel local na sua rede <span class="footer-right">Última atualização: {lastUpdate || '—'}</span></footer>
    </section>
  </main>
</div>
