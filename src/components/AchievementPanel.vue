<template>
  <div class="ach-panel">

    <!-- Header -->
    <div class="ach-header">
      <span class="ach-title">Alle achievements</span>
      <span class="ach-count">{{ unlockedCount }} låst opp · {{ lockedCount }} ikke låst</span>
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div v-for="s in rarityStats" :key="s.rarity" class="stat-card">
        <div class="stat-val" :style="{ color: s.color }">{{ s.count }}</div>
        <div class="stat-label">{{ s.rarity }}</div>
      </div>
    </div>

    <!-- Filters + Search -->
    <div class="filter-row">
      <div class="filter-chips">
        <button
          v-for="f in filters"
          :key="f.id"
          class="fc"
          :class="{ active: activeFilter === f.id }"
          @click="activeFilter = f.id"
        >{{ f.label }}</button>
      </div>
      <input v-model="search" class="search-inp" placeholder="Søk achievements..." />
    </div>

    <!-- Unlocked section -->
    <template v-if="activeFilter !== 'locked' && filteredUnlocked.length">
      <div class="sec">
        <span class="sec-title">Låst <em>opp</em></span>
        <div class="sec-line" />
        <span class="sec-count">{{ filteredUnlocked.length }} achievements</span>
      </div>
      <div class="ach-grid">
        <Achievement v-for="a in filteredUnlocked" :key="a.id" v-bind="a" />
      </div>
    </template>

    <!-- Locked section -->
    <template v-if="filteredLocked.length">
      <div class="sec">
        <span class="sec-title">Ikke <em>låst opp</em></span>
        <div class="sec-line" />
        <span class="sec-count">{{ filteredLocked.length }} achievements</span>
      </div>
      <div class="ach-grid">
        <Achievement v-for="a in filteredLocked" :key="a.id" v-bind="a" />
      </div>
    </template>

    <div v-if="!filteredUnlocked.length && !filteredLocked.length" class="empty">
      Ingen achievements funnet.
    </div>

  </div>
</template>

<script>
import axios from '@/axios'
import Achievement from './Achievement.vue'

const RARITIES = ['legendary', 'epic', 'rare', 'common']
const RARITY_COLORS = { legendary: 'var(--gold)', epic: '#9070f0', rare: 'var(--cyan)', common: 'rgba(255,255,255,0.4)' }

function mapAch(a) {
  return {
    id:          a.id,
    title:       a.title,
    description: a.description,
    svg:         a.svg || a.icon,
    achieved:    a.achieved || false,
    rarity:      a.rarity || 'common',
    glow_color:  a.glow_color,
    unlocked_at: a.unlocked_at,
    progress:    a.progress ?? null,
    progressMax: a.progress_max ?? null,
    category:    a.category || 'site'
  }
}

export default {
  components: { Achievement },
  data() {
    return {
      achievements:        [],
      clickerAchievements: [],
      activeFilter: 'alle',
      search: '',
      filters: [
        { id: 'alle',      label: 'Alle' },
        { id: 'legendary', label: 'Legendary' },
        { id: 'epic',      label: 'Epic' },
        { id: 'rare',      label: 'Rare' },
        { id: 'common',    label: 'Common' },
        { id: 'locked',    label: 'Ikke låst' }
      ]
    }
  },
  computed: {
    merged() {
      return [...this.achievements, ...this.clickerAchievements]
    },
    unlockedCount() { return this.merged.filter(a => a.achieved).length },
    lockedCount()   { return this.merged.filter(a => !a.achieved).length },
    rarityStats() {
      return RARITIES.map(r => ({
        rarity: r.charAt(0).toUpperCase() + r.slice(1),
        color:  RARITY_COLORS[r],
        count:  this.merged.filter(a => a.achieved && (a.rarity || 'common').toLowerCase() === r).length
      }))
    },
    filteredUnlocked() { return this.merged.filter(a =>  a.achieved && this.matches(a)) },
    filteredLocked()   { return this.merged.filter(a => !a.achieved && this.matches(a)) }
  },
  methods: {
    matches(a) {
      const q = this.search.toLowerCase()
      if (q && !(a.title || '').toLowerCase().includes(q) && !(a.description || '').toLowerCase().includes(q)) return false
      if (this.activeFilter === 'alle' || this.activeFilter === 'locked') return true
      return (a.rarity || 'common').toLowerCase() === this.activeFilter
    },
    async fetchAchievements() {
      try {
        const [{ data: site }, { data: clicker }] = await Promise.all([
          axios.get('/user/achievements'),
          axios.get('/clicker-achievements')
        ])
        this.achievements        = site.map(mapAch)
        this.clickerAchievements = clicker.filter(a => (a.category || '').toLowerCase() === 'clicker').map(mapAch)
      } catch (e) {
        console.error('Could not fetch achievements:', e)
      }
    }
  },
  mounted() { this.fetchAchievements() }
}
</script>

