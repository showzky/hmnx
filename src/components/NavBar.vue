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
          <div class="navbar-icons">
            <div class="avatar" ref="avatar" @click="toggleDropdown">
              <img v-if="auth.user && auth.user.avatar" :src="auth.user.avatar" alt="User Avatar" />
              <i v-else class="fa-solid fa-user"></i>
            </div>
            <span v-if="hasUnreadNotifications" class="notification-dot-navbar"></span>
          </div>

          <transition name="slide-fade">
            <div v-if="showDropdown" class="dropdown-menu" ref="dropdownMenu" @click.stop>

              <!-- Toggle Notifications -->
              <div class="dropdown-item" @click="toggleNotificationsList">
                <i class="fas fa-bell mr-2"></i>Notifications
                <span v-if="unreadNotificationCount > 0" class="notification-count-badge">
                  {{ unreadNotificationCount }}
                </span>
              </div>

              <!-- Toggle Friend Requests -->
              <div class="dropdown-item" @click="toggleRequestsList">
                <i class="fas fa-user-friends mr-2"></i>Friend Requests
                <span v-if="pendingRequests.length > 0" class="notification-count-badge">
                  {{ pendingRequests.length }}
                </span>
              </div>

              <!-- Notification List -->
              <transition name="slide-fade">
                <div v-if="showNotificationsList" class="notifications-section">
                  <div v-if="notifications.length" class="px-4 py-2">
                    <h6 class="text-sm font-medium text-gray-500 mb-2">Updates</h6>
                    <div v-for="notification in notifications" :key="notification.id" class="dropdown-notification-item py-2">
                      <button class="notification-link w-full text-left" @click="handleNotificationClick(notification)">
                        {{ notification.message }}
                      </button>
                    </div>
                    <button class="dropdown-item view-all-btn mt-2" @click.stop="markAllAsRead">Mark All as Read</button>
                  </div>
                  <div v-else class="px-4 py-6 text-center text-gray-400">
                    No new notifications
                  </div>
                </div>
              </transition>

              <!-- Friend Requests List -->
              <transition name="slide-fade">
                <div v-if="showRequestsList" class="notifications-section">
                  <div v-if="pendingRequests.length" class="px-4 py-2">
                    <h6 class="text-sm font-medium text-gray-500 mb-2">Friend Requests</h6>
                    <div v-for="req in pendingRequests" :key="req.id" class="flex justify-between items-center py-2">
                      <span>{{ req.sender.username || req.sender.email }}</span>
                      <div class="flex gap-2">
                        <button @click="acceptRequest(req.id)" class="text-xs bg-green-500 hover:bg-green-600 text-white py-1 px-3 rounded">Accept</button>
                        <button @click="declineRequest(req.id)" class="text-xs bg-red-500 hover:bg-red-600 text-white py-1 px-3 rounded">Decline</button>
                      </div>
                    </div>
                  </div>
                  <div v-else class="px-4 py-6 text-center text-gray-400">
                    No friend requests
                  </div>
                </div>
              </transition>

              <!-- Profile & Settings -->
              <button class="dropdown-item" @click="viewProfile">Vis Profil</button>
              <button class="dropdown-item" @click="goToSettings">
                <i class="fas fa-cog mr-2"></i>Settings
              </button>

              <!-- Dark Mode -->
              <button class="dropdown-item dark-mode-toggle" @click="toggleDarkMode">
                <i :class="isDarkMode ? 'fas fa-sun' : 'fas fa-moon'" class="toggle-icon mr-2"></i>
                <span>{{ isDarkMode ? 'Light Mode' : 'Dark Mode' }}</span>
              </button>

              <!-- Logout -->
              <button class="dropdown-item" @click="logoutUser">Utlogging</button>
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
      notifications: [],
      pendingRequests: [],
      showRequestsList: false,
      isDarkMode: localStorage.getItem('darkMode') === 'true'
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
    toggleRequestsList() {
  this.showRequestsList = !this.showRequestsList;
  this.showNotificationsList = false;

  if (this.showRequestsList) {
    this.fetchRequests();
  }
},
    toggleNotificationsList() {
      this.showNotificationsList = !this.showNotificationsList;
    },
    async acceptRequest(id) {
  await acceptFriendRequest(id);
  this.pendingRequests = this.pendingRequests.filter(r => r.id !== id);

  // ✅ refresh friend list if the FriendsList component is available
  this.$refs.friendsList?.loadFriends();
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
      console.log('Notification clicked:', notification);
      if (notification.related_object_id) {
        this.$router.push({ 
          name: 'EventDetail', 
          params: { eventId: notification.related_object_id } 
        });
      } else {
        console.log('No related event id found in notification.');
      }
      this.markNotificationAsRead(notification.id);
    },
    goToForum() {
      window.location.href = "https://forum.hmnmentalpasienter.no";
    },
    goToSettings() {
      this.showDropdown = false;
      this.$router.push('/settings');
    },
    viewProfile() {
      this.showDropdown = false;
      this.$router.push('/dashboard');
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
      this.isDarkMode = !this.isDarkMode;
      document.documentElement.classList.toggle('dark-mode', this.isDarkMode);
      localStorage.setItem('darkMode', this.isDarkMode);
    },
    handleClickOutside(event) {
      if (this.showDropdown && !this.$refs.avatar.contains(event.target) && !this.$refs.dropdownMenu.contains(event.target)) {
        this.showDropdown = false;
        this.showNotificationsList = false;
      }
    }
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside);
    document.documentElement.classList.toggle('dark-mode', this.isDarkMode);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  }
};
</script>

