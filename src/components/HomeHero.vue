<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <section class="hero">
    <div class="hero-bg"></div>
    <div class="hero-grid"></div>
    <div class="hmn-container">
      <div class="hero-inner">
        <!-- Left: copy + CTA -->
        <div class="reveal">
          <div class="eyebrow">
            <span class="eyebrow-dot"></span>
            <span class="eyebrow-text">Portal online · Alle systemer nominelt kaotiske</span>
          </div>
          <h1>
            <span class="t1">Profesjonelt</span>
            <span class="t2">Uansvarlige</span>
            <span class="t3">Siden 2024 · § 1.1</span>
          </h1>
          <p class="hero-desc">
            Et internt univers for <strong>6 venner fra Trondheim</strong> med særegen
            dømmekraft. Hendelser, musikk, gaming og
            <strong>full kontroll på totalt ukontrollert drift</strong>.
            Årsaken til de fleste hendelser er fortsatt under utredning.
          </p>
          <div class="hero-cta">
            <button class="btn btn-red" @click="$router.push('/login')">Logg inn</button>
            <button class="btn btn-ghost" @click="$router.push('/about')">Hva er dette egentlig?</button>
          </div>
          <div class="hero-pills">
            <div class="hpill">🏥 Godkjent av ingen</div>
            <div class="hpill">📍 Trondheim</div>
            <div class="hpill">🎮 Steam · Xbox · Battle.net</div>
          </div>
        </div>

        <!-- Right: Pasientstatus panel -->
        <div class="reveal">
          <div class="sp">
            <div class="sp-head">
              <span class="sp-head-title">Pasientstatus</span>
              <span class="sp-live"><span class="sp-live-dot"></span>Live</span>
            </div>
            <template v-if="loading.stats">
              <div v-for="i in 4" :key="i" class="sp-row">
                <span class="skel skel-sm"></span>
                <span class="skel skel-xs"></span>
              </div>
            </template>
            <template v-else>
              <div class="sp-row">
                <span class="sp-key">Krenkethetsnivå</span>
                <span class="sp-val c-red">{{ krenkethetLabel }}</span>
              </div>
              <div class="sp-row">
                <span class="sp-key">Pasienter online</span>
                <span class="sp-val c-green">{{ stats.pasienter_online !== null ? stats.pasienter_online + ' / 6' : '— / 6' }}</span>
              </div>
              <div class="sp-row">
                <span class="sp-key">Kommende hendelser</span>
                <span class="sp-val c-cyan">{{ stats.kommende_hendelser_count !== null ? stats.kommende_hendelser_count : '—' }}</span>
              </div>
              <div class="sp-row">
                <span class="sp-key">Uforklarte hendelser</span>
                <span class="sp-val c-gold">∞</span>
              </div>
            </template>
            <div class="sp-bar">
              <div class="sp-bar-labels">
                <span>Krenkethet index</span>
                <span class="c-red">{{ stats.krenkethet_index }}%</span>
              </div>
              <div class="sp-bar-track">
                <div class="sp-bar-fill" :style="{ width: stats.krenkethet_index + '%' }"></div>
              </div>
            </div>
            <div class="sp-foot">
              <div class="sp-foot-stat">
                <div class="sp-fval">6</div>
                <div class="sp-flabel">Pasienter</div>
              </div>
              <div class="sp-foot-stat">
                <div class="sp-fval" style="color: var(--gold)">{{ stats.kommende_hendelser_count !== null ? stats.kommende_hendelser_count : '—' }}</div>
                <div class="sp-flabel">Hendelser</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  loading: { type: Object, required: true },
  stats: { type: Object, required: true },
  krenkethetLabel: { type: String, required: true },
})
</script>

<style scoped>
.hero { position: relative; overflow: hidden; }

.hero-bg {
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 72% 45%, rgba(0,184,208,0.05), transparent 60%),
    radial-gradient(ellipse 45% 55% at 8% 75%, rgba(200,16,46,0.07), transparent 55%),
    radial-gradient(ellipse 50% 35% at 88% 88%, rgba(112,80,216,0.05), transparent 50%),
    linear-gradient(180deg, #050910 0%, var(--bg) 100%);
}
.hero-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(0,184,208,0.022) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,184,208,0.022) 1px, transparent 1px);
  background-size: 52px 52px;
  mask-image: linear-gradient(155deg, rgba(0,0,0,0.45) 0%, transparent 50%);
}
.hero-inner {
  padding: 88px 0 76px;
  display: grid;
  grid-template-columns: 1fr 390px;
  gap: 60px;
  align-items: center;
  position: relative;
  z-index: 2;
}

