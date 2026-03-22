<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <div class="nav-wrap">
    <div class="hmn-container">
      <nav>
        <!-- Brand -->
        <router-link to="/" class="brand">
          <div class="brand-mark">
            <div class="bmi">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
          <div>
            <div class="brand-name">HMN Mental Pasienter</div>
            <div class="brand-sub">Internt kaos siden 2024</div>
          </div>
        </router-link>

        <!-- Nav links -->
        <div class="nav-links">
          <router-link to="/"               class="nl" exact-active-class="active">Hjem</router-link>
          <router-link to="/bedriftsmeldinger" class="nl" active-class="active">Bedriftsmeldinger</router-link>
          <router-link to="/tjenester"      class="nl" active-class="active">Tjenester</router-link>
          <router-link to="/about"          class="nl" active-class="active">Om oss</router-link>
          <router-link to="/bangerfabrikken" class="nl" active-class="active">Bangerfabrikken</router-link>
          <!-- Forum is always dead — § 4.2 -->
          <span class="nl dead">Forum</span>
        </div>

        <!-- Right side: auth buttons or user avatar dropdown -->
        <div class="nav-btns">
          <template v-if="!auth.isAuthenticated">
            <button class="btn btn-ghost" @click="$emit('toggle-register')">Registrer deg</button>
            <button class="btn btn-red"   @click="handleAuthAction">Logg inn</button>
          </template>

          <template v-else>
            <!-- Notification / avatar area -->
            <div class="auth-area">
              <div class="avatar-wrap" ref="avatarRef" @click="toggleDropdown">
                <img v-if="auth.user?.avatar" :src="auth.user.avatar" alt="Avatar" class="avatar-img" />
                <i v-else class="fa-solid fa-user avatar-icon"></i>
                <span v-if="hasUnreadNotifications" class="notif-dot"></span>
              </div>

              <transition name="dropdown-fade">
                <HmnNavDropdown
                  v-if="showDropdown"
                  ref="dropdownRef"
                  :user="auth.user"
                  :notifications="notifications"
                  :pendingRequests="pendingRequests"
                  :unreadCount="unreadNotificationCount"
                  :showNotifications="showNotificationsList"
                  :showRequests="showRequestsList"
                  :isDarkMode="isDarkMode"
                  @view-profile="viewProfile"
                  @go-settings="goToSettings"
                  @go-dashboard="goToDashboard"
                  @toggle-notifications="toggleNotificationsList"
                  @toggle-requests="toggleRequestsList"
                  @notification-click="handleNotificationClick"
                  @mark-all-read="markAllAsRead"
                  @accept-request="acceptRequest"
                  @decline-request="declineRequest"
                  @toggle-dark="toggleDarkMode"
                  @logout="logoutUser"
                />
              </transition>
            </div>
          </template>
        </div>
      </nav>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/authStore';
import axios from '@/axios';
import { listIncomingRequests, acceptFriendRequest, declineFriendRequest } from '@/services/friendRequestService';
import ProducerButton from '@/components/ProducerButton.vue';
import HmnNavDropdown from '@/components/HmnNavDropdown.vue';

export default {
  name: 'HmnNav',
  components: { ProducerButton, HmnNavDropdown },
  emits: ['toggle-login', 'toggle-register'],

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
      isDarkMode: true,
      // ────────────────────────────────────────────────────────────────
    };
  },

  computed: {
    auth() {
      return useAuthStore();
    },
    unreadNotificationCount() {
      return this.notifications.filter(n => !n.is_read).length;
    },
    hasUnreadNotifications() {
      return this.pendingRequests.length > 0 || this.unreadNotificationCount > 0;
    },
  },

  methods: {
    async fetchNotifications() {
      try {
        const { data } = await axios.get('/get-notifications');
        this.notifications = data;
      } catch (e) {
        console.error('Error fetching notifications:', e);
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
        this.notifications.forEach(n => (n.is_read = true));
      } catch (e) {
        console.error('Error marking all as read:', e);
      }
    },
    async markNotificationAsRead(id) {
      try {
        await axios.post('/mark-notification-read', { id });
        this.notifications = this.notifications.map(n =>
          n.id === id ? { ...n, is_read: true } : n
        );
      } catch (e) {
        console.error('Error marking notification as read:', e);
      }
    },
    handleNotificationClick(notification) {
      if (notification.related_object_id) {
        this.$router.push({ name: 'EventDetail', params: { eventId: notification.related_object_id } });
      }
      this.markNotificationAsRead(notification.id);
      this.showDropdown = false;
    },
    goToSettings() {
      this.showDropdown = false;
      this.$router.push('/settings');
    },
    goToDashboard() {
      this.showDropdown = false;
      this.$router.push('/management');
    },
    viewProfile() {
      this.showDropdown = false;
      this.$router.push('/dashboard');
    },
    handleAuthAction() {
      this.$emit('toggle-login');
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
      // localStorage.setItem('darkMode', String(this.isDarkMode));
      // ────────────────────────────────────────────────────────────────
    },
    handleClickOutside(event) {
      const avatar = this.$refs.avatarRef;
      const dropdown = this.$refs.dropdownRef;
      if (
        this.showDropdown &&
        avatar && !avatar.contains(event.target) &&
        dropdown && !dropdown.contains(event.target)
      ) {
        this.showDropdown = false;
        this.showNotificationsList = false;
        this.showRequestsList = false;
      }
    },
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
  },
};
</script>

