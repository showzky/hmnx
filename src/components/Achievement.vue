<template>
  <div class="ach-card" :class="[rarityClass, { locked: !achieved }]">
    <div class="badge-wrap">
      <div class="badge-img" :style="badgeBg">
        <img v-if="isImgUrl(imageSrc)" :src="imageSrc" :alt="title" />
        <span v-else v-html="imageSrc" />
      </div>
      <div class="badge-glow" />
      <div v-if="achieved" class="badge-check">✓</div>
      <div v-else class="badge-lock">🔒</div>
    </div>

    <span class="rarity-tag" :class="`rt-${rarityClass}`">{{ rarity }}</span>
    <div class="badge-name">{{ title }}</div>
    <div class="badge-desc">{{ description }}</div>

    <template v-if="achieved">
      <div class="badge-date unlocked">{{ unlockedLabel }}</div>
    </template>
    <template v-else-if="progress != null && progressMax">
      <div class="badge-progress">
        <div class="badge-progress-fill" :style="{ width: progressPct + '%', background: progressFill }" />
      </div>
      <div class="badge-date" style="margin-top:5px;">{{ progress }} / {{ progressMax }}</div>
    </template>
  </div>
</template>

<script>
export default {
  props: {
    svg:         String,
    icon:        String,
    title:       String,
    description: String,
    achieved:    Boolean,
    rarity:      { type: String, default: 'common' },
    glow_color:  String,
    unlocked_at: String,
    progress:    { type: Number, default: null },
    progressMax: { type: Number, default: null }
  },
  computed: {
    rarityClass() { return (this.rarity || 'common').toLowerCase() },
    imageSrc()    { return this.svg || this.icon },
    badgeBg() {
      const map = {
        legendary: 'background:rgba(216,152,32,0.08);border:1px solid rgba(216,152,32,0.2)',
        epic:      'background:rgba(112,80,216,0.12);border:1px solid rgba(112,80,216,0.25)',
        rare:      'background:rgba(0,184,208,0.08);border:1px solid rgba(0,184,208,0.2)',
        common:    'background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1)'
      }
      return map[this.rarityClass] || map.common
    },
    progressFill() {
      return { legendary: 'var(--gold)', epic: '#9070f0', rare: 'var(--cyan)', common: 'rgba(255,255,255,0.3)' }[this.rarityClass] || 'var(--cyan)'
    },
    progressPct() {
      return !this.progressMax ? 0 : Math.min(100, Math.round((this.progress / this.progressMax) * 100))
    },
    unlockedLabel() {
      if (!this.unlocked_at) return 'Låst opp automatisk'
      const d = new Date(this.unlocked_at)
      return isNaN(d) ? 'Låst opp automatisk'
        : 'Låst opp ' + d.toLocaleDateString('nb-NO', { day: 'numeric', month: 'long', year: 'numeric' })
    }
  },
  methods: {
    isImgUrl(src) {
      return typeof src === 'string' && (src.startsWith('http') || src.startsWith('data:image') || /\.(svg|png|jpe?g)$/.test(src))
    }
  }
}
</script>

<style scoped>
.ach-card {
  background: rgba(255,255,255,0.025);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
  overflow: hidden;
}
.ach-card:hover { transform: translateY(-3px); box-shadow: 0 14px 40px rgba(0,0,0,0.4); }
.ach-card.locked { opacity: 0.4; filter: grayscale(0.6); }
.ach-card.locked:hover { transform: none; box-shadow: none; }

/* Rarity top accent */
.ach-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.ach-card.legendary { border-color: rgba(216,152,32,0.25); background: rgba(216,152,32,0.04); }
.ach-card.legendary::before { background: linear-gradient(90deg, transparent, var(--gold), transparent); }
.ach-card.epic      { border-color: rgba(112,80,216,0.25); background: rgba(112,80,216,0.04); }
.ach-card.epic::before      { background: linear-gradient(90deg, transparent, #9070f0, transparent); }
.ach-card.rare      { border-color: rgba(0,184,208,0.2);   background: rgba(0,184,208,0.03); }
.ach-card.rare::before      { background: linear-gradient(90deg, transparent, var(--cyan), transparent); }
.ach-card.common::before    { background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent); }

/* Badge */
.badge-wrap { position: relative; margin-bottom: 14px; }
.badge-img {
  width: 80px; height: 80px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-size: 36px;
}
.badge-img img { width: 100%; height: 100%; object-fit: contain; border-radius: 50%; }

.badge-glow { position: absolute; inset: -6px; border-radius: 50%; opacity: 0; transition: opacity 0.2s; }
.ach-card:hover .badge-glow { opacity: 1; }
.legendary .badge-glow { background: radial-gradient(circle, rgba(216,152,32,0.25), transparent 70%); }
.epic      .badge-glow { background: radial-gradient(circle, rgba(112,80,216,0.25), transparent 70%); }
.rare      .badge-glow { background: radial-gradient(circle, rgba(0,184,208,0.2),   transparent 70%); }

.badge-check, .badge-lock {
  position: absolute; bottom: 0; right: 0;
  width: 22px; height: 22px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  border: 2px solid var(--bg2);
}
.badge-check { background: var(--green); color: white; font-size: 11px; font-weight: 700; box-shadow: 0 0 8px rgba(40,184,96,0.4); }
.badge-lock  { background: var(--surface2); border-color: var(--border2); color: var(--text-muted); font-size: 10px; }

/* Rarity tag */
.rarity-tag {
  font-size: 9px; padding: 2px 8px; border-radius: 3px; font-weight: 700;
  letter-spacing: 0.08em; text-transform: uppercase;
  font-family: 'Barlow Condensed', sans-serif; margin-bottom: 8px;
}
.rt-legendary { background: rgba(216,152,32,0.12); color: var(--gold);          border: 1px solid rgba(216,152,32,0.22); }
.rt-epic      { background: rgba(112,80,216,0.12); color: #9070f0;              border: 1px solid rgba(112,80,216,0.22); }
.rt-rare      { background: rgba(0,184,208,0.1);   color: var(--cyan);          border: 1px solid rgba(0,184,208,0.2); }
.rt-common    { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.4); border: 1px solid var(--border2); }

.badge-name { font-size: 14px; font-weight: 600; color: var(--text-bright); margin-bottom: 5px; line-height: 1.3; }
.badge-desc { font-size: 11px; color: rgba(255,255,255,0.35); line-height: 1.55; margin-bottom: 10px; transition: color 0.2s; }
.ach-card:hover .badge-desc { color: rgba(255,255,255,0.55); }

.badge-date { font-size: 10px; color: var(--text-muted); letter-spacing: 0.06em; text-transform: uppercase; font-family: 'Barlow Condensed', sans-serif; }
.badge-date.unlocked { color: var(--green); }

.badge-progress { width: 100%; background: rgba(255,255,255,0.06); height: 3px; border-radius: 2px; overflow: hidden; margin-top: 6px; }
.badge-progress-fill { height: 100%; border-radius: 2px; }
</style>
