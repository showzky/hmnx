<template>
  <div>
    <div v-if="!isLoading" class="admin-body-container">
      <!-- Sidebar Navigation -->
      <aside class="admin-sidebar">
        <nav>
          <ul>
            <li>
              <a href="#"
                 :class="{ active: activeTab === 'dashboard' }"
                 @click.prevent="setActive('dashboard')">
                Dashboard
              </a>
            </li>
            <li>
              <a href="#"
                 :class="{ active: activeTab === 'content' }"
                 @click.prevent="setActive('content')">
                Content
              </a>
            </li>
            <li>
              <a href="#"
                 :class="{ active: activeTab === 'system' }"
                 @click.prevent="setActive('system')">
                System
              </a>
            </li>
            <li>
              <a href="#"
                 :class="{ active: activeTab === 'users' }"
                 @click.prevent="setActive('users')">
                Users
              </a>
            </li>
            <li>
              <a href="#"
                 :class="{ active: activeTab === 'team' }"
                 @click.prevent="setActive('team')">
                Team Manager
              </a>
            </li>
            <li>
              <a href="#"
                 :class="{ active: activeTab === 'music' }"
                 @click.prevent="setActive('music')">
                Music
              </a>
            </li>
            <li>
              <a href="#"
                 :class="{ active: activeTab === 'settings' }"
                 @click.prevent="setActive('settings')">
                Settings
              </a>
            </li>
          </ul>
        </nav>
      </aside>

      <!-- Main Content -->
      <main class="admin-content">
        <div class="admin-content-header">
          <h2>Management Dashboard</h2>
          <div class="profile-info">
            <div class="user-meta">
              <h1 class="username">Welcome, {{ displayName }}</h1>
            </div>
          </div>
        </div>

        <div class="content-area">
          <!-- CONTENT TAB (Events) -->
          <section v-if="activeTab === 'content'">
            <!-- Existing Events List -->
            <div class="event-list-card">
              <div class="existing-events-header">
                <h3>Existing Events</h3>
                <input
                  type="text"
                  v-model="searchQuery"
                  placeholder="Search Events..."
                  class="search-input"
                />
              </div>
              <div class="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Event Name</th>
                      <th>Date</th>
                      <th>Time</th>
                      <th style="width: 100px;">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="event in filteredEvents" :key="event.id">
                      <td>{{ event.event_name }}</td>
                      <td>{{ formatDate(event.event_date) }}</td>
                      <td>{{ formatTime(event.event_time) }}</td>
                      <td>
                        <button @click="deleteEvent(event.id)" class="delete-button">
                          Delete
                        </button>
                      </td>
                    </tr>
                    <tr v-if="filteredEvents.length === 0">
                      <td colspan="4" class="no-events">No events found</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Create Event Form -->
            <div class="create-event-card">
              <h3>Create New Event</h3>
              <div class="form-grid">
                <div class="form-group">
                  <label for="event-name">Name</label>
                  <input type="text" id="event-name" v-model="newEvent.event_name" placeholder="Event Title" />
                </div>
                <div class="form-group">
                  <label for="event-date">Date</label>
                  <input type="date" id="event-date" v-model="newEvent.event_date" />
                </div>
                <div class="form-group">
                  <label for="event-time">Time</label>
                  <input type="time" id="event-time" v-model="newEvent.event_time" />
                </div>
                <div class="form-group">
                  <label for="template_name">Template</label>
                  <select id="template_name" v-model="newEvent.template_name" required>
                    <option value="" disabled>Select a Template</option>
                    <option value="template1">Template 1 (Image-Focused)</option>
                    <option value="template2">Template 2 (Text-Focused)</option>
                  </select>
                </div>
              </div>
              <div class="form-group full-width">
                <label for="event-description">Description (Optional)</label>
                <textarea id="event-description" v-model="newEvent.event_description" 
                          placeholder="Short event details..."></textarea>
              </div>
              <div class="form-group full-width file-upload-group">
                <label for="event_image" class="file-upload-label">
                  <span>Choose an Image</span>
                  <input type="file" id="event_image" @change="handleImageUpload" accept="image/*" class="hidden-file-input" />
                </label>
              </div>
              <div class="checkbox-group">
                <label class="custom-checkbox">
                  <input type="checkbox" v-model="newEvent.notify_users" />
                  Notify all users
                </label>
              </div>
              <button @click="createEvent" class="create-event-button">Create</button>
              <div v-if="createEventMessage" class="form-message"
                   :class="{ success: createEventSuccess, error: !createEventSuccess }">
                {{ createEventMessage }}
              </div>
            </div>
          </section>

          <!-- Users Tab Section -->
          <section v-if="activeTab === 'users'">
            <!-- Update User Role Widget -->
            <div class="data-widget">
              <h3>Update User Role</h3>
              <form @submit.prevent="updateUserRole">
                <div class="form-group">
                  <label for="user-select">Select User</label>
                  <select id="user-select" v-model="userRoleUpdate.selectedUser">
                    <option value="" disabled>Select a user</option>
                    <option v-for="user in usersList" :key="user.id" :value="user.id">
                      {{ user.username ? user.username + ', ' + user.email : user.email }}
                    </option>
                  </select>
                </div>
                <div class="form-group">
                  <label for="role-select">Select Role/Rank</label>
                  <select id="role-select" v-model="userRoleUpdate.newRole">
                    <option value="" disabled>Select a role</option>
                    <option v-for="role in availableRoles" :key="role.id" :value="role.id">
                      {{ role.name }}
                    </option>
                  </select>
                </div>
                <button type="submit" class="update-role-button">Update Role</button>
              </form>
              <div v-if="updateUserMessage" class="form-message"
                   :class="{ success: updateUserSuccess, error: !updateUserSuccess }">
                {{ updateUserMessage }}
              </div>
              <div v-if="selectedUserRoles && selectedUserRoles.length > 0" class="current-roles-container">
                <h4>Current Roles:</h4>
                <span v-for="role in selectedUserRoles" 
                      :key="role.id" 
                      class="role-badge" 
                      :class="role.name.toLowerCase()" 
                      :style="{ backgroundColor: role.badge_color }">
                  <i v-if="role.badge_icon" :class="role.badge_icon"></i>
                  {{ role.name }}
                </span>
              </div>
              <div v-else-if="userRoleUpdate.selectedUser">
                <p>No roles assigned to this user yet.</p>
              </div>
            </div>

            <!-- Demote (Remove) Roles Widget -->
            <div class="data-widget">
              <h3>Demote (Remove) User Roles</h3>
              <form @submit.prevent="removeSelectedRoles">
                <div class="form-group">
                  <label for="user-select-remove">Select User</label>
                  <select
                    id="user-select-remove"
                    v-model="userRoleRemove.selectedUser"
                    @change="fetchUserRolesToRemove"
                  >
                    <option value="" disabled>Select a user</option>
                    <option v-for="user in usersList" :key="user.id" :value="user.id">
                      {{ user.username ? user.username + ', ' + user.email : user.email }}
                    </option>
                  </select>
                </div>
                <div v-if="selectedUserRolesToRemove && selectedUserRolesToRemove.length > 0">
                  <label>Current Roles:</label>
                  <div class="checkbox-group-vertical">
                    <label
                      v-for="role in selectedUserRolesToRemove"
                      :key="role.id"
                      class="custom-checkbox"
                    >
                      <input
                        type="checkbox"
                        :value="role.id"
                        v-model="rolesToRemove"
                      />
                      {{ role.name }}
                    </label>
                  </div>
                </div>
                <div v-else-if="userRoleRemove.selectedUser">
                  <p>No roles assigned to this user or none found.</p>
                </div>
                <button type="submit" class="update-role-button">Remove Selected Roles</button>
              </form>
              <div v-if="removeRoleMessage" class="form-message"
                   :class="{ success: removeRoleSuccess, error: !removeRoleSuccess }">
                {{ removeRoleMessage }}
              </div>
            </div>
          </section>

          <!-- Latest Activity / Upcoming Events Widgets -->
          <div v-for="widget in widgets" :key="widget.id" class="data-widget">
            <div v-if="widget.id === 'latest-activity'">
              <div v-if="activeTab === 'users'">
                <h3>Create New Role</h3>
                <form @submit.prevent="createRole">
                  <div class="form-group">
                    <label for="new-role-name">Role Name</label>
                    <input type="text" id="new-role-name" v-model="newRole.name" placeholder="Enter role name" />
                  </div>
                  <div class="form-group">
                    <label for="new-role-icon">Badge Icon</label>
                    <input type="text" id="new-role-icon" v-model="newRole.badge_icon" placeholder="Enter badge icon (e.g., 👑)" />
                  </div>
                  <div class="form-group">
                    <label for="new-role-color">Badge Color</label>
                    <input type="text" id="new-role-color" v-model="newRole.badge_color" placeholder="Enter badge color (e.g., #ff0000)" />
                  </div>
                  <button type="submit" class="create-role-button">Create Role</button>
                </form>
                <div v-if="createRoleMessage" class="form-message"
                     :class="{ success: createRoleSuccess, error: !createRoleSuccess }">
                     {{ createRoleMessage }}
                    </div>
                <div class="role-list">
                  <h4>Existing Roles</h4>
                  <ul>
                    <li v-for="role in availableRoles" :key="role.id">
                      <span>{{ role.name }}</span>
                      <button @click="deleteRole(role.id)" class="delete-role-button">
                        Delete
                      </button>
                    </li>
                  </ul>
                </div>
              </div>
              <div v-else>
                <h3>{{ widget.title }}</h3>
                <p>{{ widget.description }}</p>
                <ul>
                  <li v-for="(item, index) in widget.activityItems" :key="index">
                    {{ item.text }}
                  </li>
                </ul>
              </div>
            </div>

            <div v-if="widget.id === 'upcoming-events'">
              <h3>{{ widget.title }}</h3>
              <p>{{ widget.description }}</p>
              <ul>
                <li v-for="event in upcomingEventsData" :key="event.id">
                  <router-link :to="`/events/${event.id}`" class="event-link">
                    {{ event.event_name }} - {{ formatDate(event.event_date) }}, {{ formatTime(event.event_time) }}
                  </router-link>
                </li>
                <li v-if="upcomingEventsData.length === 0">
                  <p>No upcoming events scheduled yet.</p>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Team Manager Tab Section -->
        <section v-if="activeTab === 'team'" class="team-manager">
          <div class="data-widget">
            <h3>Manage Team Members</h3>
            <div class="team-members-list">
              <div v-for="member in teamMembers" :key="member.id" class="team-member-card">
                <div class="member-avatar">
                  <img :src="member.avatar || defaultAvatar" :alt="member.name" />
                  <button class="change-avatar-btn" @click="triggerAvatarUpload(member.id)">
                    <i class="fas fa-camera"></i>
                  </button>
                </div>
                <div class="member-info">
                  <input type="text" v-model="member.name" placeholder="Name" />
                  <input type="text" v-model="member.title" placeholder="Title" />
                  <textarea v-model="member.bio" placeholder="Bio"></textarea>
                </div>
                <div class="member-actions">
                  <button class="save-btn" @click="saveTeamMember(member)">Save</button>
                  <button class="delete-btn" @click="deleteTeamMember(member.id)">Delete</button>
                </div>
              </div>
            </div>
            <button class="add-member-btn" @click="addNewTeamMember">
              <i class="fas fa-plus"></i> Add Team Member
            </button>
            <div v-if="teamMessage" class="form-message" :class="{ success: teamSuccess, error: !teamSuccess }">
              {{ teamMessage }}
            </div>
          </div>
        </section>

        <!-- Music Admin Section -->
        <section v-if="activeTab === 'music'" class="music-admin">
          <div class="data-widget">
            <h3>Manage Bangerfabrikken Playlist</h3>
            <table class="playlist-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Artist</th>
                  <th>SoundCloud URL</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(song, index) in playlist" :key="index">
                  <td>{{ song.title }}</td>
                  <td>{{ song.artist }}</td>
                  <td>{{ song.soundcloudUrl }}</td>
                  <td>
                    <button class="delete-song" @click="deleteSong(index)">Delete</button>
                    <button class="edit-song" @click="editSong(index)">Edit</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div class="form-group-music">
              <label>Title</label>
              <input v-model="newSong.title" />
            </div>
            <div class="form-group-music">
              <label>Artist</label>
              <input v-model="newSong.artist" />
            </div>
            <div class="form-group-music">
              <label>Cover URL</label>
              <input v-model="newSong.cover" />
            </div>
            <div class="form-group-music">
              <label>SoundCloud URL</label>
              <input v-model="newSong.soundcloudUrl" />
            </div>
            <button @click="saveSong" class="create-role-button">
              {{ editingIndex !== null ? 'Update Song' : 'Add Song' }}
            </button>
            <div v-if="playlistMessage" class="form-message" :class="{ success: playlistSuccess, error: !playlistSuccess }">
              {{ playlistMessage }}
            </div>
          </div>
        </section>

        <!-- Maintenance Controls -->
        <div class="data-widget" v-if="activeTab === 'settings'">
          <h3>Maintenance Settings</h3>
          <div class="maintenance-controls">
            <div class="checkbox-group">
              <label class="custom-checkbox">
                <input type="checkbox" v-model="maintenanceMode" @change="onToggleMaintenance" />
                Enable Maintenance Mode
              </label>
            </div>
            <div class="checkbox-group">
              <label class="custom-checkbox">
                <input type="checkbox" v-model="noticeMaintenanceMode" @change="onToggleNoticeMaintenance" />
                Enable Notice Maintenance Mode
              </label>
            </div>
            <div class="message-input-container" v-if="noticeMaintenanceMode">
              <input 
                type="text" 
                v-model="maintenanceBannerMessage" 
                placeholder="Enter maintenance message..."
              />
              <button 
                class="update-message-button" 
                @click="onToggleNoticeMaintenance"
                :disabled="!maintenanceBannerMessage.trim()"
              >
                Update Message
              </button>
            </div>
            <div v-if="maintenanceMessage" class="form-message" :class="{ success: maintenanceSuccess, error: !maintenanceSuccess }">
              {{ maintenanceMessage }}
            </div>
            <div v-if="noticeMaintenanceMessage" class="form-message" :class="{ success: noticeMaintenanceSuccess, error: !noticeMaintenanceSuccess }">
              {{ noticeMaintenanceMessage }}
            </div>
          </div>
        </div>
      </main>
    </div>
    <div v-else>Loading Management Panel...</div>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/authStore';
