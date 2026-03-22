<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <div class="diag-strip">
    <div class="diag-inner">
      <span class="diag-label">Systemfeed</span>
      <div class="diag-scroll">
        <span class="diag-text">
          <template v-for="pass in 2" :key="pass">
            <template v-for="(item, idx) in tickerItems" :key="pass + '-' + idx">
              <em v-if="item.highlight">{{ item.text }}</em>
              <span v-else>{{ item.text }}</span>
              <span class="sep">&nbsp;·&nbsp;</span>
            </template>
          </template>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ tickerItems: { type: Array, required: true } })
</script>

<style scoped>
.diag-strip {
  background: rgba(0,0,0,0.3);
  border-top: 1px solid rgba(0,184,208,0.08);
  border-bottom: 1px solid var(--border);
  padding: 10px 0;
  overflow: hidden;
  position: relative;
}
.diag-strip::before,
.diag-strip::after {
  content: '';
  position: absolute;
  top: 0; bottom: 0;
  width: 80px;
  z-index: 2;
  pointer-events: none;
}
.diag-strip::before { left: 0; background: linear-gradient(90deg, var(--bg), transparent); }
.diag-strip::after  { right: 0; background: linear-gradient(-90deg, var(--bg), transparent); }

.diag-inner { display: flex; align-items: center; padding: 0 2rem; }

.diag-label {
  color: var(--cyan);
  font-size: 10px;
  letter-spacing: 0.16em;
  font-weight: 700;
  font-family: var(--font-display);
  text-transform: uppercase;
  white-space: nowrap;
  flex-shrink: 0;
  margin-right: 24px;
}
.diag-scroll { overflow: hidden; flex: 1; }
.diag-text {
  display: inline-block;
  white-space: nowrap;
  color: rgba(255,255,255,0.16);
  font-size: 11px;
  font-family: var(--font-ui);
  animation: ticker 48s linear infinite;
}
.diag-text em { color: rgba(255,255,255,0.42); font-style: normal; }
.sep { color: rgba(255,255,255,0.1); }
</style>
