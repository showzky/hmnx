<template>
  <section v-if="userRoles.includes('admin') || userRoles.includes('developer')">
    <div class="sec-head mb24">
      <div>
        <div class="sec-title">Bruker<em>admin</em></div>
        <div class="sec-subtitle">Administrer brukere, roller og achievements.</div>
      </div>
    </div>
    <div class="g2 mb16">
      <!-- Update User Role -->
      <div class="panel">
        <div class="panel-head"><span class="panel-title">Oppdater brukerrolle</span></div>
        <div class="panel-body">
          <div class="form-group">
            <label class="form-label">Velg bruker</label>
            <select class="form-select" :value="userRoleUpdate.selectedUser"
              @change="updateUserRoleUpdate('selectedUser', $event.target.value)">
              <option value="" disabled>Velg bruker</option>
              <option v-for="user in usersList" :key="user.id" :value="user.id">
                {{ user.username || user.email }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Velg rolle</label>
            <select class="form-select" :value="userRoleUpdate.newRole"
              @change="updateUserRoleUpdate('newRole', $event.target.value)">
              <option value="" disabled>Velg rolle</option>
              <option v-for="role in availableRoles" :key="role.id" :value="role.id">{{ role.name }}</option>
            </select>
          </div>
          <div v-if="selectedUserRoles.length" style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;align-items:center;">
            <span style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;">Nåværende:</span>
            <span v-for="role in selectedUserRoles" :key="role.id" class="badge b-cyan">{{ role.name }}</span>
          </div>
          <button class="btn btn-red btn-sm" @click="$emit('updateUserRole')">Oppdater rolle</button>
          <div v-if="updateUserMessage" class="form-message" :class="{ success: updateUserSuccess, error: !updateUserSuccess }">{{ updateUserMessage }}</div>
        </div>
      </div>
      <!-- Remove User Roles -->
      <div class="panel">
        <div class="panel-head"><span class="panel-title">Fjern brukerroller</span></div>
        <div class="panel-body">
          <div class="form-group">
            <label class="form-label">Velg bruker</label>
            <select class="form-select" :value="userRoleRemove.selectedUser"
              @change="onUserRoleRemoveChange($event.target.value)">
              <option value="" disabled>Velg bruker</option>
              <option v-for="user in usersList" :key="user.id" :value="user.id">
                {{ user.username || user.email }}
              </option>
            </select>
          </div>
          <div class="checkbox-group-vertical" v-if="selectedUserRolesToRemove.length">
            <label v-for="role in selectedUserRolesToRemove" :key="role.id" class="custom-checkbox">
              <input type="checkbox" :value="role.id" :checked="rolesToRemove.includes(role.id)"
                @change="toggleRoleToRemove(role.id)" style="accent-color:var(--cyan);" />
              <span class="badge b-muted">{{ role.name }}</span>
            </label>
          </div>
          <div v-else-if="userRoleRemove.selectedUser" style="font-size:12px;color:var(--muted);margin-bottom:12px;">Ingen roller å fjerne.</div>
          <button class="btn btn-danger btn-sm" @click="$emit('removeSelectedRoles')">Fjern valgte roller</button>
          <div v-if="removeRoleMessage" class="form-message" :class="{ success: removeRoleSuccess, error: !removeRoleSuccess }">{{ removeRoleMessage }}</div>
        </div>
      </div>
    </div>
    <div class="g2 mb16">
      <!-- Create New Role -->
      <div class="panel">
        <div class="panel-head"><span class="panel-title">Opprett ny rolle</span></div>
        <div class="panel-body">
          <div class="role-preview-wrap">
            <span class="role-preview-label">Forhåndsvisning:</span>
            <span class="badge" :style="{ background: newRole.badge_color || 'rgba(136,136,136,0.2)', color: '#fff' }">
              <i v-if="newRole.badge_icon" :class="newRole.badge_icon"></i>
              {{ newRole.name || 'Ny Rolle' }}
            </span>
          </div>
          <div class="form-group">
            <label class="form-label">Rollenavn</label>
            <input class="form-input" :value="newRole.name" @input="updateNewRole('name', $event.target.value)" placeholder="f.eks. Producer" />
          </div>
          <div class="form-group">
            <label class="form-label">Badge-farge</label>
            <div style="display:flex;align-items:center;gap:8px;">
              <input type="color" :value="newRole.badge_color || '#5865f2'"
                @input="updateNewRole('badge_color', $event.target.value)"
                style="width:36px;height:36px;border:1px solid var(--border2);border-radius:6px;padding:2px;background:var(--s2);cursor:pointer;" />
              <input class="form-input" :value="newRole.badge_color" @input="updateNewRole('badge_color', $event.target.value)" placeholder="#5865f2" style="max-width:120px;" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Badge-ikon (Font Awesome)</label>
            <input class="form-input" :value="newRole.badge_icon" @input="updateNewRole('badge_icon', $event.target.value)" placeholder="fas fa-microphone" />
          </div>
          <button class="btn btn-red btn-sm" @click="$emit('createRole')">Opprett rolle</button>
          <div v-if="createRoleMessage" class="form-message" :class="{ success: createRoleSuccess, error: !createRoleSuccess }">{{ createRoleMessage }}</div>
        </div>
      </div>
      <!-- Existing Roles -->
      <div class="panel">
        <div class="panel-head"><span class="panel-title">Eksisterende roller</span></div>
        <div class="panel-body" style="padding:0;">
          <div v-for="role in availableRoles" :key="role.id"
            style="display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-bottom:1px solid var(--border);">
            <span class="badge" :style="{ background: role.badge_color ? role.badge_color + '22' : 'rgba(255,255,255,0.06)', color: role.badge_color || 'var(--text)', border: '1px solid ' + (role.badge_color || 'var(--border)') + '44' }">
              <i v-if="role.badge_icon" :class="role.badge_icon"></i>
              {{ role.name }}
            </span>
            <button class="btn btn-danger btn-sm" @click="$emit('deleteRole', role.id)">Slett</button>
          </div>
        </div>
      </div>
    </div>
    <!-- User Achievements -->
    <div class="panel">
      <div class="panel-head"><span class="panel-title">Administrer bruker-achievements</span></div>
      <div class="panel-body">
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Velg bruker</label>
            <select class="form-select" v-model="achvUserId" @change="fetchUserAchievements">
              <option value="" disabled>Velg bruker</option>
              <option v-for="user in usersList" :key="user.id" :value="user.id">{{ user.username || user.email }}</option>
            </select>
          </div>
          <div>
            <div class="checkbox-group-vertical" v-if="userAchievements.length">
              <label v-for="achv in userAchievements" :key="achv.achievement_id" class="custom-checkbox">
                <input type="checkbox" :value="achv.achievement_id" v-model="selectedAchievements" style="accent-color:var(--cyan);" />
                {{ achv.name || achv.title }}
                <span v-if="achv.unlocked_at" style="font-size:10px;color:var(--muted);">({{ achv.unlocked_at.slice(0,10) }})</span>
              </label>
            </div>
            <p v-else-if="achvUserId" style="font-size:12px;color:var(--muted);">Ingen achievements låst opp ennå.</p>
          </div>
        </div>
        <button class="btn btn-danger btn-sm" style="margin-top:10px;" @click="deleteUserAchievement" :disabled="!selectedAchievements.length">
          Fjern valgte achievements
        </button>
        <div v-if="achvRemoveMessage" class="form-message" :class="{ success: achvRemoveSuccess, error: !achvRemoveSuccess }">{{ achvRemoveMessage }}</div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  props: [
    'userRoles',
    'usersList',
    'userRoleUpdate',
    'availableRoles',
    'updateUserMessage',
    'updateUserSuccess',
    'selectedUserRoles',
    'userRoleRemove',
    'selectedUserRolesToRemove',
    'rolesToRemove',
    'removeRoleMessage',
    'removeRoleSuccess',
    'newRole',
    'createRoleMessage',
    'createRoleSuccess'
  ],
  emits: [
    'updateUserRole',
    'fetchUserRolesToRemove',
    'removeSelectedRoles',
    'createRole',
    'deleteRole',
    'update:userRoleUpdate',
    'update:userRoleRemove',
    'update:rolesToRemove',
    'update:newRole'
  ],
  data() {
    return {
      // --- Achievements section state ---
      achvUserId: '',                 // Selected user for achievements
      userAchievements: [],           // Achievements fetched for user
      selectedAchievements: [],       // Which achievements are checked for removal
      achvRemoveMessage: '',          // Feedback message
      achvRemoveSuccess: false        // Success status
    }
  },
  methods: {
    updateUserRoleUpdate(field, value) {
      const updated = { ...this.userRoleUpdate, [field]: value };
      this.$emit('update:userRoleUpdate', updated);
    },
    onUserRoleRemoveChange(value) {
      const updated = { ...this.userRoleRemove, selectedUser: value };
      this.$emit('update:userRoleRemove', updated);
      this.$emit('fetchUserRolesToRemove');
    },
    toggleRoleToRemove(roleId) {
      let updatedRoles;
      if (this.rolesToRemove.includes(roleId)) {
        updatedRoles = this.rolesToRemove.filter(id => id !== roleId);
      } else {
        updatedRoles = [...this.rolesToRemove, roleId];
      }
      this.$emit('update:rolesToRemove', updatedRoles);
    },
    updateNewRole(field, value) {
      const updated = { ...this.newRole, [field]: value };
      this.$emit('update:newRole', updated);
    },
    // --- Achievements Management ---
    async fetchUserAchievements() {
      if (!this.achvUserId) {
        this.userAchievements = [];
        return;
      }
      try {
        const apiBase = import.meta.env.VITE_API_URL; // should be http://localhost:5000/api
        const response = await fetch(`${apiBase}/user/${this.achvUserId}/achievements`, {
          headers: {
            Authorization: 'Bearer ' + localStorage.getItem('access_token')
          }
        });
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Error response:', errorText);
          throw new Error('Failed to fetch achievements');
        }
        const data = await response.json();
        this.userAchievements = data;
        this.selectedAchievements = [];
        this.achvRemoveMessage = '';
        this.achvRemoveSuccess = false;
      } catch (e) {
        this.userAchievements = [];
        this.achvRemoveMessage = 'Failed to fetch achievements.';
        this.achvRemoveSuccess = false;
        console.error('Error fetching achievements:', e);
      }
    },
    async deleteUserAchievement() {
      if (this.selectedAchievements.length === 0) {
        this.achvRemoveMessage = "No achievements selected.";
        this.achvRemoveSuccess = false;
        return;
      }
      try {
        // Remove one at a time (for simplicity)
        for (const achvId of this.selectedAchievements) {
          const apiBase = import.meta.env.VITE_API_URL; // should be http://localhost:5000/api
          await fetch(`${apiBase}/admin/delete-user-achievement`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: 'Bearer ' + localStorage.getItem('access_token')
            },
            body: JSON.stringify({
              user_id: this.achvUserId,
              achievement_id: achvId
            })
          });
        }
        this.achvRemoveMessage = "Selected achievements removed!";
        this.achvRemoveSuccess = true;
        this.selectedAchievements = [];
        await this.fetchUserAchievements(); // Refresh the list
      } catch (e) {
        this.achvRemoveMessage = "Failed to remove achievements.";
        this.achvRemoveSuccess = false;
      }
    }
  }
}
</script>


<style scoped>
.checkbox-group-vertical {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}
</style>