<style scoped>
/* ── Wrapper ── */
.nav-wrap {
  position: sticky;
  top: 0;
  z-index: 40;
  background: rgba(8, 12, 18, 0.9);
  backdrop-filter: blur(24px);
  border-bottom: 1px solid var(--hmn-border);
}
.nav-wrap::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(0, 184, 208, 0.2) 40%,
    rgba(0, 184, 208, 0.2) 60%,
    transparent 100%
  );
}

.hmn-container {
  width: min(calc(100% - 2.5rem), 1120px);
  margin: 0 auto;
}

nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  gap: 20px;
}

/* ── Brand ── */
.brand {
  display: flex;
  align-items: center;
  gap: 13px;
  text-decoration: none;
  flex-shrink: 0;
}
.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 9px;
  flex-shrink: 0;
  position: relative;
  background: linear-gradient(145deg, var(--hmn-red), #7a0e1e);
  box-shadow: 0 0 16px rgba(200, 16, 46, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}
.brand-mark::before {
  content: '';
  position: absolute;
  inset: 1px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12), transparent 55%);
}
.bmi {
  display: flex;
  flex-direction: column;
  gap: 3px;
  align-items: center;
  position: relative;
  z-index: 1;
}
.bmi span {
  display: block;
  background: white;
  height: 2px;
  border-radius: 1px;
}
.bmi span:nth-child(1) { width: 14px; }
.bmi span:nth-child(2) { width: 8px; align-self: flex-start; margin-left: 3px; }
.bmi span:nth-child(3) { width: 14px; }

.brand-name {
  color: var(--hmn-bright);
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  line-height: 1;
}
.brand-sub {
  color: #1e3448;
  font-size: 9px;
  letter-spacing: 0.12em;
  margin-top: 2px;
  font-family: 'DM Sans', sans-serif;
}

/* ── Nav links ── */
.nav-links {
  display: flex;
  gap: 2px;
}
.nl {
  color: var(--hmn-muted);
  font-size: 13px;
  text-decoration: none;
  padding: 7px 12px;
  border-radius: 6px;
  transition: all 0.18s;
  cursor: pointer;
  font-family: 'Barlow', sans-serif;
  font-weight: 500;
  user-select: none;
}
.nl:hover {
  color: var(--hmn-text);
  background: rgba(255, 255, 255, 0.05);
}
.nl.active {
  color: var(--hmn-cyan);
}
/* Forum is always dead */
.nl.dead {
  color: #182430;
  text-decoration: line-through;
  pointer-events: none;
  cursor: default;
}

/* ── Right buttons ── */
.nav-btns {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
.btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 20px;
  border-radius: var(--hmn-radius-md);
  font-size: 13px;
  font-weight: 600;
  font-family: 'Barlow', sans-serif;
  cursor: pointer;
  border: none;
  transition: all 0.18s;
  letter-spacing: 0.02em;
}
.btn:hover { transform: translateY(-1px); }
.btn-red {
  background: linear-gradient(145deg, var(--hmn-red), #8a0e1e);
  color: white;
  box-shadow: 0 4px 16px rgba(200, 16, 46, 0.28);
}
.btn-red:hover { box-shadow: 0 6px 24px rgba(200, 16, 46, 0.42); }
.btn-ghost {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--hmn-border2);
  color: var(--hmn-text);
}
.btn-ghost:hover { background: rgba(255, 255, 255, 0.08); }

/* ── Auth area + avatar ── */
.auth-area {
  position: relative;
}
.avatar-wrap {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--hmn-surface2);
  border: 1px solid var(--hmn-border2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: border-color 0.18s;
}
.avatar-wrap:hover { border-color: var(--hmn-cyan); }
.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}
.avatar-icon {
  color: var(--hmn-muted);
  font-size: 14px;
}
.notif-dot {
  position: absolute;
  top: 0;
  right: 0;
  width: 8px;
  height: 8px;
  background: var(--hmn-red2);
  border-radius: 50%;
  border: 2px solid var(--hmn-bg);
  box-shadow: 0 0 6px var(--hmn-red2);
}

/* ── Dropdown transition (content styles in HmnNavDropdown) ── */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}
.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
