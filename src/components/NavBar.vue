<template>
  <nav class="navbar">
    <div class="nav-container">
      <!-- Logo -->
      <router-link to="/" class="logo-link">
        <div class="logo">Helse Midt-Norge MP</div>
      </router-link>

      <!-- Navigation Links -->
      <ul class="nav-links">
        <li><router-link to="/" class="nav-link">Hjem</router-link></li>
        <li><router-link to="/about" class="nav-link">Om oss</router-link></li>
        <li><router-link to="/tjenester" class="nav-link">Tjenester</router-link></li>
        <li><button @click="goToForum" class="nav-link" style="background: none; border: none; cursor: pointer;">Forum</button></li>
        <li><router-link to="/bangerfabrikken" class="nav-link">Bangerfabrikken</router-link></li>

        <!-- Authenticated User Dropdown -->
        <li v-if="auth.isAuthenticated" class="auth-dropdown">
          <div class="nav-avatar-wrap" ref="avatar" @click="toggleDropdown">
            <div class="nav-avatar">
              <img v-if="auth.user && auth.user.avatar" :src="auth.user.avatar" alt="User Avatar" />
              <span v-else>{{ userInitial }}</span>
            </div>
            <span v-if="hasUnreadNotifications" class="nav-unread-dot"></span>
          </div>

          <transition name="dd-slide">
            <div v-if="showDropdown" class="dd-menu" ref="dropdownMenu" @click.stop>

              <!-- Header -->
              <div class="dd-header">
                <div class="dd-avatar-row">
                  <div class="dd-av">
                    <img v-if="auth.user && auth.user.avatar" :src="auth.user.avatar" />
                    <span v-else>{{ userInitial }}</span>
                    <span class="dd-online-dot"></span>
                  </div>
                  <div>
                    <div class="dd-name">{{ userDisplayName }}</div>
                    <div class="dd-rank">{{ topRoleLabel }} · Online</div>
                  </div>
                </div>
              </div>

              <!-- Core nav items -->
              <div class="dd-section">
                <div class="dd-item" @click="viewProfile">
                  <span class="dd-icon">👤</span>
                  <span class="dd-label">Vis profil</span>
                </div>
                <div class="dd-item" @click="goToSettings">
                  <span class="dd-icon">⚙️</span>
                  <span class="dd-label">Innstillinger</span>
                </div>

                <!-- Notifications accordion -->
                <div class="dd-item" :class="{ 'is-open': showNotificationsList }" @click="toggleNotificationsList">
                  <span class="dd-icon">🔔</span>
                  <span class="dd-label">Varsler</span>
                  <span v-if="unreadNotificationCount > 0" class="dd-badge">{{ unreadNotificationCount }}</span>
                  <span class="dd-chevron">▾</span>
                </div>
                <div class="dd-panel" :class="{ open: showNotificationsList }">
                  <template v-if="notifications.length">
                    <div
                      v-for="notif in notifications.slice(0, 4)"
                      :key="notif.id"
                      class="notif-item"
                      :class="{ unread: !notif.is_read }"
                      @click="handleNotificationClick(notif)"
                    >
                      <div class="notif-dot" :style="{ background: notifDotColor(notif) }"></div>
                      <div class="notif-text">{{ notif.message }}</div>
                      <div class="notif-time">{{ formatNotifTime(notif.created_at) }}</div>
                    </div>
                    <div class="panel-footer" @click.stop="markAllAsRead">Se alle varsler</div>
                  </template>
                  <div v-else class="notif-empty">Ingen nye varsler</div>
                </div>

                <!-- Friend requests accordion -->
                <div class="dd-item" :class="{ 'is-open': showRequestsList }" @click="toggleRequestsList">
                  <span class="dd-icon">🤝</span>
                  <span class="dd-label">Venneforespørsler</span>
                  <span v-if="pendingRequests.length > 0" class="dd-badge">{{ pendingRequests.length }}</span>
                  <span class="dd-chevron">▾</span>
                </div>
                <div class="dd-panel" :class="{ open: showRequestsList }">
                  <template v-if="pendingRequests.length">
                    <div v-for="req in pendingRequests" :key="req.id" class="freq-item">
                      <div class="freq-avatar" :style="{ background: requestAvatarColor(req) }">
                        {{ (req.sender.username || req.sender.email || '?')[0].toUpperCase() }}
                      </div>
                      <div class="freq-info">
                        <div class="freq-name">{{ req.sender.username || req.sender.email }}</div>
                        <div class="freq-sub">{{ req.sender.roles && req.sender.roles[0] ? req.sender.roles[0].name : 'Bruker' }}</div>
                      </div>
                      <div class="freq-btns">
                        <button class="freq-btn freq-ok" @click.stop="acceptRequest(req.id)">✓</button>
                        <button class="freq-btn freq-no" @click.stop="declineRequest(req.id)">✕</button>
                      </div>
                    </div>
                  </template>
                  <div v-else class="notif-empty">Ingen ventende forespørsler</div>
                </div>
              </div>

              <!-- Dashboard link — role-based -->
              <template v-if="isAdminOrDev || isProducerOnly">
                <div class="dd-divider"></div>
                <div class="dd-section">
                  <div v-if="isAdminOrDev" class="dd-item admin-item" @click="goToAdminDashboard">
                    <span class="dd-icon">🛡️</span>
                    <span class="dd-label">Admin Dashboard</span>
                    <span class="dd-admin-pip"></span>
                  </div>
                  <div v-else class="dd-item admin-item" @click="goToProducerDashboard">
                    <span class="dd-icon">🎵</span>
                    <span class="dd-label">Music Dashboard</span>
                    <span class="dd-admin-pip"></span>
                  </div>
                </div>
              </template>

              <!-- Logout -->
              <div class="dd-divider"></div>
              <div class="dd-section">
                <div class="dd-item dd-logout" @click="logoutUser">
                  <span class="dd-icon">→</span>
                  <span class="dd-label">Logg ut</span>
                </div>
              </div>

            </div>
          </transition>
        </li>

        <!-- Login Button -->
        <li v-else>
          <button class="login-btn" @click="handleAuthAction">Logg inn</button>
        </li>
      </ul>
    </div>
  </nav>
