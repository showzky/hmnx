<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <HmnModal :show="show" max-width="380px" @close="$emit('cancel')">
    <template #header>
      <div class="confirm-icon" :class="variant">
        <span v-if="variant === 'danger'">⚠️</span>
        <span v-else-if="variant === 'warn'">⚡</span>
        <span v-else>ℹ️</span>
      </div>
      <div class="confirm-title">{{ title }}</div>
    </template>

    <p class="confirm-message">{{ message }}</p>

    <template #footer>
      <button class="btn-cancel" @click="$emit('cancel')">Avbryt</button>
      <button
        :class="variant === 'danger' ? 'btn-danger' : 'btn-primary'"
        @click="$emit('confirm')"
      >
        {{ confirmLabel || 'Bekreft' }}
      </button>
    </template>
  </HmnModal>
</template>

<script setup>
import HmnModal from './HmnModal.vue'

defineProps({
  show: Boolean,
  title: { type: String, default: 'Bekreft handling' },
  message: { type: String, default: '' },
  variant: { type: String, default: 'danger' },
  confirmLabel: { type: String, default: '' },
})

defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.confirm-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--r-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-bottom: 14px;
}
.confirm-icon.danger { background: var(--red-bg); border: 1px solid var(--red-border); }
.confirm-icon.warn   { background: var(--gold-bg); border: 1px solid var(--gold-border); }
.confirm-icon.info   { background: var(--cyan-bg); border: 1px solid var(--cyan-border); }

.confirm-title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 900;
  color: var(--text-bright);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.confirm-message {
  font-size: 13px;
  color: var(--text);
  font-family: var(--font-ui);
  line-height: 1.65;
}

.btn-cancel {
  padding: 9px 20px;
  border-radius: var(--r-md);
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border2);
  color: var(--text);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all var(--transition-base);
}
.btn-cancel:hover { background: rgba(255,255,255,0.08); }

.btn-danger {
  background: linear-gradient(145deg, var(--red), #8a0e1e);
  color: white;
  border: none;
  padding: 9px 20px;
  border-radius: var(--r-md);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  cursor: pointer;
  box-shadow: var(--shadow-red);
  transition: all var(--transition-base);
}
.btn-danger:hover { box-shadow: var(--shadow-red2); transform: translateY(-1px); }

.btn-primary {
  background: linear-gradient(145deg, var(--cyan), #0090a8);
  color: white;
  border: none;
  padding: 9px 20px;
  border-radius: var(--r-md);
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  cursor: pointer;
  box-shadow: var(--shadow-cyan);
  transition: all var(--transition-base);
}
.btn-primary:hover { transform: translateY(-1px); }
</style>
