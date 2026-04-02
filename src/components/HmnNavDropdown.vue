<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <div class="dropdown" @click.stop>
    <div class="dd-header">
      <div class="dd-username">{{ user?.username || 'Pasient' }}</div>
      <div class="dd-role">{{ topRoleLabel }}</div>
    </div>

    <div class="dd-divider"></div>

    <button class="dd-item" @click="$emit('view-profile')">
      <i class="fas fa-user"></i> Vis Profil
    </button>
    <button class="dd-item" @click="$emit('go-settings')">
      <i class="fas fa-cog"></i> Settings
    </button>
    <button v-if="canSeeDashboard" class="dd-item dd-item-dashboard" @click="$emit('go-dashboard')">
      <i :class="dashboardIcon"></i> {{ dashboardLabel }}
    </button>

    <div class="dd-divider"></div>

    <div class="dd-item" @click="$emit('toggle-notifications')">
      <i class="fas fa-bell"></i> Notifications
      <span v-if="unreadCount > 0" class="dd-badge">{{ unreadCount }}</span>
    </div>
    <transition name="slide-fade">
      <div v-if="showNotifications" class="dd-sublist">
        <template v-if="notifications.length">
          <div
            v-for="n in notifications"
            :key="n.id"
            class="dd-notif-item"
            @click="$emit('notification-click', n)"
          >
            {{ n.message }}
          </div>
          <button class="dd-item mark-read-btn" @click.stop="$emit('mark-all-read')">
            Merk alle som lest
          </button>
        </template>
        <div v-else class="dd-empty">Ingen nye varsler</div>
      </div>
    </transition>

    <div class="dd-item" @click="$emit('toggle-requests')">
      <i class="fas fa-user-friends"></i> Venneforesporsler
      <span v-if="pendingRequests.length > 0" class="dd-badge">{{ pendingRequests.length }}</span>
    </div>
    <transition name="slide-fade">
      <div v-if="showRequests" class="dd-sublist">
        <template v-if="pendingRequests.length">
          <div v-for="req in pendingRequests" :key="req.id" class="dd-req-item">
            <span>{{ req.sender?.username || req.sender?.email }}</span>
            <div class="dd-req-btns">
              <button class="dd-req-accept" @click="$emit('accept-request', req.id)">OK</button>
              <button class="dd-req-decline" @click="$emit('decline-request', req.id)">X</button>
            </div>
          </div>
        </template>
        <div v-else class="dd-empty">Ingen foresporsler</div>
      </div>
    </transition>

    <!-- ── DARK MODE TOGGLE ──────────────────────────────────────────
    May remove or keep not sure yet
    <div class="dd-divider"></div>

    <button class="dd-item" @click="$emit('toggle-dark')">
      <i :class="isDarkMode ? 'fas fa-sun' : 'fas fa-moon'"></i>
      {{ isDarkMode ? 'Lys modus' : 'Mork modus' }}
    </button>

    <div class="dd-divider"></div>
    ─────────────────────────────────────────────────────────────── -->

    <button class="dd-item dd-logout" @click="$emit('logout')">
      <i class="fas fa-sign-out-alt"></i> Utlogging
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { getDashboardFlavor, getRoleNames, hasPermission, hasAnyPermission } from '@/utils/permissions';

const props = defineProps({
  user: Object,
  notifications: { type: Array, default: () => [] },
  pendingRequests: { type: Array, default: () => [] },
  unreadCount: { type: Number, default: 0 },
  showNotifications: Boolean,
  showRequests: Boolean,
  isDarkMode: Boolean,
});

defineEmits([
  'view-profile', 'go-settings', 'go-dashboard',
  'toggle-notifications', 'toggle-requests',
  'notification-click', 'mark-all-read',
  'accept-request', 'decline-request',
  'toggle-dark', 'logout',
]);

const userRoles = computed(() => getRoleNames(props.user));

const isAdminOrStaff = computed(() =>
  userRoles.value.some(role => ['admin', 'developer', 'staff', 'moderator', 'superadmin'].includes(role))
);

const canAccessManagement = computed(() =>
  hasPermission(props.user, 'access_management') ||
  hasAnyPermission(props.user, ['manage_music', 'publish_bedriftsmeldinger', 'edit_bedriftsmeldinger'])
);

