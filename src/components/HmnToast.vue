<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <Teleport to="body">
    <TransitionGroup name="toast" tag="div" class="toast-wrap">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="t.variant">
        <span class="toast-dot"></span>
        <span class="toast-msg">{{ t.message }}</span>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const toasts = ref([])
let nextId = 0

function show(message, variant = 'info', duration = 4000) {
  const id = ++nextId
  toasts.value.push({ id, message, variant })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, duration)
}

defineExpose({ show })
</script>

<style scoped>
.toast-wrap {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: var(--z-toast);
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}

.toast {
  background: var(--surface3);
  border: 1px solid var(--border2);
  border-radius: var(--r-lg);
  padding: 12px 16px;
  min-width: 260px;
  max-width: 340px;
  box-shadow: var(--shadow-md);
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-ui);
  font-size: 13px;
  color: var(--text);
  pointer-events: auto;
  animation: toastIn 0.25s ease;
}

.toast-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.toast.success { border-color: var(--green-border); }
.toast.success .toast-dot { background: var(--green); box-shadow: 0 0 8px var(--green); }

.toast.error { border-color: var(--red-border); }
.toast.error .toast-dot { background: var(--red2); box-shadow: 0 0 8px var(--red2); }

.toast.warning { border-color: var(--gold-border); }
.toast.warning .toast-dot { background: var(--gold); box-shadow: 0 0 8px var(--gold); }

.toast.info { border-color: var(--cyan-border); }
.toast.info .toast-dot { background: var(--cyan); box-shadow: 0 0 8px var(--cyan); }

.toast-enter-active { animation: toastIn 0.25s ease; }
.toast-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.toast-leave-to { opacity: 0; transform: translateX(20px); }
</style>