import axios from '@/axios'; // Ensure this has baseURL + withCredentials set
import { useWebSocket } from '@/composables/useWebSocket';
import { ref } from 'vue';

export default {
  name: 'Management',
  data() {
    return {
      activeTab: 'dashboard',
      isLoading: true,
      searchQuery: '',

      // Team Manager
      teamMembers: [],
      teamMessage: '',
      teamSuccess: false,
      defaultAvatar: 'https://picsum.photos/200/200',

      // Maintenance Mode
      maintenanceMode: false,
      maintenanceMessage: '',
      maintenanceSuccess: false,

      // Notice Maintenance Mode
      noticeMaintenanceMode: false,
      noticeMaintenanceMessage: '',
      noticeMaintenanceSuccess: false,
      maintenanceBannerMessage: '',

      // Widgets
      widgets: [
        {
          id: 'latest-activity',
          title: 'Latest Activity',
          description: 'Recent updates and happenings on the site.',
          activityItems: [],
        },
        {
          id: 'upcoming-events',
          title: 'Upcoming Events',
          description: 'Never miss out on friend gatherings.',
          eventItems: [],
        }
      ],

      // Users & Roles
      userRoleUpdate: { selectedUser: '', newRole: '' },
      userRoleRemove: { selectedUser: '' },
      usersList: [],
      availableRoles: [],
      updateUserMessage: '',
      updateUserSuccess: false,
      selectedUserRoles: [],
      selectedUserRolesToRemove: [],
      rolesToRemove: [],
      removeRoleMessage: '',
      removeRoleSuccess: false,
      newRole: { name: '', badge_icon: '', badge_color: '' },
      createRoleMessage: '',
      createRoleSuccess: false,

      // Events
      upcomingEventsData: [],
      newEvent: {
        event_name: '',
        event_date: '',
        event_time: '',
        event_description: '',
        template_name: '',
        event_image: null,
        notify_users: false,
      },
      createEventMessage: '',
      createEventSuccess: false,

      // Music
      playlist: [],
      newSong: { title: '', artist: '', cover: '', soundcloudUrl: '' },
      playlistMessage: '',
      playlistSuccess: false,
      editingIndex: null,
      isLoadingSongs: true
    };
  },

  computed: {
    auth() {
      return useAuthStore();
    },
    displayName() {
      return this.auth.user?.username || 'Admin User';
    },
    filteredEvents() {
      if (!Array.isArray(this.upcomingEventsData)) return [];
      const query = this.searchQuery.toLowerCase();
      return this.upcomingEventsData.filter(event =>
        event.event_name.toLowerCase().includes(query)
      );
    },
    userRoles() {
      try {
        const user = JSON.parse(localStorage.getItem('user'));
        return user?.roles?.map(role => role.name.toLowerCase()) || [];
      } catch {
        return [];
      }
    },
    canManageSongs() {
      return ['developer', 'admin', 'producer'].some(role => this.userRoles.includes(role));
    },
    currentSong() {
      if (!this.playlist.length) return undefined;
      return this.playlist[this.editingIndex ?? 0];
    }
  },

  methods: {
    setActive(tab) {
      this.activeTab = tab;
    },

    // ---------------- MAINTENANCE ----------------
    fetchMaintenanceStatus() {
      axios.get('/maintenance-status')
        .then(res => {
          this.maintenanceMode = res.data.maintenance_mode === 'on';
          this.noticeMaintenanceMode = res.data.notice_maintenance_mode === 'on';
        })
        .catch(err => console.error('Failed to fetch maintenance status:', err));
    },
    onToggleMaintenance() {
      axios.post('/maintenance', {
        mode: this.maintenanceMode ? 'on' : 'off'
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      })
      .then(() => {
        this.maintenanceMessage = 'Maintenance mode updated.';
        this.maintenanceSuccess = true;
      })
      .catch(error => {
        console.error('Error toggling maintenance mode:', error);
        this.maintenanceMessage = 'Failed to update maintenance mode.';
        this.maintenanceSuccess = false;
      })
      .finally(() => {
        setTimeout(() => {
          this.maintenanceMessage = '';
        }, 3000);
      });
    },

    onToggleNoticeMaintenance() {
      const message = this.maintenanceBannerMessage.trim();
      console.log('Sending maintenance update:', {
        mode: this.noticeMaintenanceMode ? 'on' : 'off',
        message: message
      });
      
      axios.post('/notice-maintenance', {
        mode: this.noticeMaintenanceMode ? 'on' : 'off',
        message: message
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      })
      .then(res => {
        console.log('Maintenance update response:', res.data);
        this.noticeMaintenanceMessage = 'Notice maintenance mode updated.';
        this.noticeMaintenanceSuccess = true;
      })
      .catch(error => {
        console.error('Error toggling notice maintenance mode:', error);
        this.noticeMaintenanceMessage = 'Failed to update notice maintenance mode. Please try again later.';
        this.noticeMaintenanceSuccess = false;
      })
      .finally(() => {
        setTimeout(() => {
          this.noticeMaintenanceMessage = '';
        }, 3000);
      });
    },

    // ---------------- USERS ----------------
    fetchUsersList() {
      axios.get('/users')
        .then(res => this.usersList = res.data.users)
        .catch(err => console.error('Error fetching users:', err));
    },
    fetchRoles() {
      axios.get('/roles')
        .then(res => this.availableRoles = res.data.roles)
        .catch(err => console.error('Error fetching roles:', err));
    },
    updateUserRole() {
      axios.put('/update-user-roles', {
        user_id: this.userRoleUpdate.selectedUser,
        role_ids: [this.userRoleUpdate.newRole]
      })
      .then(res => {
        this.updateUserMessage = res.data.msg;
        this.updateUserSuccess = true;
      })
      .catch(err => {
        console.error('Error updating user role:', err);
        this.updateUserMessage = err.response?.data?.msg || 'Failed to update role';
        this.updateUserSuccess = false;
      })
      .finally(() => {
        setTimeout(() => this.updateUserMessage = '', 3000);
      });
    },
    removeSelectedRoles() {
      if (!this.userRoleRemove.selectedUser || !this.rolesToRemove.length) {
        this.removeRoleMessage = 'Select a user and at least one role to remove.';
        this.removeRoleSuccess = false;
        return;
      }

      const requests = this.rolesToRemove.map(roleId => {
        const role = this.selectedUserRolesToRemove.find(r => r.id === roleId);
        return axios.put('/demote-user', {
          user_id: this.userRoleRemove.selectedUser,
          role_to_remove: role?.name
        });
      });

      Promise.all(requests)
        .then(() => {
          this.removeRoleMessage = 'Roles removed.';
          this.removeRoleSuccess = true;
          this.fetchUserRolesToRemove();
          this.rolesToRemove = [];
        })
        .catch(err => {
          console.error('Error removing roles:', err);
          this.removeRoleMessage = 'Failed to remove one or more roles.';
          this.removeRoleSuccess = false;
        })
        .finally(() => {
          setTimeout(() => this.removeRoleMessage = '', 3000);
        });
    },
    fetchUserRolesToRemove() {
      axios.get('/users')
        .then(res => {
          const user = res.data.users.find(u => u.id === parseInt(this.userRoleRemove.selectedUser));
          this.selectedUserRolesToRemove = user?.roles || [];
        })
        .catch(err => console.error('Error loading user roles:', err));
    },
    createRole() {
      axios.post('/roles', this.newRole)
        .then(res => {
          this.createRoleMessage = res.data.msg;
          this.createRoleSuccess = true;
          this.newRole = { name: '', badge_icon: '', badge_color: '' };
          this.fetchRoles();
        })
        .catch(err => {
          this.createRoleMessage = err.response?.data?.msg || 'Error creating role.';
          this.createRoleSuccess = false;
        })
        .finally(() => {
          setTimeout(() => this.createRoleMessage = '', 3000);
        });
    },
    deleteRole(roleId) {
      if (!confirm('Delete this role?')) return;
      axios.delete(`/roles/${roleId}`)
        .then(() => this.fetchRoles())
        .catch(err => console.error('Error deleting role:', err));
    },

    // ---------------- EVENTS ----------------
    fetchUpcomingEvents() {
      axios.get('/events', {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      })
      .then(res => {
        this.upcomingEventsData = Array.isArray(res.data.events) ? res.data.events : [];
      })
      .catch(err => console.error('Error fetching events:', err));
    },
    createEvent() {
      const form = new FormData();
      Object.entries(this.newEvent).forEach(([key, value]) => {
        if (value !== null) form.append(key, value);
      });

      axios.post('/events', form, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      })
      .then(() => {
        this.createEventMessage = 'Event created!';
        this.createEventSuccess = true;
        this.fetchUpcomingEvents();
        this.newEvent = {
          event_name: '',
          event_date: '',
          event_time: '',
          event_description: '',
          template_name: '',
          event_image: null,
          notify_users: false,
        };
      })
      .catch(() => {
        this.createEventMessage = 'Error creating event.';
        this.createEventSuccess = false;
      })
      .finally(() => setTimeout(() => this.createEventMessage = '', 3000));
    },
    deleteEvent(id) {
      if (!confirm('Delete this event?')) return;
      axios.delete(`/events/${id}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      })
      .then(() => this.fetchUpcomingEvents())
      .catch(err => {
        console.error('Delete event failed:', err);
        alert('Error deleting event.');
      });
    },
    formatDate(d) {
      const date = new Date(d);
      return date.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
    },
    formatTime(t) {
      return t.split(':').slice(0, 2).join(':');
    },
    handleImageUpload(e) {
      this.newEvent.event_image = e.target.files[0];
    },

    // ---------------- MUSIC ----------------
    fetchPlaylist() {
      axios.get('/songs')
        .then(res => this.playlist = res.data.songs)
        .catch(err => console.error('Playlist fetch error:', err))
        .finally(() => this.isLoadingSongs = false);
    },
    saveSong() {
      const api = this.editingIndex !== null
        ? axios.put(`/playlist/${this.playlist[this.editingIndex].id}`, this.newSong)
        : axios.post('/playlist', this.newSong);

      api.then(() => {
        this.playlistMessage = this.editingIndex !== null ? 'Song updated!' : 'Song added!';
        this.playlistSuccess = true;
        this.resetForm();
        this.fetchPlaylist();
      })
      .catch(err => {
        console.error('Save song error:', err);
        this.playlistMessage = 'Error saving song.';
        this.playlistSuccess = false;
      })
      .finally(() => setTimeout(() => this.playlistMessage = '', 3000));
    },
    resetForm() {
      this.newSong = { title: '', artist: '', cover: '', soundcloudUrl: '' };
      this.editingIndex = null;
    },
    editSong(index) {
      this.newSong = { ...this.playlist[index] };
      this.editingIndex = index;
    },
    deleteSong(index) {
      const song = this.playlist[index];
      if (!confirm(`Delete "${song.title}"?`)) return;
      axios.delete(`/playlist/${song.id}`)
        .then(() => {
          this.playlistMessage = 'Song deleted!';
          this.playlistSuccess = true;
          this.fetchPlaylist();
        })
        .catch(err => {
          console.error('Delete song error:', err);
          this.playlistMessage = 'Failed to delete song.';
          this.playlistSuccess = false;
        })
        .finally(() => setTimeout(() => this.playlistMessage = '', 3000));
    },

    // Team Manager Methods
    fetchTeamMembers() {
      axios.get('/team-members')
        .then(res => this.teamMembers = res.data.team_members)
        .catch(err => console.error('Error fetching team members:', err));
    },
    saveTeamMember(member) {
  const isNew = !member.id;

  const hasImage = typeof member.avatar === 'object'; // File object

  const endpoint = isNew ? '/team-members' : `/team-members/${member.id}`;
  const method = isNew ? 'post' : 'put';

  let payload, headers;

  if (hasImage) {
    payload = new FormData();
    Object.entries(member).forEach(([key, value]) => {
      payload.append(key, value);
    });
    headers = {
      'Content-Type': 'multipart/form-data',
      Authorization: `Bearer ${localStorage.getItem('access_token')}`
    };
  } else {
    payload = member;
    headers = {
      Authorization: `Bearer ${localStorage.getItem('access_token')}`
    };
  }

  axios[method](endpoint, payload, { headers })
    .then(() => {
      this.teamMessage = isNew ? 'Team member added!' : 'Team member updated!';
      this.teamSuccess = true;
      this.fetchTeamMembers();
    })
    .catch(err => {
      console.error('❌ Error saving team member:', err);
      this.teamMessage = 'Failed to save team member.';
      this.teamSuccess = false;
    })
    .finally(() => {
      setTimeout(() => this.teamMessage = '', 3000);
    });
},

    addNewTeamMember() {
      this.teamMembers.push({
        id: null,
        name: '',
        title: '',
        bio: '',
        avatar: null
      });
    },
    triggerAvatarUpload(memberId) {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'image/*';
      input.onchange = (e) => this.handleAvatarUpload(e, memberId);
      input.click();
    },
    handleAvatarUpload(event, memberId) {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('avatar', file);
      formData.append('member_id', memberId);

      axios.post('/team-members/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      })
      .then(res => {
        const member = this.teamMembers.find(m => m.id === memberId);
        if (member) member.avatar = res.data.avatar_url;
        this.teamMessage = 'Avatar updated successfully!';
        this.teamSuccess = true;
      })
      .catch(err => {
        console.error('Error uploading avatar:', err);
        this.teamMessage = 'Failed to upload avatar.';
        this.teamSuccess = false;
      })
      .finally(() => {
        setTimeout(() => this.teamMessage = '', 3000);
      });
    },
  },

  mounted() {
    if (!localStorage.getItem('access_token')) {
      return this.$router.push('/login');
    }

    this.fetchMaintenanceStatus();
    this.fetchUsersList();
    this.fetchRoles();
    this.fetchUpcomingEvents();
    this.fetchPlaylist();
    this.fetchTeamMembers();

    if (this.auth.user?.id && this.socket) {
      this.socket.emit('setUserId', this.auth.user.id);
    }

    axios.get('/dashboard/latest-activity')
      .then(res => {
        const widget = this.widgets.find(w => w.id === 'latest-activity');
        if (widget) widget.activityItems = res.data.latest_activity;
      })
      .catch(err => console.error('Dashboard activity error:', err))
      .finally(() => this.isLoading = false);
  },

  setup() {
    const snackBar = ref(null);
    const { socket } = useWebSocket();
    return { snackBar, socket };
  }
};
</script>

<style scoped>
/* LAYOUT */
.admin-body-container {
  display: flex;
  width: 100%;
  height: 100vh;
  background-color: #e9ecef;
  overflow: hidden;
}

/* SIDEBAR */
.admin-sidebar {
  background-color: #2d3238;
  width: 200px;
  padding: 1rem 0;
  color: #ddd;
}
.admin-sidebar nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
.admin-sidebar nav li {
  margin: 0.2rem 0;
}
.admin-sidebar nav a {
  display: block;
  color: #ddd;
  text-decoration: none;
  padding: 0.7rem 1.5rem;
  transition: background-color 0.15s;
}
.admin-sidebar nav a:hover,
.admin-sidebar nav a.active {
  background-color: #dc3545;
  color: #fff;
  font-weight: 500;
}
/* --- File Upload Styling --- */
.file-upload-group {
  display: flex;
  flex-direction: column; /* Stack label and feedback message if needed */
  margin-top: 1rem;
}

.file-upload-label {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.8rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  letter-spacing: 0.025em;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  position: relative;
  overflow: hidden;
  border: none;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  max-width: 220px;
}

.file-upload-label:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  transform: translateY(-1px);
}

.file-upload-label:active {
  transform: translateY(1px);
  box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
}

.file-upload-label::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.1);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.file-upload-label:hover::before {
  opacity: 1;
}

.file-upload-label svg {
  width: 1.25rem;
  height: 1.25rem;
  fill: currentColor;
  transition: transform 0.2s ease;
}

.file-upload-label:active svg {
  transform: scale(0.95);
}

.file-upload-label:focus-visible {
  outline: 2px solid #6366f1;
  outline-offset: 2px;
}

/* Optional: Add an icon animation */
.file-upload-label:hover svg {
  animation: float 1.5s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

.hidden-file-input {
  position: absolute;
  opacity: 0;
  z-index: -1; /* Ensure it's behind other elements */
  width: 0;
  height: 0;
  overflow: hidden;
  /* Important: Keep it focusable for accessibility, but hide visually */
}

/* Optional: Style the area around the button (if needed) */
.form-group.file-upload-group label {
  margin-bottom: 0; /* Remove default label margin if needed */
}

/* MAIN CONTENT */
.admin-content {
  flex-grow: 1;
  padding: 1.5rem 2rem;
  overflow-y: auto;
}
.admin-content-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 1.5rem;
}
.admin-content-header h2 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
  color: #343a40;
}
.profile-info .username {
  font-size: 1rem;
  color: #6c757d;
  margin: 0;
}

/* GRID AREA */
.content-area {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

/* WIDGETS */
/* Updated styles for Data Widgets in the Users Tab */
.data-widget {
  background-color: #fff;
  border: none; /* Remove the solid border */
  border-radius: 0.5rem; /* Add rounded corners */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); /* Add a subtle box shadow */
  padding: 1.5rem; /* Increase padding for more spacing */
  margin-bottom: 1.5rem; /* Add margin between widgets */
}

.data-widget h3 {
  margin-top: 0;
  margin-bottom: 1.2rem;
  font-size: 1.25rem; /* Slightly larger title */
  font-weight: 500; /* Slightly lighter font weight for modern feel */
  color: #333; /* Darker text for better contrast */
  text-transform: none; /* Keep the title as is */
}

.data-widget .form-group {
  margin-bottom: 1.2rem; /* More spacing between form elements */
}

.data-widget label {
  font-size: 0.95rem;
  color: #555; /* Slightly lighter label color */
  margin-bottom: 0.4rem;
  display: block; /* Ensure labels are on their own line */
}

.data-widget select {
  border: 1px solid #ddd;
  border-radius: 0.3rem;
  padding: 0.7rem 1rem;
  font-size: 1rem;
  width: 100%; /* Make select boxes full width */
  appearance: none; /* Remove default arrow for custom styling */
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23666'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E"); /* Custom arrow */
  background-repeat: no-repeat;
  background-position: right 0.7rem center;
  background-size: 1rem;
}

.data-widget select:focus {
  outline: none;
  border-color: #007bff; /* Example focus color */
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25); /* Subtle focus shadow */
}

.data-widget button.update-role-button,
.data-widget button.create-role-button {
  background-color: #007bff; /* Modern primary color */
  color: #fff;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 0.3rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
}

.data-widget button.update-role-button:hover,
.data-widget button.create-role-button:hover {
  background-color: #0056b3;
}

.data-widget .current-roles-container {
  margin-top: 1.5rem;
  padding: 1rem;
  background-color: #f8f9fa; /* Light background for the roles */
  border-radius: 0.3rem;
  border: 1px solid #eee;
}

.data-widget .current-roles-container h4 {
  margin-top: 0;
  margin-bottom: 0.8rem;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.data-widget .role-badge {
  display: inline-block;
  padding: 0.5rem 0.8rem;
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
  border-radius: 0.3rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: #fff; /* Default text color for badges */
}

/* You can adjust the background colors for specific roles here */
.data-widget .role-badge.developer {
  background-color: #6c757d; /* Example grey color */
}

.data-widget .role-badge.admin {
  background-color: #dc3545; /* Example red color */
}

.data-widget .role-badge.producer {
  background-color: #28a745; /* Example green color */
}

.data-widget input[type="checkbox"] {
  margin-right: 0.5rem;
}

.data-widget label[for^="remove-role-"] {
  display: inline-block;
  margin-right: 1rem;
}

.data-widget button.delete-role-button {
  background-color: #f44336; /* Modern delete button color */
  color: #fff;
  border: none;
  padding: 0.3rem 0.8rem; /* Reduced padding for a smaller button */
  border-radius: 0.3rem;
  font-size: 0.8rem; /* Smaller font size */
  cursor: pointer;
  transition: background-color 0.2s ease-in-out;
  margin-left: 0.5rem;
  line-height: 1; /* Ensures text is centered properly */
  display: inline-flex; /* Better alignment for icons or text */
  align-items: center; /* Centers content vertically */
  justify-content: center; /* Centers content horizontally */
}

.data-widget button.delete-role-button:hover {
  background-color: #d32f2f; /* Darker shade on hover */
}

.data-widget .form-message {
  margin-top: 1rem;
  padding: 0.8rem 1.2rem;
  border-radius: 0.3rem;
  font-size: 0.9rem;
}
.data-widget .form-message.success {
  background-color: #e6ffe6;
  color: #155724;
  border: 1px solid #c3e6cb;
}
.data-widget .form-message.error {
  background-color: #ffe6e6;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* EVENT LIST CARD */
.event-list-card {
  background-color: #fff;
  border: 1px solid #dee2e6;
  border-radius: 0.3rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  padding: 1rem 1.2rem;
  grid-column: 1 / -1; /* Full-width in the grid */
}
.event-list-card h3 {
  margin: 0 0 0.8rem 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #343a40;
}
.event-list-card table {
  width: 100%;
  border-collapse: collapse;
}
.event-list-card th,
.event-list-card td {
  padding: 0.6rem;
  border-bottom: 1px solid #dee2e6;
  text-align: left;
  font-size: 0.95rem;
}
.event-list-card .no-events {
  text-align: center;
  color: #6c757d;
}
.delete-button {
  background-color: #dc3545;
  border: none;
  color: #fff;
  padding: 0.5rem 0.8rem;
  border-radius: 0.2rem;
  cursor: pointer;
  font-size: 0.85rem;
}
.delete-button:hover {
  background-color: #c82333;
}

/* CREATE EVENT CARD */
.create-event-card {
  background-color: #fff;
  border: 1px solid #dee2e6;
  border-radius: 0.3rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  padding: 1rem 1.2rem;
  grid-column: 1 / -1; /* Full-width in the grid */
}
.create-event-card h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.15rem;
  color: #343a40;
  font-weight: 600;
}
/* ===================== START Custom Checkbox Styling ===================== */
.custom-checkbox {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  position: relative;
  font-size: 0.95rem;
  user-select: none;
}

.custom-checkbox input[type="checkbox"] {
  appearance: none;
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border: 2px solid #007bff;
  border-radius: 4px;
  outline: none;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease-in-out;
  margin-right: 0.5rem;
}

.custom-checkbox input[type="checkbox"]:checked {
  background-color: #007bff;
  border-color: #007bff;
}

.custom-checkbox input[type="checkbox"]::after {
  content: '';
  position: absolute;
  display: none;
  left: 5px;
  top: 2px;
  width: 4px;
  height: 9px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.custom-checkbox input[type="checkbox"]:checked::after {
  display: block;
}
/* ===================== END Custom Checkbox Styling ===================== */

/* ========================= */
/* 1) Header with Title+Input */
/* ========================= */

.existing-events-header{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

/* ========================= */
/* 2) Search Bar Input       */
/* ========================= */

.search-input {
  border: 1px solid #ced4da;
  border-radius: 4px;
  padding: 0.4rem 0.6rem;
  font-size: 0.9rem;
  width: 200px;
}

/* ========================= */
/* 3) Scrollable Table       */
/* ========================= */

.table-container {
  max-height: 240px;
  overflow-y: auto;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
}
/* You can reuse your existing th/td styles here or add them if needed */
.table-container th,
.table-container td {
  padding: 0.6rem;
  border-bottom: 1px solid #dee2e6;
}

/* Make the table fill the container width */
.tabel-container table {
  width: 100%;
  border-collapse: collapse;
}

/* FORM GRID */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}
.form-group {
  display: flex;
  flex-direction: column;
}
.form-group.full-width {
  grid-column: 1 / -1;
}
.form-group label {
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.3rem;
  color: #495057;
}
.form-group input[type="text"],
.form-group input[type="date"],
.form-group input[type="time"],
.form-group select,
.form-group textarea {
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  padding: 0.5rem;
  font-size: 0.9rem;
}
.form-group textarea {
  min-height: 80px;
  resize: vertical;
}
.checkbox-group {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}
.checkbox-group input[type="checkbox"] {
  margin-right: 0.4rem;
}
.checkbox-group .checkbox-label {
  font-size: 0.9rem;
  color: #495057;
}

/* CREATE BUTTON */
.create-event-button {
  background-color: #28a745; 
  color: #fff;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 0.25rem;
  font-size: 0.9rem;
  cursor: pointer;
}
.create-event-button:hover {
  background-color: #218838;
}

/* FORM MESSAGE */
.form-message {
  margin-top: 0.5rem;
  padding: 0.6rem 1rem;
  border-radius: 0.25rem;
  font-size: 0.9rem;
}
.form-message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}
.form-message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .admin-body-container {
    flex-direction: column;
    height: auto;
  }
  .admin-sidebar {
    width: 100%;
    border-bottom: 1px solid #ced4da;
  }
  .admin-content {
    padding: 1rem;
  }
  .admin-content-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .content-area {
    grid-template-columns: 1fr;
  }
}

/* ===================== START upcoming event list link styles ===================== */
.event-link {
  text-decoration: none;
  color: var(--primary);
  padding: 0.5rem 0;
  display: block;
  transition: color 0.3s ease, background-color 0.3s ease;
}

.event-link:hover {
  color: var(--accent);
  background-color: rgba(0, 0, 0, 0.4); 
  backdrop-filter: blur(10px);
  border-radius: 0.5rem;
  border-bottom: none;
}
/* ===================== END upcoming event list link styles ===================== */

/* ===================== MUSIC ADMIN (Consistent with Management Theme) ===================== */
.music-admin .data-widget {
  /* Match the existing white widget style */
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 1.5rem;
  color: #343a40;
  font-family: 'Roboto', sans-serif; /* Use a modern sans-serif to match your other widgets */
  margin-bottom: 1.5rem;
  position: relative;
  overflow: hidden;
}

/* Section Heading */
.music-admin .data-widget h3 {
  color: #343a40;
  text-transform: none;  /* Keep normal case if you want */
  letter-spacing: 1px;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  font-weight: 600;
}

/* ===================== Playlist Table ===================== */
.music-admin .playlist-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.music-admin .playlist-table th,
.music-admin .playlist-table td {
  padding: 0.8rem;
  border-bottom: 1px solid #dee2e6;
}

.music-admin .playlist-table th {
  background: #f8f9fa;
  color: #343a40;
  text-align: left;
  font-weight: 600;
}

.music-admin .playlist-table td {
  color: #495057;
}

.music-admin .playlist-table tr:hover {
  background: #f8f9fa;
}

/* ===================== Music Form Inputs ===================== */
/* Group each input with a label in a .form-group-music container */
.music-admin .form-group-music {
  margin-bottom: 1rem;
}

.music-admin .form-group-music label {
  display: block;
  color: #343a40;
  margin-bottom: 0.4rem;
  font-weight: 500;
}

.music-admin .form-group-music input {
  background: #f8f9fa;
  border: 1px solid #ced4da;
  color: #495057;
  padding: 0.6rem 0.75rem;
  border-radius: 0.25rem;
  width: 100%;
  font-family: 'Roboto', sans-serif;
  font-size: 0.9rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.music-admin .form-group-music input:focus {
  outline: none;
  background-color: #fff;
  border-color: #dc3545; /* match your accent color if desired */
  box-shadow: 0 0 5px rgba(220, 53, 69, 0.3);
}

/* Placeholder styling */
.music-admin .form-group-music input::placeholder {
  color: #6c757d;
  font-style: italic;
}

/* ===================== Delete Button ===================== */
.music-admin .delete-song {
  background: #ff0055;
  border: none;
  color: #fff;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s ease, box-shadow 0.3s ease;
  font-family: 'Roboto Mono', monospace;
  letter-spacing: 1px;
}

.music-admin .delete-song:hover {
  background: #cc0044;
  box-shadow: 
    0 0 10px #ff0055,
    0 0 20px rgba(255, 0, 85, 0.5);
}

/* ===================== Optional Subtle Overlay ===================== */
/* If you want a very subtle pattern, lighten it to keep the white aesthetic. */
.music-admin .data-widget::after {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: radial-gradient(
    circle,
    rgba(0, 0, 0, 0.02) 10%,
    transparent 10.01%
  );
  background-size: 20px 20px;
  pointer-events: none;
  opacity: 0.3; /* Keep it subtle for a professional feel */
}

.maintenance-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-input-container {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.message-input-container input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  font-size: 0.9rem;
}

.update-message-button {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.update-message-button:hover:not(:disabled) {
  background-color: #218838;
}

.update-message-button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.message-hint {
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #6c757d;
}

:root.dark-mode .message-hint {
  color: #adb5bd;
}

:root.dark-mode .message-input-container input {
  background-color: var(--input-bg);
  color: var(--text);
  border-color: var(--border-color);
}

:root.dark-mode .update-message-button {
  background-color: #28a745;
}

:root.dark-mode .update-message-button:hover:not(:disabled) {
  background-color: #218838;
}

/* Team Manager Styles */
.team-manager .data-widget {
  background: #fff;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.team-members-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.team-member-card {
  background: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.member-avatar {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto;
}

.member-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.change-avatar-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.member-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.member-info input,
.member-info textarea {
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  font-size: 0.9rem;
}

.member-info textarea {
  min-height: 80px;
  resize: vertical;
}

.member-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.save-btn,
.delete-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.9rem;
}

.save-btn {
  background: #28a745;
  color: white;
}

.delete-btn {
  background: #dc3545;
  color: white;
}

.add-member-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 1rem;
}

.add-member-btn:hover {
  background: #0056b3;
}
</style>
