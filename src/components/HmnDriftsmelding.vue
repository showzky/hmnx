<template>
  <div v-if="shouldShow" class="drifts-bar">
    <span class="drifts-dot"></span>
    <span class="drifts-tag">Driftsmelding</span>
    <span class="drifts-text">{{ visibleMessage }}</span>
    <span class="drifts-time">{{ visibleTime }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useWebSocket } from '@/composables/useWebSocket';

const { maintenanceStatus } = useWebSocket();

const visibleMessage = computed(() => maintenanceStatus.value.message || '');
const shouldShow = computed(() => maintenanceStatus.value.isActive && Boolean(visibleMessage.value.trim()));

const visibleTime = computed(() => {
  if (!maintenanceStatus.value.updatedAt) {
    return 'oppdatert nylig';
  }

  const updatedAt = new Date(maintenanceStatus.value.updatedAt);
  if (Number.isNaN(updatedAt.getTime())) {
    return 'oppdatert nylig';
  }

  return `oppdatert ${updatedAt.toLocaleDateString('nb-NO', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })}`;
});
</script>

<style scoped>
.drifts-bar {
  background: rgba(200, 16, 46, 0.06);
  border-bottom: 1px solid rgba(200, 16, 46, 0.15);
  padding: 7px 2rem;
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: var(--z-sticky);
  overflow: hidden;
}

.drifts-dot {
  width: 6px;
  height: 6px;
  background: #e8304a;
  border-radius: 50%;
  box-shadow: 0 0 7px #e8304a;
  flex-shrink: 0;
  animation: blink 2s infinite;
}

.drifts-tag {
  color: #e8304a;
  font-family: var(--font-display);
  font-size: 10px;
  letter-spacing: 0.14em;
  font-weight: 700;
  text-transform: uppercase;
  white-space: nowrap;
}

.drifts-text {
  color: rgba(255, 255, 255, 0.65);
  font-size: 11px;
  font-family: var(--font-ui);
  min-width: 0;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.drifts-time {
  margin-left: auto;
  color: #3d5668;
  font-size: 10px;
  font-family: var(--font-ui);
  white-space: nowrap;
  flex-shrink: 0;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.25; }
}

@media (max-width: 700px) {
  .drifts-bar {
    padding: 8px 14px;
    gap: 10px;
  }
  .drifts-time {
    display: none;
  }
}
</style>