<style scoped>
/* Add this new style */
.logo-link {
  text-decoration: none;
  color: inherit;
}

/* Navbar main styling */
.navbar {
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

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
  list-style: none;
}

.nav-links a {
  text-decoration: none;
  color: #34495e;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-links a:hover {
  color: #3498db;
}

/* Add styles for the Forum button to match other nav links */
.nav-links button.nav-link {
  text-decoration: none;
  color: #34495e;
  font-weight: 500;
  transition: color 0.3s ease;
  font-size: inherit;
  font-family: inherit;
  padding: 0;
  background: none;
  border: none;
  cursor: pointer;
}

.nav-links button.nav-link:hover {
  color: #3498db;
}

/* Dark mode styles for the Forum button */
.dark-mode .nav-links button.nav-link {
  color: var(--text);
}

.dark-mode .nav-links button.nav-link:hover {
  color: #3498db;
}

.login-btn {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.25rem;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.login-btn:hover {
  background-color: #2980b9;
}

/* Authentication dropdown styling */
.auth-dropdown {
  position: relative;
}

/* Make the clickable notification link look modern */
.notification-link {
  background: none;      /* Remove default background */
  border: none;          /* Remove default border */
  padding: 0.5rem 0;      /* Add some vertical padding */
  font-size: 0.9rem;      /* Adjust font size */
  color: #333;           /* Base text color */
  text-align: left;      /* Align text to left */
  cursor: pointer;       /* Show pointer cursor */
  width: 100%;           /* Make it take the full container width */
  transition: color 0.3s ease, transform 0.3s ease;
}

/* Hover effect for the notification link */
.notification-link:hover {
  color: #3498db;        /* Change color on hover */
  transform: translateX(5px);  /* Slight move on hover */
  text-decoration: underline;
}


/* Navbar icons container (avatar and notification dot) */
.navbar-icons {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
}

/* Avatar styling */
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #3498db;
  color: white;
  font-size: 1.2rem;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Notification dot styling */
.notification-dot-navbar {
  display: block;
  position: absolute;
  top: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  background-color: red;
  border-radius: 50%;
  border: 2px solid white;
}

/* Dropdown menu styling */
.dropdown-menu {
  position: absolute;
  right: 0;
  top: 55px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid #add8e6;
  border-radius: 12px;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.05), 0 10px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  min-width: 200px;
  overflow: hidden;
  transform-origin: top right;
  animation: dropdownEntrance 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes dropdownEntrance {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Slide-fade transition for dropdown and notifications */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

/* Notification count badge styling */
.notification-count-badge {
  margin-left: 8px;
  color: red;
  font-weight: bold;
}

/* Notifications sub-list container styling */
.notifications-section {
  padding: 0 1.5rem 1rem 1.5rem;
  max-height: 300px;
  overflow-y: auto;
  border-bottom: 1px solid #e0e0e0;
}

/* Notification items styling */
.dropdown-notification-item {
  padding: 0.7rem 0;
  font-size: 0.9rem;
  color: #333;
  border-bottom: 1px dashed #eee;
  word-wrap: break-word;
}
.dropdown-notification-item:last-child {
  border-bottom: none;
}

/* Dropdown item styling */
.dropdown-item {
  padding: 1rem 1.5rem;
  background: transparent;
  border: none;
  color: #333;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.3s ease;
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
}

.dropdown-item::before {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #add8e6, #87ceeb);
  transition: width 0.3s ease;
}

.dropdown-item:hover {
  background: #f0f0f0;
  transform: translateX(8px);
}

.dropdown-item:hover::before {
  width: 100%;
}


  .dark-mode {
    --primary: #7b2cbf;
    --secondary: #3a86ff;
    --accent: #ff006e;
    --background: #0f0e17;
    --text: #fffffe;
    --card-bg: #16151d;
    background-color: var(--background);
    color: var(--text);
  }
  

/* ===================== START Dark Mode Toggle Styling ===================== */
.dark-mode-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: transparent;
  border: none;
  font-size: 0.95rem;
  color: #000000;
  cursor: pointer;
  padding: 0.75rem 1.5rem;
  transition: background 0.3s ease, color 0.3s ease;
}

.dark-mode-toggle:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--accent);
}

.dark-mode-toggle .toggle-icon {
  /* Optional: add a smooth transition for icon change */
  transition: transform 0.3s ease;
}

/* Optionally, if you want the icon to bounce on toggle: */
.dark-mode-toggle:active .toggle-icon {
  transform: scale(0.9);
}
/* ===================== END Dark Mode Toggle Styling ===================== */

/* Existing dark mode overrides for navbar */
.dark-mode .navbar {
  background-color: var(--card-bg);
}

.dark-mode .nav-links a {
  color: var(--text);
}

/* Dark mode styles for dropdown menu */
.dark-mode .dropdown-menu {
  background: rgba(30, 30, 30, 0.95);
  border-color: #444;
}

.dark-mode .dropdown-item {
  color: var(--text);
}

.dark-mode .dropdown-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.dark-mode .notification-link {
  color: var(--text);
}

.dark-mode .notification-link:hover {
  color: #3498db;
}

.dark-mode .text-gray-500 {
  color: #a0a0a0;
}

.dark-mode .text-gray-400 {
  color: #666;
}

/* Pseudo-element icons for dropdown items */
.dropdown-item:first-child::after {
  content: '👤';
  margin-left: auto;
}

.dropdown-item:nth-child(2)::after {
  content: '🔑';
  margin-left: auto;
}

.dropdown-item:last-child::after {
  content: '🚪';
  margin-left: auto;
}

/* Dark mode styles */
.dark-mode .logo {
    color: #ffffff;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}
</style>
