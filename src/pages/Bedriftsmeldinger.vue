<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <div class="bm-page">

    <!-- PAGE HERO -->
    <div class="page-hero">
      <div class="container">
        <div class="hero-inner">
          <div class="hero-eyebrow">
            <span class="hero-dot"></span>
            <span class="hero-label">Offisielle kunngjøringer</span>
          </div>
          <h1 class="hero-title">Bedrifts<em>meldinger</em></h1>
          <p class="hero-sub">Nyheter, oppdateringer og kaos fra HMN. § 7.7 garanterer ingenting.</p>
        </div>
      </div>
    </div>

    <div class="container bm-body">

      <!-- LOADING -->
      <template v-if="loading">
        <div class="filters-row">
          <div v-for="i in 5" :key="i" class="skel-chip"></div>
        </div>
        <div class="bm-grid">
          <div v-for="i in 6" :key="i" class="bm-card skel-card">
            <div class="skel-tag"></div>
            <div class="skel-title"></div>
            <div class="skel-line mb6"></div>
            <div class="skel-line" style="width:70%"></div>
          </div>
        </div>
      </template>

      <!-- CONTENT -->
      <template v-else>

        <!-- FILTER TABS -->
        <div class="filters-row">
          <button
            v-for="f in filters"
            :key="f.value"
            class="filter-chip"
            :class="{ active: activeFilter === f.value }"
            @click="activeFilter = f.value"
          >{{ f.label }}</button>
        </div>

        <!-- PINNED FEATURED (if pinned exists and filter is 'alle') -->
        <router-link
          v-if="pinnedMelding && activeFilter === 'alle'"
          :to="`/bedriftsmeldinger/${pinnedMelding.id}`"
          class="featured-card"
        >
          <div class="fc-top">
            <span class="post-live-dot"></span>
            <span class="fc-eyebrow">Festet melding</span>
            <span class="post-tag" :class="tagClass(pinnedMelding.category)">{{ categoryLabel(pinnedMelding.category) }}</span>
            <span class="fc-ref">{{ pinnedMelding.ref }}</span>
            <span class="fc-date">{{ formatDate(pinnedMelding.created_at) }}</span>
          </div>
          <div class="fc-title">{{ pinnedMelding.title }}</div>
          <div class="fc-preview">{{ stripHtml(pinnedMelding.content) }}</div>
          <div class="fc-cta">Les melding →</div>
        </router-link>

        <!-- GRID -->
        <div v-if="filteredMeldinger.length" class="bm-grid">
          <router-link
            v-for="m in filteredMeldinger"
            :key="m.id"
            :to="`/bedriftsmeldinger/${m.id}`"
            class="bm-card"
          >
            <div class="bmc-top">
              <span class="post-tag" :class="tagClass(m.category)">{{ categoryLabel(m.category) }}</span>
              <span v-if="m.pinned" class="pin-icon">📌</span>
            </div>
            <div class="bmc-title">{{ m.title }}</div>
            <div class="bmc-preview">{{ stripHtml(m.content) }}</div>
            <div class="bmc-meta">{{ m.ref }} · {{ formatDate(m.created_at) }}</div>
          </router-link>
        </div>

        <!-- EMPTY -->
        <div v-else class="bm-empty">
          <div class="bm-empty-icon">📭</div>
          <div class="bm-empty-title">Ingen meldinger her</div>
          <div class="bm-empty-sub">Prøv et annet filter.</div>
        </div>

      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '@/axios';

const loading = ref(true);
const meldinger = ref([]);
const activeFilter = ref('alle');

const filters = [
  { value: 'alle',            label: 'Alle' },
  { value: 'oppdatering',     label: 'Oppdatering' },
  { value: 'kaos',            label: 'Kaos' },
  { value: 'hendelse',        label: 'Hendelse' },
  { value: 'viktig',          label: 'Viktig' },
  { value: 'thomas-relatert', label: 'Thomas' },
];

const CATEGORY_LABELS = {
  oppdatering: 'Oppdatering',
  kaos: 'Kaos',
  hendelse: 'Hendelse',
  viktig: 'Viktig',
  'thomas-relatert': 'Thomas-relatert',
};

function categoryLabel(cat) {
  return CATEGORY_LABELS[cat] || cat || 'Melding';
}

