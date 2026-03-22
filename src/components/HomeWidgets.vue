<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <div class="g2 reveal mb48">
    <div class="events-card">
      <div class="ec-head">
        <span class="ec-title">Kommende hendelser</span>
        <span class="ec-meta">
          {{ loading.hendelser ? '…' : displayHendelser.length + ' aktive' }}
        </span>
      </div>
      <template v-if="loading.hendelser">
        <div v-for="i in 3" :key="i" class="ev">
          <div>
            <div class="skel skel-sm mb6"></div>
            <div class="skel skel-xs"></div>
          </div>
          <div class="skel skel-badge"></div>
        </div>
      </template>
      <template v-else-if="!displayHendelser.length">
        <div class="ev-empty">
          <div class="ev-empty-title">Ingen kommende hendelser</div>
          <div class="ev-empty-sub">Neste oppføring dukker opp her så snart admin publiserer en ekte hendelse.</div>
        </div>
      </template>
      <template v-else>
        <router-link
          v-for="ev in displayHendelser"
          :key="ev.id || ev.title"
          :to="ev.to"
          class="ev ev-link"
        >
          <div>
            <div class="ev-name">{{ ev.title }}</div>
            <div class="ev-date">{{ ev.dateLabel }}</div>
          </div>
          <span :class="['evb', ev.badge.cls]">{{ ev.badge.label }}</span>
        </router-link>
      </template>
    </div>

    <div class="health-widget">
      <div class="hw-head">
        <span class="hw-title">Helsejournal 🏥</span>
        <span class="hw-status"><span class="hw-status-dot"></span>Stabil-ish</span>
      </div>
      <div class="hw-metric">
        <div class="hw-metric-label">Eksistensielt stressnivå</div>
        <div>
          <div class="hw-metric-val c-red">Forhøyet</div>
          <div class="hw-metric-sub">etter torsdagsmøtet</div>
        </div>
      </div>
      <div class="hw-metric">
        <div class="hw-metric-label">Kaffeinntak i dag</div>
        <div>
          <div class="hw-metric-val c-gold">3 kopper</div>
          <div class="hw-metric-sub">§ 5.2 anbefalt maks</div>
        </div>
      </div>
      <div class="hw-metric">
        <div class="hw-metric-label">Sist sett utenfor</div>
        <div>
          <div class="hw-metric-val c-cyan">2 dager</div>
          <div class="hw-metric-sub">sol ikke detektert</div>
        </div>
      </div>
      <div class="hw-metric">
        <div class="hw-metric-label">Diagnose</div>
        <div>
          <div class="hw-metric-val c-green">Stabil</div>
          <div class="hw-metric-sub">for nå</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  loading: { type: Object, required: true },
  displayHendelser: { type: Array, required: true },
})
</script>

<style scoped>
.events-card {
  background: rgba(255,255,255,0.018);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  overflow: hidden;
}
.ec-head {
  padding: 11px 16px;
  border-bottom: 1px solid var(--border);
  background: rgba(255,255,255,0.02);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.ec-title {
  font-family: var(--font-display);
  font-size: 13px; font-weight: 800;
  color: var(--bright);
  letter-spacing: 0.08em; text-transform: uppercase;
}
.ec-meta { font-size: 11px; color: var(--text-muted); font-family: var(--font-ui); }
.ev {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 13px 16px;
  border-bottom: 1px solid var(--border);
  transition: background 0.15s;
  gap: 12px;
}
.ev-link {
  color: inherit;
  text-decoration: none;
}
.ev:hover { background: rgba(255,255,255,0.025); }
.ev:last-child { border-bottom: none; }
.ev-name { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 3px; font-family: var(--font-body); }
.ev-date { font-size: 11px; color: var(--text-muted); font-family: var(--font-ui); }
.ev-empty {
  padding: 22px 16px;
  text-align: left;
}
.ev-empty-title {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 800;
  color: var(--bright);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.ev-empty-sub {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.6;
  font-family: var(--font-body);
}
.evb {
  font-size: 9px; padding: 4px 10px;
  border-radius: var(--r-xs);
  font-weight: 700; letter-spacing: 0.07em;
  white-space: nowrap;
  font-family: var(--font-display);
  text-transform: uppercase;
  flex-shrink: 0;
}
.evb-gold { background: rgba(216,152,32,0.12); color: var(--gold); border: 1px solid rgba(216,152,32,0.22); }
.evb-red  { background: rgba(200,16,46,0.12);  color: var(--red2); border: 1px solid rgba(200,16,46,0.22); }
.evb-cyan { background: rgba(0,184,208,0.08);  color: var(--cyan); border: 1px solid rgba(0,184,208,0.18); }

.health-widget {
  background: rgba(255,255,255,0.018);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  overflow: hidden;
}
.hw-head {
  padding: 11px 16px;
  border-bottom: 1px solid var(--border);
  background: rgba(255,255,255,0.02);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.hw-title { font-family: var(--font-display); font-size: 13px; font-weight: 800; color: var(--bright); letter-spacing: 0.08em; text-transform: uppercase; }
.hw-status { display: flex; align-items: center; gap: 6px; font-size: 10px; color: var(--green); font-weight: 600; font-family: var(--font-ui); }
.hw-status-dot { width: 5px; height: 5px; background: var(--green); border-radius: 50%; }
.hw-metric {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.hw-metric:last-child { border-bottom: none; }
.hw-metric-label { font-size: 12px; color: var(--text-muted); font-family: var(--font-ui); }
.hw-metric-val   { font-family: var(--font-display); font-size: 18px; font-weight: 800; text-align: right; }
.hw-metric-sub   { font-size: 10px; color: var(--text-muted); margin-top: 1px; text-align: right; font-family: var(--font-ui); }
</style>
