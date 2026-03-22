<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <div class="g2 reveal mb48">
    <!-- Featured melding -->
    <div class="melding">
      <template v-if="loading.featuredMelding">
        <div class="melding-top">
          <span class="skel skel-sm"></span>
          <span class="skel skel-xs" style="margin-left:auto"></span>
        </div>
        <div class="melding-body">
          <div class="skel skel-title mb16"></div>
          <div class="skel skel-line mb8"></div>
          <div class="skel skel-line mb8" style="width:80%"></div>
          <div class="skel skel-line mb16" style="width:60%"></div>
        </div>
      </template>
      <template v-else>
        <div class="melding-top">
          <span class="melding-dot"></span>
          <span class="melding-kicker">Ny melding · {{ featuredMelding?.ref || 'HMN-MSG-019' }}</span>
          <span class="melding-date">{{ formatDate(featuredMelding?.date) || '19. mars 2026' }}</span>
        </div>
        <div class="melding-body">
          <div class="melding-title">{{ featuredMelding?.title || 'Ny portal.\nSamme mentale standard.' }}</div>
          <p class="melding-text">
            {{ featuredMelding?.body || 'HMN går inn i en ny designæra. Penere grensesnitt, bedre oversikt — kaoset er det samme. § 7.7 garanterer fortsatt ingenting. Årsaken til tidligere hendelser er fortsatt under utredning.' }}
          </p>
          <div class="melding-actions">
            <router-link
              :to="featuredMelding?.id
                ? `/bedriftsmeldinger/${featuredMelding.id}`
                : (featuredMelding?.ctaRoute || '/news')"
              class="btn btn-red"
            >{{ featuredMelding?.ctaLabel || 'Les melding' }}</router-link>
            <button class="btn btn-ghost" @click="$router.push(featuredMelding?.secondaryRoute || '/about')">
              {{ featuredMelding?.secondaryLabel || 'Hva er HMN?' }}
            </button>
          </div>
        </div>
      </template>
    </div>

    <!-- Updates list -->
    <div class="updates">
      <template v-if="loading.meldinger">
        <div v-for="i in 3" :key="i" class="upd">
          <div class="skel skel-sm mb8"></div>
          <div class="skel skel-xs mb6"></div>
          <div class="skel skel-line" style="width:75%"></div>
        </div>
      </template>
      <template v-else>
        <div
          v-for="item in displayMeldinger"
          :key="item.id || item.title"
          class="upd"
          @click="item.id ? $router.push(`/bedriftsmeldinger/${item.id}`) : $router.push('/news')"
        >
          <div class="upd-title">{{ item.title }}</div>
          <div class="upd-meta">{{ item.meta }}</div>
          <div class="upd-desc">{{ item.desc }}</div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
defineProps({
  loading: { type: Object, required: true },
  featuredMelding: { type: Object, default: null },
  displayMeldinger: { type: Array, required: true },
  formatDate: { type: Function, required: true },
})
</script>

<style scoped>
/* ── Featured melding ── */
.melding {
  background: rgba(255,255,255,0.028);
  border: 1px solid var(--border2);
  border-radius: var(--r-lg);
  overflow: hidden;
  transition: border-color 0.2s;
}
.melding:hover { border-color: rgba(255,255,255,0.15); }
.melding-top {
  padding: 12px 18px;
  border-bottom: 1px solid var(--border);
  background: rgba(0,184,208,0.05);
  display: flex;
  align-items: center;
  gap: 10px;
}
.melding-dot {
  width: 7px; height: 7px;
  background: var(--cyan);
  border-radius: 50%;
  box-shadow: 0 0 9px var(--cyan);
  flex-shrink: 0;
}
.melding-kicker {
  font-size: 11px; color: var(--cyan);
  letter-spacing: 0.07em; font-weight: 600;
  font-family: var(--font-display); text-transform: uppercase;
}
.melding-date { margin-left: auto; font-size: 11px; color: var(--text-muted); font-family: var(--font-ui); }
.melding-body { padding: 20px 20px 22px; }
.melding-title {
  font-family: var(--font-display); font-size: 26px; font-weight: 900;
  color: var(--text-bright); line-height: 1.05; text-transform: uppercase;
  letter-spacing: 0.02em; margin-bottom: 10px; white-space: pre-line;
}
.melding-text {
  color: rgba(255,255,255,0.32); font-size: 13px; line-height: 1.8;
  margin-bottom: 18px; font-family: var(--font-body);
}
.melding-actions { display: flex; gap: 10px; }

/* ── Buttons ── */
.btn {
  display: inline-flex; align-items: center; gap: 7px; padding: 9px 20px;
  border-radius: var(--r-md); font-size: 13px; font-weight: 600;
  font-family: var(--font-body); cursor: pointer; border: none;
  transition: all 0.18s; letter-spacing: 0.02em;
}
.btn:hover { transform: translateY(-1px); }
.btn-red { background: linear-gradient(145deg, var(--red), #8a0e1e); color: white; box-shadow: var(--shadow-red); }
.btn-red:hover { box-shadow: var(--shadow-red2); }
.btn-ghost { background: rgba(255,255,255,0.04); border: 1px solid var(--border2); color: var(--text); }
.btn-ghost:hover { background: rgba(255,255,255,0.08); }

/* ── Updates list ── */
.updates { background: rgba(255,255,255,0.018); border: 1px solid var(--border); border-radius: var(--r-lg); overflow: hidden; }
.upd {
  padding: 15px 18px; border-bottom: 1px solid var(--border);
  transition: background 0.15s; cursor: pointer; position: relative; overflow: hidden;
}
.upd::before {
  content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 2px;
  background: transparent; transition: background 0.2s; border-radius: 0 2px 2px 0;
}
.upd:hover { background: rgba(255,255,255,0.03); }
.upd:hover::before { background: var(--cyan); }
.upd:last-child { border-bottom: none; }
.upd-title { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 3px; font-family: var(--font-body); }
.upd-meta  { font-size: 11px; color: var(--text-muted); margin-bottom: 4px; font-family: var(--font-ui); }
.upd-desc  { font-size: 12px; color: rgba(255,255,255,0.2); line-height: 1.6; font-family: var(--font-body); }
</style>
