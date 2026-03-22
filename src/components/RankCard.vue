<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <div class="rank-card" :class="[normalizedVariant, { 'has-color': colorRgb }]" :style="colorVars">
    <div class="rank-glow"></div>
    <div class="rank-card-inner">
      <div class="rank-icon-wrap">{{ meta.icon }}</div>
      <div class="rank-info">
        <div class="rank-label">{{ label }}</div>
        <div class="rank-name">{{ name }}</div>
        <div class="rank-desc" v-if="effectiveDesc">{{ effectiveDesc }}</div>
        <div class="rank-since" v-if="since">Tildelt {{ since }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const RANK_META = {
  admin:     { icon: '🛡️', desc: 'Ansvarlig for alt som går galt. Og bra. Men mest galt.' },
  overlege:  { icon: '🩺', desc: 'Tittel er selvpålagt og juridisk bindende. § 3.1.' },
  developer: { icon: '💻', desc: 'Vet hva en npm install er. Bruker det til å true andre.' },
  producer:  { icon: '🎵', desc: 'Lager bangere på bekostning av andre. § 2.1 godkjent.' },
  junior:    { icon: '🌱', desc: 'Ny pasient. Det er ikke din feil. Uansett hva det er.' },
  member:    { icon: '🪪', desc: 'Offisielt registrert pasient. Velkommen til kaoset.' },
  testrolle: { icon: '🧪', desc: 'Eksisterer for å teste ting. Hva slags ting? Ukjent.' },
}

const props = defineProps({
  variant:  { type: String, default: 'member' },
  name:     { type: String, required: true },
  desc:     { type: String, default: '' },
  since:    { type: String, default: '' },
  label:    { type: String, default: 'Din rang' },
  color:    { type: String, default: '' }, // ADDED THIS - badge_color from DB
})

function hexToRgb(hex) {
  if (!hex) return null
  const h = hex.replace('#', '')
  if (h.length !== 6) return null
  const r = parseInt(h.substring(0, 2), 16)
  const g = parseInt(h.substring(2, 4), 16)
  const b = parseInt(h.substring(4, 6), 16)
  return `${r}, ${g}, ${b}`
}

const normalizedVariant = computed(() => props.variant.toLowerCase())
const meta              = computed(() => RANK_META[normalizedVariant.value] ?? { icon: '👤', desc: '' })
const effectiveDesc     = computed(() => props.desc || meta.value.desc)
const colorRgb          = computed(() => hexToRgb(props.color)) // ADDED THIS
const colorVars         = computed(() => colorRgb.value ? { '--rc': colorRgb.value } : {}) // ADDED THIS
</script>

<style scoped>
.rank-card {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--border2);
  position: relative;
}
.rank-glow        { position: absolute; inset: 0; opacity: 0.5; pointer-events: none; }
.rank-card-inner  { padding: 18px 16px 16px; display: flex; align-items: center; gap: 14px; position: relative; z-index: 1; }
.rank-icon-wrap   { width: 48px; height: 48px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 22px; flex-shrink: 0; }
.rank-info        { flex: 1; min-width: 0; }
.rank-label       { font-size: 9px; letter-spacing: 0.14em; font-weight: 700; font-family: var(--font-display); text-transform: uppercase; margin-bottom: 3px; opacity: 0.6; }
.rank-name        { font-family: var(--font-display); font-size: 20px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.04em; line-height: 1; margin-bottom: 5px; }
.rank-desc        { font-size: 11px; font-family: var(--font-body); line-height: 1.55; opacity: 0.5; font-style: italic; color: var(--text); }
.rank-since       { font-size: 10px; font-family: var(--font-display); letter-spacing: 0.06em; opacity: 0.4; margin-top: 6px; text-transform: uppercase; }