</template>


<script>
import { useAuthStore } from '@/stores/authStore';
import axios from '@/axios';
import { listIncomingRequests, acceptFriendRequest, declineFriendRequest } from '@/services/friendRequestService';

export default {
  name: 'Navbar',
  emits: ['toggle-login'],
  data() {
    return {
      showDropdown: false,
      showNotificationsList: false,
      showRequestsList: false,
      notifications: [],
      pendingRequests: [],
      // ── DARK MODE ALWAYS ON ─────────────────────────────────────────
      // May remove or keep not sure yet
      // isDarkMode: localStorage.getItem('darkMode') === 'true',
      isDarkMode: true
      // ────────────────────────────────────────────────────────────────
    };
  },
      this.showDropdown = false;
      this.$router.push('/dashboard');
    },
    auth() {
      return useAuthStore();
    },
    userDisplayName() {
      const u = this.auth.user;
      return u?.username || u?.email || 'Bruker';
    },
    userInitial() {
      return (this.userDisplayName[0] || 'B').toUpperCase();
    },
    userRoles() {
      const u = this.auth.user;
      if (!u || !u.roles) return [];
      return u.roles.map(r => r.name.toLowerCase());
    },
    topRoleLabel() {
      const r = this.userRoles;
      if (r.includes('developer')) return 'Developer';
      if (r.includes('admin')) return 'Admin';
      if (r.includes('producer')) return 'Producer';
      if (r.includes('staff')) return 'Staff';
      if (r.includes('member')) return 'Medlem';
      return 'Bruker';
    },
    isAdminOrDev() {
      return this.userRoles.some(r => ['admin', 'developer', 'staff', 'moderator', 'superadmin'].includes(r));
    },
    isProducerOnly() {
      return !this.isAdminOrDev && this.userRoles.includes('producer');
    },
    unreadNotificationCount() {
      return this.notifications.filter(n => !n.is_read).length;
    },
    hasUnreadNotifications() {
      return this.pendingRequests.length > 0 || this.unreadNotificationCount > 0;
    }
  },
  methods: {
    async fetchNotifications() {
      try {
        const response = await axios.get('/get-notifications');
        this.notifications = response.data;
      } catch (error) {
        console.error('Error fetching notifications:', error);
      }
    },
    async fetchRequests() {
      try {
        const { data } = await listIncomingRequests();
        this.pendingRequests = data;
      } catch (e) {
        console.error('Failed to load friend requests:', e);
      }
    },
    toggleDropdown() {
      this.showDropdown = !this.showDropdown;
      if (this.showDropdown) {
        this.fetchNotifications();
        this.fetchRequests();
      }
    },
    toggleNotificationsList() {
      this.showNotificationsList = !this.showNotificationsList;
      if (this.showNotificationsList) this.showRequestsList = false;
    },
    toggleRequestsList() {
      this.showRequestsList = !this.showRequestsList;
      if (this.showRequestsList) {
        this.showNotificationsList = false;
        this.fetchRequests();
      }
    },
    async acceptRequest(id) {
      await acceptFriendRequest(id);
      this.pendingRequests = this.pendingRequests.filter(r => r.id !== id);
    },
    async declineRequest(id) {
      await declineFriendRequest(id);
      this.pendingRequests = this.pendingRequests.filter(r => r.id !== id);
    },
    async markAllAsRead() {
      try {
        await axios.post('/mark-notifications-read');
        this.notifications.forEach(n => n.is_read = true);
      } catch (error) {
        console.error('Error marking all as read:', error);
      }
    },
    async markNotificationAsRead(notificationId) {
      try {
        await axios.post('/mark-notification-read', { id: notificationId });
        this.notifications = this.notifications.map(n =>
          n.id === notificationId ? { ...n, is_read: true } : n
        );
      } catch (error) {
        console.error('Error marking notification as read:', error);
      }
    },
    handleNotificationClick(notification) {
      if (notification.related_object_id) {
        this.$router.push({ name: 'EventDetail', params: { eventId: notification.related_object_id } });
      }
      this.markNotificationAsRead(notification.id);
    },
    formatNotifTime(dateStr) {
      if (!dateStr) return '';
      const diff = Date.now() - new Date(dateStr).getTime();
      const mins = Math.floor(diff / 60000);
      if (mins < 1) return 'nå';
      if (mins < 60) return `${mins}m`;
      const hours = Math.floor(mins / 60);
      if (hours < 24) return `${hours}t`;
      const days = Math.floor(hours / 24);
      if (days === 1) return 'i går';
      return `${days}d`;
    },
    notifDotColor(notif) {
      if (!notif.is_read) {
        if (notif.type === 'friend_request') return 'var(--cyan)';
        if (notif.type === 'event_created') return 'var(--gold)';
        if (notif.type === 'achievement') return 'var(--green)';
        return 'var(--cyan)';
      }
      return 'var(--text-muted)';
    },
    requestAvatarColor(req) {
      const name = req.sender.username || req.sender.email || '?';
      const hue = (name.charCodeAt(0) * 137) % 360;
      return `linear-gradient(135deg, hsl(${hue},55%,22%), hsl(${hue},55%,12%))`;
    },
    goToForum() {
      window.location.href = 'https://forum.hmnmentalpasienter.no';
    },
    goToSettings() {
      this.showDropdown = false;
      this.$router.push('/settings');
    },
    viewProfile() {
      this.showDropdown = false;
      this.$router.push('/dashboard');
    },
    goToAdminDashboard() {
      this.showDropdown = false;
      this.$router.push('/management');
    },
    goToProducerDashboard() {
      this.showDropdown = false;
      this.$router.push('/management');
    },
    handleAuthAction() {
      this.auth.isAuthenticated ? this.logoutUser() : this.$emit('toggle-login');
    },
    logoutUser() {
      this.auth.logout();
      this.showDropdown = false;
      this.$router.push('/');
    },
    toggleDarkMode() {
      // ── DARK MODE ALWAYS ON ─────────────────────────────────────────
      // May remove or keep not sure yet
      // this.isDarkMode = !this.isDarkMode;
      // document.documentElement.classList.toggle('dark-mode', this.isDarkMode);
      // localStorage.setItem('darkMode', this.isDarkMode);
      // ────────────────────────────────────────────────────────────────
    },
    handleClickOutside(event) {
      if (this.showDropdown && this.$refs.avatar && this.$refs.dropdownMenu) {
        if (!this.$refs.avatar.contains(event.target) && !this.$refs.dropdownMenu.contains(event.target)) {
          this.showDropdown = false;
          this.showNotificationsList = false;
          this.showRequestsList = false;
        }
      }
    }
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside);
    // ── DARK MODE ALWAYS ON ─────────────────────────────────────────
    // May remove or keep not sure yet
    // document.documentElement.classList.toggle('dark-mode', this.isDarkMode);
    document.documentElement.classList.add('dark-mode');
    // ────────────────────────────────────────────────────────────────
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  }
};
</script>