<style scoped>
.ach-panel { width: 100%; }

/* Header */
.ach-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.ach-title {
  font-family: 'Barlow Condensed', sans-serif; font-size: 13px; font-weight: 800;
  color: var(--text-bright); letter-spacing: 0.1em; text-transform: uppercase;
}
.ach-count { font-size: 11px; color: var(--text-muted); }

/* Stats */
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 20px; }
.stat-card {
  background: rgba(255,255,255,0.025); border: 1px solid var(--border);
  border-radius: 8px; padding: 12px 14px; text-align: center;
}
.stat-val {
  font-family: 'Barlow Condensed', sans-serif; font-size: 22px;
  font-weight: 900; line-height: 1; margin-bottom: 3px;
}
.stat-label {
  font-size: 10px; color: var(--text-muted); letter-spacing: 0.07em;
  text-transform: uppercase; font-family: 'Barlow Condensed', sans-serif;
}

/* Filters */
.filter-row {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; margin-bottom: 24px; flex-wrap: wrap;
}
.filter-chips { display: flex; gap: 6px; flex-wrap: wrap; }
.fc {
  padding: 5px 13px; border-radius: 5px; font-size: 11px; font-weight: 600;
  font-family: 'Barlow Condensed', sans-serif; letter-spacing: 0.06em; text-transform: uppercase;
  cursor: pointer; border: 1px solid var(--border); background: rgba(255,255,255,0.03);
  color: var(--text-muted); transition: all 0.15s;
}
.fc:hover { color: var(--text); border-color: var(--border2); }
.fc.active { background: rgba(0,184,208,0.08); border-color: rgba(0,184,208,0.2); color: var(--cyan); }

.search-inp {
  background: var(--surface2); border: 1px solid var(--border2); border-radius: 7px;
  padding: 7px 12px; font-size: 12px; color: var(--text-bright); outline: none; width: 200px;
}
.search-inp:focus { border-color: var(--cyan); }
.search-inp::placeholder { color: var(--text-muted); }

/* Section divider */
.sec { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; margin-top: 8px; }
.sec-title {
  font-family: 'Barlow Condensed', sans-serif; font-size: 13px; font-weight: 800;
  color: var(--text-bright); letter-spacing: 0.08em; text-transform: uppercase; white-space: nowrap;
}
.sec-title em { color: var(--cyan); font-style: normal; }
.sec-line { flex: 1; height: 1px; background: linear-gradient(90deg, var(--border2), transparent); }
.sec-count { font-size: 10px; color: var(--text-muted); font-family: 'Barlow Condensed', sans-serif; }

/* Grid */
.ach-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 28px; }

.empty { text-align: center; padding: 40px; color: var(--text-muted); font-size: 13px; font-style: italic; }

@media (max-width: 900px) {
  .ach-grid   { grid-template-columns: repeat(2, 1fr); }
  .stats-row  { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 500px) {
  .ach-grid { grid-template-columns: 1fr; }
}
</style>
