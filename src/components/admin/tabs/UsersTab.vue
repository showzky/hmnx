<template>
  <section v-if="userRoles.includes('admin') || userRoles.includes('developer')">

    <!-- Header -->
    <div class="sec-head mb24">
      <div>
        <div class="sec-title">Bruker<em>admin</em></div>
        <div class="sec-subtitle">Administrer brukere, roller og achievements.</div>
      </div>
    </div>

    <!-- Row 1: Update Role + Remove Roles -->
    <div class="g2 mb16">

      <!-- Update User Role -->
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Oppdater brukerrolle</span>
        </div>
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
          <div v-if="selectedUserRoles.length" class="current-roles-container">
            <span class="form-label">Nåværende:</span>
            <span v-for="role in selectedUserRoles" :key="role.id"
              class="role-badge"
              :style="roleBadgeStyle(role)">{{ role.name }}</span>
          </div>
          <button class="btn btn-red btn-sm" style="margin-top:14px;" @click="$emit('updateUserRole')">Oppdater rolle</button>
          <div v-if="updateUserMessage" class="form-message" :class="{ success: updateUserSuccess, error: !updateUserSuccess }">{{ updateUserMessage }}</div>
        </div>
      </div>

      <!-- Remove User Roles -->
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Fjern brukerroller</span>
        </div>
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
          <div v-if="selectedUserRolesToRemove.length" class="role-remove-list">
            <label v-for="role in selectedUserRolesToRemove" :key="role.id" class="role-remove-row" :class="{ selected: rolesToRemove.includes(role.id) }">
              <input type="checkbox" :value="role.id" :checked="rolesToRemove.includes(role.id)"
                @change="toggleRoleToRemove(role.id)" style="accent-color:var(--cyan);" />
              <span class="role-badge" :style="roleBadgeStyle(role)">{{ role.name }}</span>
            </label>
          </div>
          <div v-else-if="userRoleRemove.selectedUser" class="empty-hint">Ingen roller å fjerne.</div>
          <button class="btn btn-danger btn-sm" @click="$emit('removeSelectedRoles')">Fjern valgte roller</button>
          <div v-if="removeRoleMessage" class="form-message" :class="{ success: removeRoleSuccess, error: !removeRoleSuccess }">{{ removeRoleMessage }}</div>
        </div>
      </div>

    </div>

    <!-- Row 2: Create Role + Existing Roles -->
    <div class="g2 mb16">

      <!-- Create New Role -->
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Opprett ny rolle</span>
        </div>
        <div class="panel-body">
          <div class="role-preview-wrap">
            <span class="role-preview-label">Forhåndsvisning:</span>
            <span class="role-badge" :style="previewBadgeStyle">{{ newRole.name || 'Ny Rolle' }}</span>
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
                class="color-picker" />
              <input class="form-input" :value="newRole.badge_color"
                @input="onHexInput($event.target.value)"
                placeholder="#5865f2" style="max-width:130px;" />
            </div>
          </div>
          <button class="btn btn-red btn-sm" @click="$emit('createRole')">Opprett rolle</button>
          <div v-if="createRoleMessage" class="form-message" :class="{ success: createRoleSuccess, error: !createRoleSuccess }">{{ createRoleMessage }}</div>
        </div>
      </div>

      <!-- Existing Roles -->
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Eksisterende roller</span>
          <span class="panel-meta">{{ availableRoles.length }} roller</span>
        </div>
        <div class="panel-body" style="padding:0;">
          <div v-if="!availableRoles.length" class="empty-hint" style="padding:16px;">Ingen roller opprettet ennå.</div>
          <div v-for="role in availableRoles" :key="role.id" class="role-row">
            <div class="role-row-left">
              <span class="role-badge" :style="roleBadgeStyle(role)">{{ role.name }}</span>
            </div>
            <button class="btn btn-danger btn-sm" @click="$emit('deleteRole', role.id)">Slett</button>
          </div>
        </div>
      </div>

    </div>

    <!-- User Achievements Management -->
    <div class="panel">
      <div class="panel-head">
        <span class="panel-title">Administrer bruker-achievements</span>
        <span v-if="achvUserId && userAchievements.length" class="panel-meta">{{ userAchievements.length }} achievements</span>
      </div>
      <div class="panel-body">
        <div class="form-group" style="max-width:320px;">
          <label class="form-label">Velg bruker</label>
          <select class="form-select" v-model="achvUserId" @change="fetchUserAchievements">
            <option value="" disabled>Velg bruker</option>
            <option v-for="user in usersList" :key="user.id" :value="user.id">{{ user.username || user.email }}</option>
          </select>
        </div>

        <template v-if="achvUserId">
          <div v-if="userAchievements.length" class="ach-admin-grid">
            <label
              v-for="achv in userAchievements"
              :key="achv.achievement_id"
              class="ach-admin-card"
              :class="[achvRarityClass(achv), { 'is-selected': selectedAchievements.includes(achv.achievement_id) }]"
            >
              <input type="checkbox" :value="achv.achievement_id" v-model="selectedAchievements" class="ach-checkbox" />
              <div class="ach-admin-icon">
                <img v-if="isImgUrl(achv.svg || achv.icon)" :src="achv.svg || achv.icon" :alt="achv.name || achv.title" />
                <span v-else-if="achv.svg || achv.icon" v-html="achv.svg || achv.icon" />
                <span v-else>🏆</span>
              </div>
              <div class="ach-admin-info">
                <div class="ach-admin-name">{{ achv.name || achv.title }}</div>
                <div class="ach-admin-meta">
                  <span class="badge" :class="achvRarityBadge(achv)">{{ achv.rarity || 'common' }}</span>
                  <span v-if="achv.unlocked_at" class="ach-admin-date">{{ achv.unlocked_at.slice(0,10) }}</span>
                </div>
              </div>
              <div v-if="selectedAchievements.includes(achv.achievement_id)" class="ach-admin-check">✓</div>
            </label>
          </div>
          <div v-else class="empty-hint">Ingen achievements låst opp ennå.</div>

          <div style="display:flex;align-items:center;gap:12px;margin-top:14px;flex-wrap:wrap;">
            <button class="btn btn-danger btn-sm" @click="deleteUserAchievement" :disabled="!selectedAchievements.length">
              Fjern valgte ({{ selectedAchievements.length }})
            </button>
            <span v-if="selectedAchievements.length" style="font-size:11px;color:var(--muted);">{{ selectedAchievements.length }} valgt</span>
          </div>
          <div v-if="achvRemoveMessage" class="form-message" :class="{ success: achvRemoveSuccess, error: !achvRemoveSuccess }">{{ achvRemoveMessage }}</div>
        </template>
      </div>
    </div>

  </section>