function tagClass(cat) {
  const map = {
    oppdatering: 'pt-oppdatering',
    kaos: 'pt-kaos',
    hendelse: 'pt-hendelse',
    viktig: 'pt-viktig',
    'thomas-relatert': 'pt-thomas',
  };
  return map[cat] || 'pt-oppdatering';
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('nb-NO', { day: 'numeric', month: 'long', year: 'numeric' });
}

function stripHtml(html) {
  if (!html) return '';
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || '';
}

const pinnedMelding = computed(() => meldinger.value.find(m => m.pinned) || null);

const filteredMeldinger = computed(() => {
  let list = meldinger.value;
  if (activeFilter.value !== 'alle') {
    list = list.filter(m => m.category === activeFilter.value || m.tag === activeFilter.value);
  }
  // In 'alle' view, don't show the pinned one in the grid (it's in the featured card)
  if (activeFilter.value === 'alle' && pinnedMelding.value) {
    list = list.filter(m => m.id !== pinnedMelding.value.id);
  }
  return list;
});

async function fetchMeldinger() {
  try {
    const { data } = await api.get('/bedriftsmeldinger');
    meldinger.value = Array.isArray(data) ? data : [];
  } catch (e) {
    console.error('Failed to load bedriftsmeldinger:', e);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchMeldinger);
</script>

<style scoped>
.bm-page {
  min-height: 100vh;
}

/* ── Page hero ── */
.page-hero {
  padding: 48px 0 40px;
  position: relative;
  border-bottom: 1px solid var(--border);
}
.page-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 70% 120% at 50% 0%, rgba(0,184,208,0.05), transparent 70%);
  pointer-events: none;
}
.hero-inner { position: relative; }
.hero-eyebrow {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 14px;
}
.hero-dot {
  width: 6px; height: 6px; background: var(--cyan);
  border-radius: 50%; box-shadow: 0 0 8px var(--cyan);
  animation: blink 2.5s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
.hero-label {
  font-size: 11px; color: var(--cyan);
  font-family: var(--font-display); letter-spacing: 0.1em; text-transform: uppercase;
}
.hero-title {
  font-family: var(--font-display); font-size: clamp(2.4rem, 5vw, 3.6rem);
  font-weight: 900; color: var(--text-bright); text-transform: uppercase;
  line-height: 0.95; letter-spacing: -0.01em; margin-bottom: 12px;
}
.hero-title em { color: var(--cyan); font-style: normal; }
.hero-sub { font-size: 14px; color: var(--text-muted); font-family: var(--font-body); }

/* ── Body ── */
.bm-body { padding: 32px 0 64px; }

.container {
  width: min(calc(100% - 2.5rem), 1120px);
  margin: 0 auto;
}

/* ── Filters ── */
.filters-row {
  display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 24px;
}
.filter-chip {
  font-size: 12px; font-family: var(--font-display); font-weight: 700;
  letter-spacing: 0.06em; text-transform: uppercase;
  padding: 5px 14px; border-radius: 20px;
  border: 1px solid var(--border2);
  background: rgba(255,255,255,0.03);
  color: var(--text-muted); cursor: pointer; transition: all 0.15s;
}
.filter-chip:hover { background: rgba(255,255,255,0.07); color: var(--text); }
.filter-chip.active { background: rgba(0,184,208,0.1); border-color: rgba(0,184,208,0.3); color: var(--cyan); }

/* ── Category tags ── */
.post-tag {
  display: inline-block; font-size: 10px; padding: 3px 10px;
  border-radius: 4px; font-weight: 700; letter-spacing: 0.08em;
  font-family: var(--font-display); text-transform: uppercase;
}
.pt-oppdatering { background: rgba(40,184,96,0.1);  color: var(--green); border: 1px solid rgba(40,184,96,0.2); }
.pt-kaos        { background: rgba(200,16,46,0.12); color: var(--red2);  border: 1px solid rgba(200,16,46,0.22); }
.pt-hendelse    { background: rgba(0,184,208,0.1);  color: var(--cyan);  border: 1px solid rgba(0,184,208,0.2); }
.pt-viktig      { background: rgba(216,152,32,0.1); color: var(--gold);  border: 1px solid rgba(216,152,32,0.2); }
.pt-thomas      { background: rgba(112,80,216,0.1); color: #9070f0;      border: 1px solid rgba(112,80,216,0.22); }

/* ── Featured pinned card ── */
.featured-card {
  display: block; text-decoration: none;
  background: rgba(255,255,255,0.028); border: 1px solid var(--border2);
  border-radius: var(--r-lg); padding: 24px 28px; margin-bottom: 24px;
  border-left: 3px solid var(--cyan);
  transition: all 0.2s; position: relative; overflow: hidden;
}
.featured-card::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse 80% 100% at 0% 50%, rgba(0,184,208,0.04), transparent 60%);
  pointer-events: none;
}
.featured-card:hover { border-color: var(--cyan); transform: translateY(-2px); box-shadow: 0 16px 40px rgba(0,0,0,0.3); }
.fc-top {
  display: flex; align-items: center; gap: 10px; margin-bottom: 12px; flex-wrap: wrap;
}
.post-live-dot {
  width: 6px; height: 6px; background: var(--green); border-radius: 50%;
  box-shadow: 0 0 6px var(--green); flex-shrink: 0; animation: blink 2.5s infinite;
}
.fc-eyebrow {
  font-size: 10px; color: var(--cyan);
  font-family: var(--font-display); letter-spacing: 0.1em; text-transform: uppercase; font-weight: 700;
}
.fc-ref  { font-size: 11px; color: var(--text-muted); font-family: var(--font-display); letter-spacing: 0.07em; }
.fc-date { font-size: 11px; color: var(--text-muted); margin-left: auto; }
.fc-title {
  font-family: var(--font-display); font-size: clamp(1.6rem, 3vw, 2.4rem);
  font-weight: 900; color: var(--text-bright); text-transform: uppercase;
  line-height: 1; margin-bottom: 10px;
}
.fc-preview {
  font-size: 13px; color: rgba(255,255,255,0.35); font-family: var(--font-body);
  line-height: 1.7; margin-bottom: 16px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.fc-cta { font-size: 12px; color: var(--cyan); font-family: var(--font-display); font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }

/* ── Cards grid ── */
.bm-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.bm-card {
  background: rgba(255,255,255,0.025); border: 1px solid var(--border);
  border-radius: 10px; padding: 18px; cursor: pointer;
  transition: all 0.2s; text-decoration: none; display: block;
}
.bm-card:hover { border-color: var(--border2); transform: translateY(-2px); box-shadow: 0 12px 32px rgba(0,0,0,0.3); }
.bmc-top { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.pin-icon { font-size: 11px; margin-left: auto; }
.bmc-title { font-size: 15px; font-weight: 600; color: var(--text-bright); font-family: var(--font-body); margin-bottom: 8px; line-height: 1.4; }
.bmc-preview {
  font-size: 12px; color: rgba(255,255,255,0.3); font-family: var(--font-body);
  line-height: 1.55; margin-bottom: 12px;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}
.bmc-meta { font-size: 10px; color: var(--text-muted); font-family: var(--font-display); letter-spacing: 0.06em; }

/* ── Empty state ── */
.bm-empty { text-align: center; padding: 80px 0; }
.bm-empty-icon  { font-size: 40px; margin-bottom: 14px; }
.bm-empty-title { font-family: var(--font-display); font-size: 18px; font-weight: 800; color: var(--text-bright); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }
.bm-empty-sub   { font-size: 13px; color: var(--text-muted); }

/* ── Skeletons ── */
.skel-chip  { height: 30px; width: 90px; background: rgba(255,255,255,0.05); border-radius: 20px; }
.skel-card  { min-height: 140px; }
.skel-tag   { height: 18px; width: 70px; background: rgba(255,255,255,0.06); border-radius: 4px; margin-bottom: 10px; }
.skel-title { height: 20px; width: 80%; background: rgba(255,255,255,0.06); border-radius: 4px; margin-bottom: 10px; }
.skel-line  { height: 12px; width: 100%; background: rgba(255,255,255,0.04); border-radius: 4px; }
.mb6 { margin-bottom: 6px; }

@media (max-width: 900px) {
  .bm-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 600px) {
  .bm-grid { grid-template-columns: 1fr; }
}
</style>
