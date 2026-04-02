<template>
  <button
    v-if="canSeeProducerButton"
    class="dropdown-item producer-btn"
    @click="goToProducerPanel"
  >
    <i class="fas fa-sliders"></i>
    Dashboard
  </button>
</template>

<script>
import { getDashboardFlavor, hasPermission, hasAnyPermission } from '@/utils/permissions';

export default {
  name: 'ProducerButton',
  computed: {
    canSeeProducerButton() {
      let user = null;
      try {
        user = JSON.parse(localStorage.getItem('user'));
      } catch {}
      if (!user) return false;
      return (
        hasPermission(user, 'access_management') ||
        hasAnyPermission(user, ['manage_music', 'publish_bedriftsmeldinger']) ||
        getDashboardFlavor(user) === 'music'
      );
    }
  },
  methods: {
    goToProducerPanel() {
      // Change this route to wherever your producer panel is
      this.$router.push('/management');
    }
  }
};
</script>

<style scoped>
.producer-btn {
  color: #fff;
  background: #43b581;
  font-weight: 600;
  border: none;
  border-radius: 6px;
  margin-bottom: 0.5rem;
  transition: background 0.2s;
}
.producer-btn:hover {
  background: #389e6b;
}
</style>
