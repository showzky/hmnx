<template>
  <button 
    v-if="hasAdminAccess"
    class="action-btn admin-action"
    @click="goToManagement"
  >
    <i class="fas fa-shield-alt"></i>
    <span>Admin Panel</span>
  </button>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

const router = useRouter();
const auth = useAuthStore();

// Check if user has admin or developer role
const hasAdminAccess = computed(() => {
  const userRoles = auth.user?.roles || [];
  return userRoles.some(role => 
    role.name.toLowerCase() === 'admin' || 
    role.name.toLowerCase() === 'developer'
  );
});

const goToManagement = () => {
  router.push('/management');
};
</script>

<style scoped>
/* Inherits most styles from the parent action-btn class */
.admin-action {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text);
  transition: background 0.3s ease;
}

.admin-action:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* Dark mode support */
:root[class~="dark-mode"] .admin-action {
  background: rgba(255, 255, 255, 0.03);
}

:root[class~="dark-mode"] .admin-action:hover {
  background: rgba(255, 255, 255, 0.08);
}
</style> 