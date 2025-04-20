<template>
  <div v-if="shouldShowBanner" 
       :class="['maintenance-banner', { 'is-active': maintenanceStatus.isActive }]">
    <div class="banner-content">
      <span class="fa fa-tools"></span>
      <span class="custom-message">{{ bannerMessage }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue';
import { useWebSocket } from '@/composables/useWebSocket';

const defaultMessage = 'System maintenance in progress. Please try again later.';
const { maintenanceStatus } = useWebSocket();

const shouldShowBanner = computed(() => {
  console.log('🎯 Computing shouldShowBanner:', {
    maintenanceStatus: maintenanceStatus.value,
    isActive: maintenanceStatus.value.isActive
  });
  return maintenanceStatus.value.isActive;
});

const bannerMessage = computed(() => {
  return maintenanceStatus.value.message || defaultMessage;
});

// Debug mounting and state changes
onMounted(() => {
  console.log('🏗 MaintenanceBanner mounted');
});

watch(maintenanceStatus, (newStatus) => {
  console.log('👀 maintenanceStatus changed:', newStatus);
}, { deep: true });

watch(shouldShowBanner, (newValue) => {
  console.log('🚩 shouldShowBanner changed:', newValue);
});
</script>

<style>
.maintenance-banner {
  top: 0;
  left: 0;
  right: 0;
  background-color: #ff9800;
  color: white;
  padding: 10px;
  text-align: center;
  z-index: 9999;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.banner-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.message-container {
  display: flex;
  align-items: center;
}

.custom-message {
  font-weight: 500;
}

.fa-tools {
  font-size: 1.2em;
  margin-right: 10px;
  color: black;
}
</style> 