<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <Transition name="modal">
    <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal" :style="{ maxWidth }">
        <button class="modal-close" @click="$emit('close')">&times;</button>
        <div v-if="$slots.header || title" class="modal-header">
          <slot name="header">
            <div class="modal-title">{{ title }}</div>
            <div v-if="subtitle" class="modal-subtitle">{{ subtitle }}</div>
          </slot>
        </div>
        <div class="modal-body">
          <slot />
        </div>
        <div v-if="$slots.footer" class="modal-footer">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  maxWidth: { type: String, default: '460px' },
})

const emit = defineEmits(['close'])

function onEscape(e) {
  if (e.key === 'Escape') emit('close')
}

watch(() => props.show, (val) => {
  document.body.style.overflow = val ? 'hidden' : ''
})

onMounted(() => window.addEventListener('keydown', onEscape))
onUnmounted(() => {
  window.removeEventListener('keydown', onEscape)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.65);
  backdrop-filter: blur(8px);
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.modal {
  background: var(--surface3);
  border: 1px solid var(--border2);
  border-radius: var(--r-2xl);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  width: 100%;
  position: relative;
}
.modal::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 40% at 50% 0%, rgba(0,184,208,0.06), transparent 60%);
  pointer-events: none;
  z-index: 0;
}

.modal-header {
  padding: 20px 24px 16px;
  border-bottom: 1px solid var(--border);
  position: relative;
  z-index: 1;
}
.modal-title {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 900;
  color: var(--text-bright);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 4px;
}
.modal-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  font-family: var(--font-ui);
  line-height: 1.5;
}

.modal-body {
  padding: 20px 24px;
  position: relative;
  z-index: 1;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  position: relative;
  z-index: 1;
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 28px;
  height: 28px;
  border-radius: var(--r-md);
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 16px;
  transition: all var(--transition-fast);
  z-index: 2;
}
.modal-close:hover {
  background: rgba(255,255,255,0.09);
  color: var(--text);
}
</style>