const isProducerOnly = computed(() =>
  !isAdminOrStaff.value && getDashboardFlavor(props.user) === 'music'
);

const canSeeDashboard = computed(() => isAdminOrStaff.value || canAccessManagement.value || isProducerOnly.value);

const dashboardLabel = computed(() =>
  getDashboardFlavor(props.user) === 'music' && !isAdminOrStaff.value ? 'Music Dashboard' : 'Dashboard'
);

const dashboardIcon = computed(() =>
  getDashboardFlavor(props.user) === 'music' && !isAdminOrStaff.value ? 'fas fa-sliders' : 'fas fa-shield-halved'
);

const topRoleLabel = computed(() => {
  if (userRoles.value.includes('superadmin')) return 'superadmin';
  if (userRoles.value.includes('admin')) return 'admin';
  if (userRoles.value.includes('developer')) return 'developer';
  if (userRoles.value.includes('staff')) return 'staff';
  if (userRoles.value.includes('moderator')) return 'moderator';
  if (userRoles.value.includes('producer')) return 'producer';
  return props.user?.roles?.[0]?.name || 'Member';
});
</script>

<style scoped>
.dropdown {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  min-width: 220px;
  background: var(--surface);
  border: 1px solid var(--border2);
  border-radius: var(--r-lg);
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(0,0,0,0.6);
  z-index: 100;
}

.dd-header { padding: 14px 16px 12px; border-bottom: 1px solid var(--border); }
.dd-username {
  font-family: var(--font-display); font-size: 15px; font-weight: 800;
  color: var(--text-bright); letter-spacing: 0.04em; text-transform: uppercase;
}
.dd-role { font-size: 10px; color: var(--text-muted); margin-top: 2px; font-family: var(--font-ui); }
.dd-divider { height: 1px; background: var(--border); margin: 4px 0; }

.dd-item {
  display: flex; align-items: center; gap: 10px; width: 100%;
  padding: 10px 16px; background: none; border: none; color: var(--text);
  font-size: 13px; font-family: var(--font-body); font-weight: 500;
  cursor: pointer; text-align: left; transition: background 0.15s, color 0.15s;
}
.dd-item:hover { background: rgba(255,255,255,0.05); color: var(--text-bright); }
.dd-item-dashboard { color: var(--cyan); }
.dd-item-dashboard:hover { background: rgba(0,184,208,0.08); }
.dd-logout { color: var(--red2); }
.dd-logout:hover { background: rgba(200,16,46,0.08); color: var(--red2); }

.dd-badge {
  margin-left: auto; background: var(--red2); color: white;
  font-size: 9px; font-weight: 700; padding: 2px 6px;
  border-radius: 10px; font-family: var(--font-display);
}

.dd-sublist {
  background: rgba(0,0,0,0.2); border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border); max-height: 200px; overflow-y: auto;
}
.dd-notif-item {
  padding: 9px 16px; font-size: 12px; color: var(--text);
  font-family: var(--font-ui); border-bottom: 1px solid var(--border);
  cursor: pointer; transition: background 0.15s;
}
.dd-notif-item:hover { background: rgba(255,255,255,0.04); }
.dd-notif-item:last-child { border-bottom: none; }

.dd-req-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 9px 16px; font-size: 12px; color: var(--text);
  font-family: var(--font-ui); border-bottom: 1px solid var(--border);
}
.dd-req-item:last-child { border-bottom: none; }
.dd-req-btns { display: flex; gap: 6px; }
.dd-req-accept, .dd-req-decline {
  width: 26px; height: 26px; border-radius: var(--r-sm);
  border: 1px solid var(--border); background: rgba(255,255,255,0.04);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 11px; transition: all 0.15s;
}
.dd-req-accept { color: var(--green); }
.dd-req-accept:hover { background: var(--green-bg); border-color: var(--green-border); }
.dd-req-decline { color: var(--red2); }
.dd-req-decline:hover { background: var(--red-bg); border-color: var(--red-border); }

.dd-empty { padding: 12px 16px; font-size: 12px; color: var(--text-muted); font-family: var(--font-ui); }
.mark-read-btn { font-size: 11px; color: var(--cyan); }

.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.2s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; max-height: 0; }
</style>
