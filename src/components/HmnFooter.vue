<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <footer class="footer">
    <div class="hmn-container">
      <div class="footer-inner">
        <span>© 2024 HMN Mental Pasienter AS · org.nr 999 999 999</span>
        <span>GDPR-compliant* · v2.4.1 · § 12.4 alle rettigheter forbeholdt (vi mener det ikke)</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
// Hardcoded — no props
</script>

<style scoped>
.footer {
  background:    rgba(0,0,0,0.35);
  border-top:    1px solid var(--border);
  padding:       16px 0;
  margin-top:    auto;
}
.footer-inner {
  display:         flex;
  justify-content: space-between;
  align-items:     center;
  flex-wrap:       wrap;
  gap:             10px;
  font-size:       11px;
  color:           rgba(255,255,255,0.1);
  font-family:     var(--font-ui);
}
</style>