</template>

<script>
export default {
  props: [
    'userRoles', 'usersList', 'userRoleUpdate', 'availableRoles',
    'updateUserMessage', 'updateUserSuccess', 'selectedUserRoles',
    'userRoleRemove', 'selectedUserRolesToRemove', 'rolesToRemove',
    'removeRoleMessage', 'removeRoleSuccess',
    'newRole', 'createRoleMessage', 'createRoleSuccess'
  ],
  emits: [
    'updateUserRole', 'fetchUserRolesToRemove', 'removeSelectedRoles',
    'createRole', 'deleteRole',
    'update:userRoleUpdate', 'update:userRoleRemove',
    'update:rolesToRemove', 'update:newRole'
  ],
  computed: {
    previewBadgeStyle() {
      const c = (this.newRole.badge_color && /^#[0-9a-fA-F]{6}$/.test(this.newRole.badge_color))
        ? this.newRole.badge_color : '#888888'
      const r = parseInt(c.slice(1,3), 16)
      const g = parseInt(c.slice(3,5), 16)
      const b = parseInt(c.slice(5,7), 16)
      return {
        background: `rgba(${r},${g},${b},0.1)`,
        color: c,
        border: `1px solid rgba(${r},${g},${b},0.2)`
      }
    }
  },
  data() {
    return {
      achvUserId:           '',
      userAchievements:     [],
      selectedAchievements: [],
      achvRemoveMessage:    '',
      achvRemoveSuccess:    false
    }
  },
  methods: {
    hexToRgba(hex, opacity) {
      if (!hex || !hex.startsWith('#') || hex.length < 7) return `rgba(180,180,180,${opacity})`
      const r = parseInt(hex.slice(1, 3), 16)
      const g = parseInt(hex.slice(3, 5), 16)
      const b = parseInt(hex.slice(5, 7), 16)
      return `rgba(${r}, ${g}, ${b}, ${opacity})`
    },
    roleBadgeStyle(role) {
      const c = role.badge_color || '#888888'
      const style = {
        background: this.hexToRgba(c, 0.1),
        color: c,
        border: `1px solid ${this.hexToRgba(c, 0.2)}`
      }
      if (role.badge_border_style === 'dashed') style.borderStyle = 'dashed'
      return style
    },
    onHexInput(value) {
      // Only emit if it looks like a valid hex
      if (/^#[0-9a-fA-F]{6}$/.test(value) || value === '') {
        this.updateNewRole('badge_color', value)
      }
    },
    updateUserRoleUpdate(field, value) {
      this.$emit('update:userRoleUpdate', { ...this.userRoleUpdate, [field]: value })
    },
    onUserRoleRemoveChange(value) {
      this.$emit('update:userRoleRemove', { ...this.userRoleRemove, selectedUser: value })
      this.$emit('fetchUserRolesToRemove')
    },
    toggleRoleToRemove(roleId) {
      const list = this.rolesToRemove.includes(roleId)
        ? this.rolesToRemove.filter(id => id !== roleId)
        : [...this.rolesToRemove, roleId]
      this.$emit('update:rolesToRemove', list)
    },
    updateNewRole(field, value) {
      this.$emit('update:newRole', { ...this.newRole, [field]: value })
    },
    achvRarityClass(achv) {
      return (achv.rarity || 'common').toLowerCase()
    },
    achvRarityBadge(achv) {
      const map = { legendary: 'b-gold', epic: 'b-purple', rare: 'b-cyan', common: 'b-muted' }
      return map[(achv.rarity || 'common').toLowerCase()] || 'b-muted'
    },
    isImgUrl(src) {
      return typeof src === 'string' && (src.startsWith('http') || src.startsWith('data:image') || /\.(svg|png|jpe?g)$/.test(src))
    },
    async fetchUserAchievements() {
      if (!this.achvUserId) { this.userAchievements = []; return }
      try {
        const apiBase = import.meta.env.VITE_API_URL
        const res = await fetch(`${apiBase}/user/${this.achvUserId}/achievements`, {
          headers: { Authorization: 'Bearer ' + localStorage.getItem('access_token') }
        })
        if (!res.ok) throw new Error('Failed to fetch achievements')
        this.userAchievements     = await res.json()
        this.selectedAchievements = []
        this.achvRemoveMessage    = ''
        this.achvRemoveSuccess    = false
      } catch (e) {
        this.userAchievements  = []
        this.achvRemoveMessage = 'Klarte ikke å hente achievements.'
        this.achvRemoveSuccess = false
      }
    },
    async deleteUserAchievement() {
      if (!this.selectedAchievements.length) return
      try {
        const apiBase = import.meta.env.VITE_API_URL
        for (const achvId of this.selectedAchievements) {
          await fetch(`${apiBase}/admin/delete-user-achievement`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: 'Bearer ' + localStorage.getItem('access_token')
            },
            body: JSON.stringify({ user_id: this.achvUserId, achievement_id: achvId })
          })
        }
        this.achvRemoveMessage    = 'Valgte achievements er fjernet.'
        this.achvRemoveSuccess    = true
        this.selectedAchievements = []
        await this.fetchUserAchievements()
      } catch (e) {
        this.achvRemoveMessage = 'Klarte ikke å fjerne achievements.'
        this.achvRemoveSuccess = false
      }
    }
  }
}
</script>

