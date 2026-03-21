<template>
  <div>
    <div v-if="!isLoading" class="admin-wrapper">
      <!-- Topbar -->
      <AdminHeader :displayName="displayName" :userRoles="userRoles" />
      <!-- Body: sidebar + content -->
      <div class="admin-layout">
        <!-- Sidebar Navigation -->
        <AdminSidebar
          :activeTab="activeTab"
          :userRoles="userRoles"
          :open="open"
          :isOnlyProducer="isOnlyProducer"
          :isAdminOrDeveloper="isAdminOrDeveloper"
          @set-active="setActive"
          @toggle-group="toggleGroup"
        />
        <!-- Main Content Area -->
        <div class="admin-main-content">
        <AdminContent
          :displayName="displayName"
          :isOnlyProducer="isOnlyProducer"
          :activeTab="activeTab"
          :searchQuery="searchQuery"
          :upcomingEventsData="upcomingEventsData"
          :newEvent="newEvent"
          :musicTracks="musicTracks"
          :musicMessage="musicMessage"
          :musicSuccess="musicSuccess"
          :createEventMessage="createEventMessage"
          :createEventSuccess="createEventSuccess"
          :userRoles="userRoles"
          :usersList="usersList"
          :userRoleUpdate="userRoleUpdate"
          :availableRoles="availableRoles"
          :updateUserMessage="updateUserMessage"
          :updateUserSuccess="updateUserSuccess"
          :selectedUserRoles="selectedUserRoles"
          :userRoleRemove="userRoleRemove"
          :selectedUserRolesToRemove="selectedUserRolesToRemove"
          :rolesToRemove="rolesToRemove"
          :removeRoleMessage="removeRoleMessage"
          :removeRoleSuccess="removeRoleSuccess"
          :newRole="newRole"
          :createRoleMessage="createRoleMessage"
          :createRoleSuccess="createRoleSuccess"
          :teamMembers="teamMembers"
          :defaultAvatar="defaultAvatar"
          :teamMessage="teamMessage"
          :teamSuccess="teamSuccess"
          :maintenanceMode="maintenanceMode"
          :noticeMaintenanceMode="noticeMaintenanceMode"
          :maintenanceBannerMessage="maintenanceBannerMessage"
          :maintenanceMessage="maintenanceMessage"
          :maintenanceSuccess="maintenanceSuccess"
          :noticeMaintenanceMessage="noticeMaintenanceMessage"
          :noticeMaintenanceSuccess="noticeMaintenanceSuccess"
          :newChangelog="newChangelog"
          :changelogEntries="changelogEntries"
          :changelogMessage="changelogMessage"
          :changelogSuccess="changelogSuccess"
          :widgets="widgets"
          @createEvent="createEvent"
          @deleteEvent="deleteEvent"
          @handleImageUpload="handleImageUpload"
          @addTrack="handleAddTrack"
          @deleteTrack="handleDeleteTrack"
          @setFeatured="handleSetFeatured"
          @reorderTracks="handleReorderTracks"
          @updateUserRole="updateUserRole"
          @fetchUserRolesToRemove="fetchUserRolesToRemove"
          @removeSelectedRoles="removeSelectedRoles"
          @createRole="createRole"
          @deleteRole="deleteRole"
          @saveTeamMember="saveTeamMember"
          @deleteTeamMember="deleteTeamMember"
          @addNewTeamMember="addNewTeamMember"
          @triggerAvatarUpload="triggerAvatarUpload"
          @onToggleMaintenance="onToggleMaintenance"
          @onToggleNoticeMaintenance="onToggleNoticeMaintenance"
          @submitChangelogEntry="submitChangelogEntry"
          @deleteChangelogEntry="deleteChangelogEntry"
          @update:searchQuery="searchQuery = $event"
          @update:newEvent="newEvent = $event"
          @update:userRoleUpdate="userRoleUpdate = $event"
          @update:userRoleRemove="userRoleRemove = $event"
          @update:rolesToRemove="rolesToRemove = $event"
          @update:newRole="newRole = $event"
          @update:teamMembers="teamMembers = $event"
          @update:maintenanceMode="maintenanceMode = $event"
          @update:noticeMaintenanceMode="noticeMaintenanceMode = $event"
          @update:maintenanceBannerMessage="maintenanceBannerMessage = $event"
          @update:newChangelog="newChangelog = $event"
        />
        </div><!-- /admin-main-content -->
      </div><!-- /admin-layout -->
    </div><!-- /admin-wrapper -->
    <div v-else>Loading Management Panel...</div>
  </div>
</template>
<script>
import '@/components/admin/assets/admin.css';
import { useAuthStore } from '@/stores/authStore';
import axios from '@/axios'; 
import { useWebSocket } from '@/composables/useWebSocket';
import { ref } from 'vue';