<style scoped>
/* ── NAV SHELL ── */
.hmn-navbar {
  background-color: #ffffff;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  padding: 0.75rem 0;
}
.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 1.5rem;
}
.logo-link { text-decoration: none; color: inherit; }
.logo { font-size: 1.5rem; font-weight: bold; color: #2c3e50; }
.nav-links { display: flex; gap: 1.5rem; list-style: none; align-items: center; }
.nav-link { text-decoration: none; color: #34495e; font-weight: 500; transition: color 0.3s; }
.nav-link:hover { color: #3498db; }
.nav-links button.nav-link {
  background: none; border: none; cursor: pointer;
  font-size: inherit; font-family: inherit; padding: 0;
}
.login-btn {
  background-color: #3498db; color: white; border: none;
  padding: 0.75rem 1.25rem; border-radius: 5px; cursor: pointer;
  transition: background-color 0.3s;
}
.login-btn:hover { background-color: #2980b9; }

/* ── DARK MODE NAV ── */
.dark-mode .hmn-navbar { background-color: var(--card-bg, #16151d); }
.dark-mode .logo { color: #ffffff; }
.dark-mode .nav-link { color: var(--text, #b8ccd8); }
.dark-mode .nav-links button.nav-link { color: var(--text, #b8ccd8); }

/* ── AUTH DROPDOWN CONTAINER ── */
.auth-dropdown { position: relative; }
.nav-avatar-wrap { position: relative; cursor: pointer; display: inline-flex; }
.nav-avatar {
  width: 38px; height: 38px; border-radius: 50%; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #c8102e, #7a0e1e);
  color: white; font-family: 'Barlow Condensed', sans-serif;
  font-size: 15px; font-weight: 900; border: 2px solid rgba(200,16,46,0.3);
}
.nav-avatar img { width: 100%; height: 100%; object-fit: cover; }
.nav-unread-dot {
  position: absolute; top: -1px; right: -1px;
  width: 10px; height: 10px; background: #c8102e;
  border-radius: 50%; border: 2px solid white;
}

/* ── DROPDOWN MENU ── */
.dd-menu {
  position: absolute; right: 0; top: calc(100% + 10px);
  width: 256px; background: #0c121c;
  border: 1px solid rgba(255,255,255,0.11); border-radius: 12px; overflow: hidden;
  box-shadow: 0 24px 64px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.04);
  z-index: 1000;
}
.dd-menu::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 60px;
  background: radial-gradient(ellipse 80% 100% at 50% 0%, rgba(0,184,208,0.06), transparent);
  pointer-events: none;
}

/* ── HEADER ── */
.dd-header {
  padding: 16px 16px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  position: relative; z-index: 1;
}
.dd-avatar-row { display: flex; align-items: center; gap: 12px; }
.dd-av {
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, #c8102e, #7a0e1e);
  border: 2px solid rgba(200,16,46,0.35); box-shadow: 0 0 14px rgba(200,16,46,0.2);
  display: flex; align-items: center; justify-content: center;
  font-family: 'Barlow Condensed', sans-serif; font-size: 16px; font-weight: 900; color: white;
  flex-shrink: 0; position: relative; overflow: hidden;
}
.dd-av img { width: 100%; height: 100%; object-fit: cover; }
.dd-online-dot {
  position: absolute; bottom: 1px; right: 1px;
  width: 10px; height: 10px; background: #28b860;
  border-radius: 50%; border: 2px solid #0c121c; box-shadow: 0 0 6px #28b860;
}
.dd-name {
  font-family: 'Barlow Condensed', sans-serif; font-size: 17px; font-weight: 900;
  color: #eaf2ff; letter-spacing: 0.03em; line-height: 1;
}
.dd-rank { font-size: 11px; color: #3d5668; margin-top: 3px; }

/* ── SECTION / DIVIDER ── */
.dd-section { padding: 6px; }
.dd-divider { height: 1px; background: rgba(255,255,255,0.07); margin: 2px 0; }

/* ── NAV ITEM ── */
.dd-item {
  display: flex; align-items: center; gap: 10px; padding: 9px 10px;
  border-radius: 7px; font-size: 13px; color: #b8ccd8; cursor: pointer;
  transition: all 0.15s; font-family: 'Barlow', sans-serif; font-weight: 500;
  user-select: none;
}
.dd-item:hover { background: rgba(255,255,255,0.05); color: #eaf2ff; }
.dd-item:hover .dd-icon { color: #00b8d0; }
.dd-item.is-open {
  background: rgba(0,184,208,0.06); color: #eaf2ff;
  border-radius: 7px 7px 0 0;
}
.dd-item.is-open .dd-icon { color: #00b8d0; }
.dd-item.is-open .dd-chevron { transform: rotate(180deg); color: #00b8d0; }
.dd-icon { width: 18px; text-align: center; font-size: 14px; color: #3d5668; transition: color 0.15s; flex-shrink: 0; }
.dd-label { flex: 1; }
.dd-chevron { font-size: 10px; color: #3d5668; transition: transform 0.2s, color 0.2s; }
.dd-badge {
  min-width: 18px; height: 18px; border-radius: 9px;
  background: #c8102e; color: white; font-size: 10px; font-weight: 700;
  font-family: 'Barlow Condensed', sans-serif;
  display: flex; align-items: center; justify-content: center; padding: 0 5px;
}

/* ── ADMIN ITEM ── */
.dd-item.admin-item:hover { background: rgba(0,184,208,0.06); }
.dd-admin-pip {
  width: 6px; height: 6px; border-radius: 50%;
  background: #00b8d0; box-shadow: 0 0 5px #00b8d0; flex-shrink: 0;
}

/* ── LOGOUT ── */
.dd-item.dd-logout { color: rgba(255,255,255,0.3); }
.dd-item.dd-logout:hover { background: rgba(200,16,46,0.08); color: #e8304a; }
.dd-item.dd-logout:hover .dd-icon { color: #e8304a; }

/* ── ACCORDION PANEL ── */
.dd-panel {
  display: none; background: rgba(0,0,0,0.25);
  border-top: 1px solid rgba(255,255,255,0.07);
  border-bottom: 1px solid rgba(255,255,255,0.07);
  padding: 10px; flex-direction: column; gap: 7px;
  margin: 0 0 2px; border-radius: 0 0 7px 7px;
}
.dd-panel.open { display: flex; }

/* ── NOTIFICATION ITEM ── */
.notif-item {
  display: flex; align-items: flex-start; gap: 9px; padding: 9px 10px;
  border-radius: 7px; background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07); cursor: pointer; transition: background 0.15s;
}
.notif-item:hover { background: rgba(255,255,255,0.06); }
.notif-item.unread { border-color: rgba(0,184,208,0.18); }
.notif-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; margin-top: 4px; }
.notif-text { font-size: 12px; color: rgba(255,255,255,0.5); font-family: 'Barlow', sans-serif; line-height: 1.55; flex: 1; }
.notif-time { font-size: 10px; color: #3d5668; white-space: nowrap; margin-top: 1px; flex-shrink: 0; }
.notif-empty { font-size: 12px; color: #3d5668; font-family: 'Barlow', sans-serif; font-style: italic; text-align: center; padding: 10px 0; }

/* ── FRIEND REQUEST ITEM ── */
.freq-item {
  display: flex; align-items: center; gap: 10px; padding: 8px 10px;
  border-radius: 7px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
}
.freq-avatar {
  width: 30px; height: 30px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Barlow Condensed', sans-serif; font-size: 12px; font-weight: 900; color: white; flex-shrink: 0;
}
.freq-info { flex: 1; min-width: 0; }
.freq-name { font-size: 12px; font-weight: 600; color: #eaf2ff; font-family: 'Barlow', sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.freq-sub { font-size: 10px; color: #3d5668; }
.freq-btns { display: flex; gap: 5px; flex-shrink: 0; }
.freq-btn {
  padding: 4px 9px; border-radius: 4px; font-size: 10px; font-weight: 700;
  font-family: 'Barlow Condensed', sans-serif; letter-spacing: 0.05em; text-transform: uppercase;
  cursor: pointer; border: none; transition: all 0.15s;
}
.freq-ok { background: rgba(40,184,96,0.15); color: #28b860; border: 1px solid rgba(40,184,96,0.25); }
.freq-ok:hover { background: rgba(40,184,96,0.28); }
.freq-no { background: rgba(255,255,255,0.04); color: #3d5668; border: 1px solid rgba(255,255,255,0.11); }
.freq-no:hover { background: rgba(200,16,46,0.08); color: #e8304a; border-color: rgba(200,16,46,0.2); }

/* ── PANEL FOOTER ── */
.panel-footer { font-size: 11px; color: #00b8d0; text-align: center; cursor: pointer; padding: 4px 0 2px; font-family: 'Barlow', sans-serif; }
.panel-footer:hover { text-decoration: underline; }

/* ── TRANSITION ── */
.dd-slide-enter-active, .dd-slide-leave-active { transition: opacity 0.18s ease, transform 0.18s ease; }
.dd-slide-enter-from, .dd-slide-leave-to { opacity: 0; transform: translateY(-8px) scale(0.97); }
</style>

