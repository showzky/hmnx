<template>
  <div class="cl-page">
    <div class="hmn-container">

      <!-- Hero -->
      <div class="cl-hero">
        <div class="cl-hero-label">VERSIONSLOGG</div>
        <h1 class="cl-hero-title">Change<em>log</em></h1>
        <p class="cl-hero-sub">Oversikt over alle oppdateringer, endringer og fikser til HMN-plattformen.</p>
      </div>

      <!-- Empty -->
      <div v-if="changelogs.length === 0" class="cl-empty">
        <div class="cl-empty-title">Ingen versjoner funnet</div>
        <div class="cl-empty-sub">Kom tilbake senere.</div>
      </div>

      <!-- Entries -->
      <div v-else class="cl-list">
        <div
          v-for="entry in changelogs"
          :key="entry.id"
          class="cl-entry"
          :class="{ open: expandedIds.includes(entry.id) }"
        >
          <!-- Header row -->
          <div class="cl-entry-head" @click="toggleEntry(entry.id)">
            <span class="cl-version">v{{ entry.version }}</span>
            <span class="cl-date">{{ formatDate(entry.date) }}</span>
            <div class="cl-tags">
              <span v-if="entry.added?.length"   class="cl-tag cl-tag-added">+{{ entry.added.length }} lagt til</span>
              <span v-if="entry.changed?.length" class="cl-tag cl-tag-changed">~ {{ entry.changed.length }} endret</span>
              <span v-if="entry.fixed?.length"   class="cl-tag cl-tag-fixed">✓ {{ entry.fixed.length }} fikset</span>
              <span v-if="entry.removed?.length" class="cl-tag cl-tag-removed">− {{ entry.removed.length }} fjernet</span>
            </div>
            <svg class="cl-chevron" :class="{ rotated: expandedIds.includes(entry.id) }" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </div>

          <!-- Body -->
          <transition name="cl-expand">
            <div v-if="expandedIds.includes(entry.id)" class="cl-entry-body">
              <div v-if="entry.added?.length" class="cl-block cl-block-added">
                <div class="cl-block-label">
                  <span class="cl-block-icon">+</span> Lagt til
                </div>
                <ul class="cl-items">
                  <li v-for="item in entry.added" :key="item">{{ item }}</li>
                </ul>
              </div>
              <div v-if="entry.changed?.length" class="cl-block cl-block-changed">
                <div class="cl-block-label">
                  <span class="cl-block-icon">~</span> Endret
                </div>
                <ul class="cl-items">
                  <li v-for="item in entry.changed" :key="item">{{ item }}</li>
                </ul>
              </div>
              <div v-if="entry.fixed?.length" class="cl-block cl-block-fixed">
                <div class="cl-block-label">
                  <span class="cl-block-icon">✓</span> Fikset
                </div>
                <ul class="cl-items">
                  <li v-for="item in entry.fixed" :key="item">{{ item }}</li>
                </ul>
              </div>
              <div v-if="entry.removed?.length" class="cl-block cl-block-removed">
                <div class="cl-block-label">
                  <span class="cl-block-icon">−</span> Fjernet
                </div>
                <ul class="cl-items">
                  <li v-for="item in entry.removed" :key="item">{{ item }}</li>
                </ul>
              </div>
            </div>
          </transition>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Changelog',
  data() {
    return {
      changelogs: [],
      expandedIds: [],
    };
  },
  async mounted() {
    try {
      const res = await axios.get(`${import.meta.env.VITE_API_URL}/changelog`);
      this.changelogs = res.data;
    } catch (e) {
      console.error('Failed to fetch changelog', e);
    }
  },
  methods: {
    toggleEntry(id) {
      if (this.expandedIds.includes(id)) {
        this.expandedIds = this.expandedIds.filter(x => x !== id);
      } else {
        this.expandedIds.push(id);
      }
    },
    formatDate(raw) {
      if (!raw) return '';
      const d = new Date(raw);
      if (isNaN(d)) return raw;
      return d.toLocaleDateString('nb-NO', { year: 'numeric', month: 'long', day: 'numeric' });
    },
  },
};
</script>

