<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <div class="ranks-page">
    <!-- Page Hero -->
    <div class="page-hero">
      <div class="hmn-container page-hero-inner">
        <div class="page-eyebrow">
          <span class="page-eyebrow-dot"></span>
          <span class="page-eyebrow-text">REF: HMN-RANK-001 · Rangdefinisjon</span>
        </div>
        <h1 class="page-title">Rang<em>system</em></h1>
        <p class="page-desc">Oversikt over alle offisielle HMN-ranger. Tildeles av administrasjonen. § 3.1 rettigheter gjelder alltid.</p>
      </div>
    </div>

    <div class="ranks-body">
      <div class="hmn-container">
        <div class="sh mb-sm">
          <span class="sh-title">Alle <em>ranger</em></span>
          <div class="sh-line"></div>
          <span class="sh-tag">{{ sortedRoles.length }} definert</span>
        </div>

        <div v-if="loading" class="ranks-loading">Laster ranger…</div>

        <div v-else-if="!sortedRoles.length" class="ranks-loading">Ingen ranger funnet.</div>

        <div v-else class="ranks-list">
          <div v-for="role in sortedRoles" :key="role.id" class="rank-item">
            <p class="rank-section-label">{{ role.name }}</p>
            <RankCard
              :variant="normalizeVariant(role.name)"
              :name="role.name"
              label="Rang"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from '@/axios'
import RankCard from '@/components/RankCard.vue'

const RANK_PRIORITY = ['admin', 'overlege', 'developer', 'producer', 'junior', 'testrolle', 'member']

const roles   = ref([])
const loading = ref(true)

const sortedRoles = computed(() =>
  [...roles.value].sort((a, b) => {
    const ai = RANK_PRIORITY.indexOf(a.name.toLowerCase())
    const bi = RANK_PRIORITY.indexOf(b.name.toLowerCase())
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi)
  })
)

function normalizeVariant(name) {
  const n = name.toLowerCase()
  return RANK_PRIORITY.includes(n) ? n : 'member'
}

onMounted(async () => {
  try {
    const res = await axios.get('/roles')
    roles.value = res.data.roles
  } catch (e) {
    console.error('Failed to load roles:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.ranks-page { background: var(--bg); min-height: 100vh; color: var(--text); }

/* ── Hero ── */
.page-hero {
  background: linear-gradient(180deg,#06090f,var(--bg));
  border-bottom: 1px solid var(--border);
  padding: 40px 0 36px;
  position: relative;
  overflow: hidden;
}
.page-hero::before {
  content: '';
  position: absolute; inset: 0;
  background-image: linear-gradient(rgba(0,184,208,0.02) 1px,transparent 1px), linear-gradient(90deg,rgba(0,184,208,0.02) 1px,transparent 1px);
  background-size: 52px 52px;
  mask-image: linear-gradient(180deg,rgba(0,0,0,0.5),transparent);
}
.page-hero-inner { position: relative; z-index: 1; }
.page-eyebrow { display: inline-flex; align-items: center; gap: 8px; background: rgba(0,184,208,0.07); border: 1px solid rgba(0,184,208,0.16); padding: 5px 14px; border-radius: 4px; margin-bottom: 12px; }
.page-eyebrow-dot { width: 6px; height: 6px; background: var(--green); border-radius: 50%; box-shadow: 0 0 8px var(--green); animation: blink 2.5s infinite; }
.page-eyebrow-text { color: var(--cyan); font-size: 10px; letter-spacing: 0.1em; font-family: var(--font-display); font-weight: 600; text-transform: uppercase; }
.page-title { font-family: var(--font-display); font-size: clamp(2.4rem,4vw,4.2rem); font-weight: 900; color: var(--bright); text-transform: uppercase; line-height: 0.92; margin-bottom: 10px; }
.page-title em { background: linear-gradient(92deg,var(--cyan),var(--cyan2)); -webkit-background-clip: text; background-clip: text; color: transparent; font-style: normal; }
.page-desc { font-size: 14px; color: rgba(255,255,255,0.35); line-height: 1.8; max-width: 460px; }

/* ── Body ── */
.ranks-body { padding: 44px 0 72px; }
.ranks-loading { color: var(--muted); font-family: var(--font-body); font-size: 14px; text-align: center; padding: 40px; font-style: italic; }
.ranks-list { display: flex; flex-direction: column; gap: 20px; max-width: 400px; }
.rank-section-label { font-size: 10px; color: var(--muted); letter-spacing: 0.12em; text-transform: uppercase; font-family: var(--font-display); font-weight: 700; margin-bottom: 6px; }
</style>