<style scoped>
/* HMN role badge — matches design system exactly */
.role-badge {
  display: inline-block;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  padding: 3px 9px;
  border-radius: 4px;
}

/* Role row in Existing Roles panel */
.role-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  transition: background 0.15s;
}
.role-row:last-child { border-bottom: none; }
.role-row:hover { background: rgba(255,255,255,0.02); }
.role-row-left { display: flex; align-items: center; gap: 8px; }

/* Role remove checkboxes */
.role-remove-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.role-remove-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.02);
  cursor: pointer;
  transition: all 0.15s;
}
.role-remove-row:hover { border-color: var(--border2); background: rgba(255,255,255,0.04); }
.role-remove-row.selected { border-color: rgba(200,16,46,0.3); background: rgba(200,16,46,0.06); }

/* Color picker */
.color-picker {
  width: 36px;
  height: 36px;
  border: 1px solid var(--border2);
  border-radius: 6px;
  padding: 2px;
  background: var(--surface2);
  cursor: pointer;
  flex-shrink: 0;
}

/* Achievement admin grid */
.ach-admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 8px;
  margin-bottom: 4px;
}

.ach-admin-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.02);
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
  overflow: hidden;
}
.ach-admin-card::before {
  content: '';
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 2px;
}
.ach-admin-card.legendary { border-color: rgba(216,152,32,0.2); background: rgba(216,152,32,0.04); }
.ach-admin-card.legendary::before { background: var(--gold); }
.ach-admin-card.epic       { border-color: rgba(112,80,216,0.2); background: rgba(112,80,216,0.04); }
.ach-admin-card.epic::before       { background: #9070f0; }
.ach-admin-card.rare       { border-color: rgba(0,184,208,0.18); background: rgba(0,184,208,0.03); }
.ach-admin-card.rare::before       { background: var(--cyan); }
.ach-admin-card.common::before     { background: rgba(255,255,255,0.15); }

.ach-admin-card:hover { border-color: var(--border2); background: rgba(255,255,255,0.04); transform: translateX(2px); }
.ach-admin-card.is-selected { border-color: rgba(200,16,46,0.3); background: rgba(200,16,46,0.06); }

.ach-checkbox { display: none; }

.ach-admin-icon {
  width: 36px;
  height: 36px;
  border-radius: 7px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border);
  overflow: hidden;
}
.ach-admin-icon img { width: 100%; height: 100%; object-fit: contain; border-radius: 6px; }

.ach-admin-info { flex: 1; min-width: 0; }
.ach-admin-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-bright);
  font-family: var(--font-body);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}
.ach-admin-meta { display: flex; align-items: center; gap: 6px; }
.ach-admin-date { font-size: 10px; color: var(--text-muted); font-family: var(--font-display); letter-spacing: 0.04em; }

.ach-admin-check {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--red);
  color: white;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 0 8px rgba(200,16,46,0.4);
}

.empty-hint {
  font-size: 12px;
  color: var(--text-muted);
  font-style: italic;
  margin-bottom: 12px;
}
</style>