import AdminSidebar from '../components/admin/AdminSidebar.vue';
import AdminHeader from '../components/admin/AdminHeader.vue';
import AdminContent from '../components/admin/AdminContent.vue';

export default {
  name: 'Management',
  components: { 
    AdminSidebar,
    AdminHeader,
    AdminContent
  },
  data() {
    return {
      
      activeTab: 'dashboard',
      isLoading: true,
      searchQuery: '',
      //sidebar dropdown
      open: {
        core: true,
        content: true,
        users: true,
        extras: true
      },
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
      musicTracks: [],
      musicMessage: '',
      musicSuccess: false,
      isLoadingSongs: true,

      // Changelog
      newChangelog: {
        version: '',
        date: '',
        added: '',
        changed: ''
      },
      changelogMessage: '',
      changelogSuccess: false,
      changelogEntries: [],
    };
  },

  computed: {
    auth() {
      return useAuthStore();
    },
    canAccessManagement() {
      return ['developer', 'admin', 'producer'].some(role => this.userRoles.includes(role));
    },
    isProducer() {
      return this.userRoles.includes('producer');
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
    isOnlyProducer() {
      return (
        this.userRoles.includes('producer') &&
        !this.userRoles.includes('admin') &&
        !this.userRoles.includes('developer')
      );
    },
    isAdminOrDeveloper() {
      return this.userRoles.includes('admin') || this.userRoles.includes('developer');
    },
  },

  methods: {
    setActive(tab) {
      this.activeTab = tab;
    },
    toggleGroup(groupName) {
      this.open[groupName] = !this.open[groupName];
    },
    onDragEnd(evt) {
    console.log('New event order:', this.filteredEvents);
    // Optional: Save the new order here
  },
    setMusicFeedback(message, success) {
      this.musicMessage = message;
      this.musicSuccess = success;
      setTimeout(() => {
        this.musicMessage = '';
      }, 3000);
    },


    // ---------------- MAINTENANCE ----------------
    fetchMaintenanceStatus() {
      axios.get('/maintenance-status')
        .then(res => {
          this.maintenanceMode = res.data.maintenance_mode === 'on';
          this.noticeMaintenanceMode = res.data.notice_maintenance_mode === 'on';
          this.maintenanceBannerMessage = res.data.notice_maintenance_message || '';
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
        setTimeout(() => this.noticeMaintenanceMessage = '', 3000);
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
        .then(res => {
          this.availableRoles = res.data.roles;
          console.log('Fetched roles:', this.availableRoles); // Debug log
        })
        .catch(err => {
          console.error('Error fetching roles:', err);
          this.availableRoles = [];
        });
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
          // Fetch the updated roles list
          this.fetchRoles();
        })
        .catch(err => {
          console.error('Error creating role:', err);
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
      .catch(err => {
        console.error('Error creating event:', err.response?.data || err);
        this.createEventMessage = err.response?.data?.msg || 'Error creating event.';
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
    fetchMusicTracks() {
      axios.get('/music')
        .then(res => {
          this.musicTracks = Array.isArray(res.data)
            ? [...res.data].sort((a, b) => a.position - b.position)
            : [];
        })
        .catch(err => {
          console.error('Music fetch error:', err);
          this.setMusicFeedback('Kunne ikke laste bangerlisten.', false);
        })
        .finally(() => {
          this.isLoadingSongs = false;
        });
    },
    handleAddTrack(track) {
      axios.post('/music', track)
        .then(res => {
          const savedTrack = res.data?.track;
          if (savedTrack) {
            const nextTracks = savedTrack.featured
              ? this.musicTracks.map(item => ({ ...item, featured: false }))
              : this.musicTracks;

            this.musicTracks = [...nextTracks, savedTrack].sort((a, b) => a.position - b.position);
          } else {
            this.fetchMusicTracks();
          }
          this.setMusicFeedback('Banger lagt til.', true);
        })
        .catch(err => {
          console.error('Add track error:', err);
          this.setMusicFeedback(err.response?.data?.error || 'Kunne ikke lagre bangeren.', false);
        });
    },
    handleDeleteTrack(trackId) {
      const track = this.musicTracks.find(item => item.id === trackId);
      if (track && !confirm(`Delete "${track.title}"?`)) {
        return;
      }

      axios.delete(`/music/${trackId}`)
        .then(() => {
          this.musicTracks = this.musicTracks.filter(item => item.id !== trackId);
          this.musicTracks = this.musicTracks.map((item, index) => ({ ...item, position: index }));
          this.setMusicFeedback('Banger slettet.', true);
        })
        .catch(err => {
          console.error('Delete track error:', err);
          this.setMusicFeedback('Kunne ikke slette bangeren.', false);
        });
    },
    handleSetFeatured(trackId) {
      axios.put(`/music/${trackId}/featured`)
        .then(res => {
          this.musicTracks = Array.isArray(res.data?.tracks)
            ? [...res.data.tracks].sort((a, b) => a.position - b.position)
            : this.musicTracks.map(track => ({
                ...track,
                featured: track.id === trackId,
              }));
          this.setMusicFeedback('Featured-banger oppdatert.', true);
        })
        .catch(err => {
          console.error('Set featured error:', err);
          this.setMusicFeedback('Kunne ikke oppdatere featured-status.', false);
        });
    },
    handleReorderTracks(orderedIds) {
      const orderedMap = new Map(this.musicTracks.map(track => [track.id, track]));
      this.musicTracks = orderedIds
        .map(({ id, position }) => {
          const track = orderedMap.get(id);
          return track ? { ...track, position } : null;
        })
        .filter(Boolean);

      axios.put('/music/reorder', { tracks: orderedIds })
        .then(res => {
          this.musicTracks = Array.isArray(res.data?.tracks)
            ? [...res.data.tracks].sort((a, b) => a.position - b.position)
            : this.musicTracks;
          this.setMusicFeedback('Rekkefolge oppdatert.', true);
        })
        .catch(err => {
          console.error('Reorder tracks error:', err);
          this.setMusicFeedback('Kunne ikke lagre ny rekkefolge.', false);
          this.fetchMusicTracks();
        });
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

    deleteTeamMember(memberId) {
  // Remove from UI immediately
  this.teamMembers = this.teamMembers.filter(m => m.id !== memberId);

  // If the member exists in the backend, delete from server
  if (memberId) {
    axios.delete(`/team-members/${memberId}`)
      .then(() => {
        this.teamMessage = 'Team member deleted!';
        this.teamSuccess = true;
        this.fetchTeamMembers(); // Refresh list
      })
      .catch(err => {
        console.error('Error deleting team member:', err);
        this.teamMessage = 'Failed to delete team member.';
        this.teamSuccess = false;
      })
      .finally(() => {
        setTimeout(() => this.teamMessage = '', 3000);
      });
  }
},

    async submitChangelogEntry() {
  try {
    const entry = {
      version: this.newChangelog.version,
      date: this.newChangelog.date,
      changes: {
        Added: this.newChangelog.added.split('\n').filter(line => line.trim() !== ''),
        Changed: this.newChangelog.changed.split('\n').filter(line => line.trim() !== ''),
      },
    };
    await this.addChangeLogEntry(entry); // Ensure this matches the method name
    this.changelogMessage = 'Changelog entry added successfully!';
    this.changelogSuccess = true;

    // Reset the form
    this.newChangelog = { version: '', date: '', added: '', changed: '' };
  } catch (error) {
    console.error('Failed to submit changelog entry:', error);
    this.changelogMessage = 'Failed to add changelog entry.';
    this.changelogSuccess = false;
  } finally {
    setTimeout(() => (this.changelogMessage = ''), 3000);
  }
},
  async fetchChangelogEntries() {
    try {
      const response = await axios.get('/changelog');
      this.changelogEntries = response.data;
    } catch (error) {
      console.error('Failed to fetch changelog entries:', error);
    }
  },

  async deleteChangelogEntry(id) {
    if (!confirm('Are you sure you want to delete this changelog entry?')) return;

    try {
      await axios.delete(`/changelog/${id}`);
      this.changelogEntries = this.changelogEntries.filter(entry => entry.id !== id);
      alert('Changelog entry deleted successfully!');
    } catch (error) {
      console.error('Failed to delete changelog entry:', error);
      alert('Failed to delete changelog entry.');
    }
  },
  async addChangeLogEntry(entry) {
    try {
      await axios.post('/changelog', entry);
      alert('Changelog entry added successfully!');
    } catch (error) {
      console.error('Failed to add changelog entry:', error);
      alert('Failed to add changelog entry.');
    }
  },

  },

  mounted() {
    if (!localStorage.getItem('access_token')) {
      return this.$router.push('/login');
    }

    if (!this.canAccessManagement) {
      this.$router.push('/');
      return;
    }

    this.fetchMaintenanceStatus();
    this.fetchUsersList();
    this.fetchRoles();
    this.fetchUpcomingEvents();
    this.fetchMusicTracks();
    this.fetchTeamMembers();
    this.fetchChangelogEntries();
    
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
    
    if (this.isOnlyProducer) {
      this.activeTab = 'content';
    }

    // Initialize sortable after data is loaded and DOM is updated
    // Note: We don't initialize Sortable here anymore since it's handled in watch.activeTab
  },

  watch: {
  activeTab(newTab) {
    if (newTab === 'users') {
      this.fetchRoles(); // Refresh roles when switching to users tab
    }

    // No need to initialize Sortable here anymore as it's handled in component lifecycle or using event bus
  }
},



  setup() {
    const snackBar = ref(null);
    const { socket } = useWebSocket();

    return { 
      snackBar, 
      socket
    };
  }
};
</script>

<style scoped>

</style>