/* ── Eyebrow ── */
.eyebrow {
  display: inline-flex; align-items: center; gap: 10px;
  background: var(--cyan-bg); border: 1px solid var(--cyan-border);
  padding: 7px 15px; border-radius: var(--r-sm); margin-bottom: 22px;
}
.eyebrow-dot {
  width: 7px; height: 7px; background: var(--green); border-radius: 50%;
  box-shadow: 0 0 9px var(--green); animation: blink 2.5s infinite; flex-shrink: 0;
}
.eyebrow-text {
  color: var(--cyan); font-size: 11px; letter-spacing: 0.1em;
  font-family: var(--font-display); font-weight: 600; text-transform: uppercase;
}

/* ── Heading ── */
h1 {
  font-family: var(--font-display);
  font-size: clamp(4.4rem, 7.8vw, 8.4rem);
  font-weight: 900; line-height: 0.88;
  text-transform: uppercase; letter-spacing: -0.01em;
}
.t1 { color: var(--text-bright); display: block; }
.t2 {
  display: block;
  background: linear-gradient(92deg, var(--cyan) 0%, var(--cyan2) 50%, rgba(160,240,255,0.9) 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.t3 { display: block; color: rgba(255,255,255,0.1); font-size: 0.52em; letter-spacing: 0.1em; margin-top: 6px; }

.hero-desc { font-size: 15px; color: rgba(255,255,255,0.35); line-height: 1.85; max-width: 460px; margin: 22px 0 30px; }
.hero-desc strong { color: rgba(255,255,255,0.65); font-weight: 500; }
.hero-cta { display: flex; gap: 12px; margin-bottom: 24px; }
.hero-pills { display: flex; gap: 8px; flex-wrap: wrap; }
.hpill {
  display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px;
  border-radius: var(--r-sm); background: rgba(255,255,255,0.035);
  border: 1px solid var(--border); color: rgba(255,255,255,0.28);
  font-size: 11px; font-family: var(--font-ui);
}

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

/* ── Status Panel ── */
.sp {
  background: rgba(255,255,255,0.025); border: 1px solid var(--border2);
  border-radius: var(--r-xl); overflow: hidden;
  box-shadow: var(--shadow-lg), inset 0 1px 0 rgba(255,255,255,0.06);
}
.sp-head {
  padding: 13px 18px; border-bottom: 1px solid var(--border);
  background: rgba(255,255,255,0.025); display: flex;
  align-items: center; justify-content: space-between;
}
.sp-head-title {
  font-family: var(--font-display); font-size: 13px; font-weight: 800;
  color: var(--text-bright); letter-spacing: 0.1em; text-transform: uppercase;
}
.sp-live {
  display: flex; align-items: center; gap: 6px; font-size: 10px;
  color: var(--green); font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase; font-family: var(--font-display);
}
.sp-live-dot {
  width: 6px; height: 6px; background: var(--green); border-radius: 50%;
  box-shadow: 0 0 7px var(--green); animation: blink 2s infinite;
}
.sp-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 13px 18px; border-bottom: 1px solid var(--border);
  transition: background 0.15s; min-height: 48px;
}
.sp-row:hover { background: rgba(255,255,255,0.025); }
.sp-key { font-size: 12px; color: var(--text-muted); font-weight: 500; font-family: var(--font-ui); }
.sp-val { font-family: var(--font-display); font-size: 22px; font-weight: 800; letter-spacing: 0.01em; }
.sp-bar { padding: 13px 18px 10px; border-top: 1px solid var(--border); }
.sp-bar-labels {
  display: flex; justify-content: space-between; font-size: 11px;
  margin-bottom: 8px; color: var(--text-muted); font-family: var(--font-ui);
}
.sp-bar-track { background: rgba(255,255,255,0.06); height: 4px; border-radius: 2px; overflow: hidden; }
.sp-bar-fill {
  height: 100%; border-radius: 2px;
  background: linear-gradient(90deg, var(--red), var(--red2));
  box-shadow: 0 0 8px rgba(232,48,74,0.4); transition: width 0.6s ease;
}
.sp-foot { display: grid; grid-template-columns: 1fr 1fr; border-top: 1px solid var(--border); background: rgba(0,0,0,0.15); }
.sp-foot-stat { padding: 13px 18px; text-align: center; }
.sp-foot-stat:first-child { border-right: 1px solid var(--border); }
.sp-fval { font-family: var(--font-display); font-size: 26px; font-weight: 900; color: var(--text-bright); line-height: 1; }
.sp-flabel { font-size: 9px; color: var(--text-muted); letter-spacing: 0.1em; margin-top: 4px; text-transform: uppercase; font-family: var(--font-display); }
</style>