<style scoped>
.cl-page {
  min-height: 80vh;
  padding: 60px 0 80px;
}

/* Hero */
.cl-hero {
  margin-bottom: 48px;
}
.cl-hero-label {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.18em;
  color: var(--cyan);
  text-transform: uppercase;
  margin-bottom: 10px;
}
.cl-hero-title {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: clamp(36px, 6vw, 56px);
  font-weight: 900;
  text-transform: uppercase;
  color: var(--text-bright);
  line-height: 1;
  margin: 0 0 12px;
  letter-spacing: 0.02em;
}
.cl-hero-title em {
  color: var(--cyan);
  font-style: normal;
}
.cl-hero-sub {
  font-family: 'Barlow', sans-serif;
  font-size: 14px;
  color: var(--text-muted);
  max-width: 480px;
}

/* Empty */
.cl-empty {
  text-align: center;
  padding: 80px 0;
}
.cl-empty-title {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 20px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-bright);
  margin-bottom: 8px;
}
.cl-empty-sub {
  font-size: 13px;
  color: var(--text-muted);
  font-family: 'Barlow', sans-serif;
}

/* List */
.cl-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* Entry */
.cl-entry {
  border: 1px solid var(--border);
  border-radius: 10px;
  background: rgba(255,255,255,0.025);
  overflow: hidden;
  transition: border-color 0.15s;
}
.cl-entry.open {
  border-color: rgba(0,184,208,0.25);
  background: rgba(255,255,255,0.035);
}

.cl-entry-head {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  cursor: pointer;
  user-select: none;
  transition: background 0.12s;
}
.cl-entry-head:hover {
  background: rgba(255,255,255,0.03);
}

.cl-version {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--cyan);
  min-width: 64px;
}
.cl-date {
  font-family: 'Barlow', sans-serif;
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
}
.cl-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  flex: 1;
}
.cl-tag {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid transparent;
}
.cl-tag-added   { background: rgba(34,197,94,0.1);  color: #4ade80; border-color: rgba(34,197,94,0.2); }
.cl-tag-changed { background: rgba(0,184,208,0.1);  color: var(--cyan); border-color: rgba(0,184,208,0.2); }
.cl-tag-fixed   { background: rgba(168,85,247,0.1); color: #c084fc; border-color: rgba(168,85,247,0.2); }
.cl-tag-removed { background: rgba(239,68,68,0.1);  color: #f87171; border-color: rgba(239,68,68,0.2); }

.cl-chevron {
  color: var(--text-muted);
  flex-shrink: 0;
  transition: transform 0.2s ease;
}
.cl-chevron.rotated {
  transform: rotate(180deg);
  color: var(--cyan);
}

/* Body */
.cl-entry-body {
  padding: 0 20px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  border-top: 1px solid var(--border);
  padding-top: 18px;
}

.cl-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.cl-block-label {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 6px;
}
.cl-block-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 900;
}

.cl-block-added   .cl-block-label { color: #4ade80; }
.cl-block-added   .cl-block-icon  { background: rgba(34,197,94,0.15); color: #4ade80; }
.cl-block-changed .cl-block-label { color: var(--cyan); }
.cl-block-changed .cl-block-icon  { background: rgba(0,184,208,0.15); color: var(--cyan); }
.cl-block-fixed   .cl-block-label { color: #c084fc; }
.cl-block-fixed   .cl-block-icon  { background: rgba(168,85,247,0.15); color: #c084fc; }
.cl-block-removed .cl-block-label { color: #f87171; }
.cl-block-removed .cl-block-icon  { background: rgba(239,68,68,0.15); color: #f87171; }

.cl-items {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.cl-items li {
  font-family: 'Barlow', sans-serif;
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.55;
  padding-left: 14px;
  position: relative;
}
.cl-items li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--border2);
}

/* Expand transition */
.cl-expand-enter-active,
.cl-expand-leave-active {
  transition: opacity 0.2s ease;
}
.cl-expand-enter-from,
.cl-expand-leave-to {
  opacity: 0;
}
</style>
