<template>
  <header class="hmn-topbar">
    <div class="topbar-left">
      <div class="topbar-menu" aria-hidden="true"><span></span></div>
      <div>
        <div class="topbar-title">HMN Management</div>
        <div class="topbar-sub">Admin Dashboard</div>
      </div>
    </div>
    <div class="topbar-right">
      <span class="topbar-badge" :class="badgeClass">{{ topRole }}</span>
      <div class="topbar-user">
        <div class="topbar-avatar">{{ initial }}</div>
        <span class="topbar-name">{{ displayName }}</span>
      </div>
      <button class="topbar-back" @click="$router.back()">← Tilbake til siden</button>
    </div>
  </header>
</template>
<script>
export default {
  name: 'AdminHeader',
  props: {
    displayName: { type: String, default: '' },
    userRoles: { type: Array, default: () => [] }
  },
  computed: {
    topRole() {
      const priority = ['admin','developer','producer','junior','member'];
      const sorted = [...this.userRoles].sort((a, b) => priority.indexOf(a.toLowerCase()) - priority.indexOf(b.toLowerCase()));
      return (sorted[0] || 'user').toUpperCase();
    },
    badgeClass() {
      const r = this.topRole.toLowerCase();
      if (r === 'admin') return '';
      if (r === 'developer') return 'tb-cyan';
      if (r === 'producer') return 'tb-green';
      return 'tb-gold';
    },
    initial() {
      return this.displayName ? this.displayName[0].toUpperCase() : '?';
    }
  }
}
</script>