/* ── ADMIN ── */
.rank-card.admin      { background: linear-gradient(145deg,#1a0a0e,#120610); border-color: rgba(200,16,46,0.3); }
.rank-card.admin      .rank-glow      { background: radial-gradient(ellipse 100% 100% at 0% 0%,rgba(200,16,46,0.12),transparent 70%); }
.rank-card.admin      .rank-icon-wrap { background: rgba(200,16,46,0.15); border: 1px solid rgba(200,16,46,0.3); }
.rank-card.admin      .rank-label     { color: var(--red2); }
.rank-card.admin      .rank-name      { color: #ff6070; }
.rank-card.admin      .rank-since     { color: var(--red2); }

/* ── OVERLEGE ── */
.rank-card.overlege   { background: linear-gradient(145deg,#1a0f04,#120b00); border-color: rgba(216,152,32,0.3); }
.rank-card.overlege   .rank-glow      { background: radial-gradient(ellipse 100% 100% at 0% 0%,rgba(216,152,32,0.1),transparent 70%); }
.rank-card.overlege   .rank-icon-wrap { background: rgba(216,152,32,0.15); border: 1px solid rgba(216,152,32,0.3); }
.rank-card.overlege   .rank-label     { color: var(--gold); }
.rank-card.overlege   .rank-name      { color: #f0b840; }
.rank-card.overlege   .rank-since     { color: var(--gold); }

/* ── DEVELOPER ── */
.rank-card.developer  { background: linear-gradient(145deg,#0a0e1a,#060c18); border-color: rgba(0,184,208,0.25); }
.rank-card.developer  .rank-glow      { background: radial-gradient(ellipse 100% 100% at 0% 0%,rgba(0,184,208,0.1),transparent 70%); }
.rank-card.developer  .rank-icon-wrap { background: rgba(0,184,208,0.12); border: 1px solid rgba(0,184,208,0.25); }
.rank-card.developer  .rank-label     { color: var(--cyan); }
.rank-card.developer  .rank-name      { color: var(--cyan2); }
.rank-card.developer  .rank-since     { color: var(--cyan); }

/* ── PRODUCER ── */
.rank-card.producer   { background: linear-gradient(145deg,#0a120a,#060e06); border-color: rgba(40,184,96,0.25); }
.rank-card.producer   .rank-glow      { background: radial-gradient(ellipse 100% 100% at 0% 0%,rgba(40,184,96,0.1),transparent 70%); }
.rank-card.producer   .rank-icon-wrap { background: rgba(40,184,96,0.12); border: 1px solid rgba(40,184,96,0.25); }
.rank-card.producer   .rank-label     { color: var(--green); }
.rank-card.producer   .rank-name      { color: #50e890; }
.rank-card.producer   .rank-since     { color: var(--green); }

/* ── JUNIOR ── */
.rank-card.junior     { background: linear-gradient(145deg,#121008,#0e0c06); border-color: rgba(216,152,32,0.25); }
.rank-card.junior     .rank-glow      { background: radial-gradient(ellipse 100% 100% at 0% 0%,rgba(216,152,32,0.1),transparent 70%); }
.rank-card.junior     .rank-icon-wrap { background: rgba(216,152,32,0.12); border: 1px solid rgba(216,152,32,0.25); }
.rank-card.junior     .rank-label     { color: var(--gold); }
.rank-card.junior     .rank-name      { color: #f0b840; }
.rank-card.junior     .rank-since     { color: var(--gold); }

/* ── MEMBER ── */
.rank-card.member     { background: linear-gradient(145deg,#0c1018,#080c14); border-color: rgba(255,255,255,0.09); }
.rank-card.member     .rank-glow      { background: radial-gradient(ellipse 100% 100% at 0% 0%,rgba(255,255,255,0.04),transparent 70%); }
.rank-card.member     .rank-icon-wrap { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); }
.rank-card.member     .rank-label     { color: rgba(255,255,255,0.4); }
.rank-card.member     .rank-name      { color: rgba(255,255,255,0.7); }
.rank-card.member     .rank-since     { color: rgba(255,255,255,0.3); }

/* ── TESTROLLE ── */
.rank-card.testrolle  { background: linear-gradient(145deg,#0e0a14,#0a0610); border-color: rgba(112,80,216,0.25); border-style: dashed; }
.rank-card.testrolle  .rank-glow      { background: radial-gradient(ellipse 100% 100% at 0% 0%,rgba(112,80,216,0.1),transparent 70%); }
.rank-card.testrolle  .rank-icon-wrap { background: rgba(112,80,216,0.12); border: 1px solid rgba(112,80,216,0.25); }
.rank-card.testrolle  .rank-label     { color: #9070f0; }
.rank-card.testrolle  .rank-name      { color: #a880ff; }
.rank-card.testrolle  .rank-since     { color: var(--purple); }

/* ── DYNAMIC COLOR (from DB badge_color) ── overrides role-specific styles ── */
.rank-card.has-color                { background: linear-gradient(145deg, rgba(var(--rc),0.08), rgba(var(--rc),0.03)); border-color: rgba(var(--rc),0.25); }
.rank-card.has-color .rank-glow     { background: radial-gradient(ellipse 100% 100% at 0% 0%, rgba(var(--rc),0.1), transparent 70%); }
.rank-card.has-color .rank-icon-wrap { background: rgba(var(--rc),0.12); border: 1px solid rgba(var(--rc),0.25); }
.rank-card.has-color .rank-label     { color: rgba(var(--rc),0.7); }
.rank-card.has-color .rank-name      { color: rgb(var(--rc)); }
.rank-card.has-color .rank-since     { color: rgba(var(--rc),0.7); }
</style>
