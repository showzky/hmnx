<template>
  <section v-if="userRoles.includes('admin') || userRoles.includes('developer') || userPermissions.includes('manage_roles') || userPermissions.includes('manage_users')">
    <div class="sec-head mb24">
      <div>
        <div class="sec-title">Roles & <em>Permissions</em></div>
        <div class="sec-subtitle">Administrer roller, medlemmer og neste generasjons tilgangsstyring fra ett sted.</div>
      </div>
    </div>

    <div class="rp-layout mb16">
      <aside class="panel">
        <div class="panel-head">
          <span class="panel-title">Roller</span>
          <button class="btn btn-red btn-sm" @click="startDraft">Ny rolle</button>
        </div>
        <div class="panel-body role-list">
          <button
            v-for="role in roleItems"
            :key="role.key"
            type="button"
            class="role-item"
            :class="{ active: selectedRoleKey === role.key }"
            @click="selectedRoleKey = role.key"
          >
            <span class="role-dot" :style="{ background: roleColor(role.badge_color) }"></span>
            <div class="role-copy">
              <div class="role-line">
                <span class="role-name">{{ role.name }}</span>
                <span class="tiny-pill" :class="{ muted: !isSystemRole(role) }">{{ isSystemRole(role) ? 'System' : 'Custom' }}</span>
              </div>
              <div class="role-meta">{{ memberCount(role.id) }} medlemmer · {{ roleFlavorLabel(role) }}</div>
            </div>
          </button>
        </div>
      </aside>

      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">{{ isDraft ? 'Ny rolle' : selectedRole?.name || 'Role Editor' }}</span>
          <div class="head-actions">
            <span v-if="!isDraft && isSystemRole(selectedRole)" class="tiny-pill">Beskyttet</span>
            <button v-if="isDraft" class="btn btn-red btn-sm" :disabled="!draft.name.trim()" @click="createDraft">Opprett rolle</button>
            <template v-else>
              <button class="btn btn-red btn-sm" @click="saveSelectedRole">Lagre endringer</button>
              <button v-if="!isSystemRole(selectedRole)" class="btn btn-danger btn-sm" @click="$emit('deleteRole', selectedRole.id)">Slett rolle</button>
            </template>
          </div>
        </div>

        <div class="panel-body">
          <div class="editor-grid">
            <section class="editor-card">
              <div class="editor-title">Display</div>
              <div class="field-grid">
                <label class="form-group">
                  <span class="form-label">Rollenavn</span>
                  <input class="form-input" :value="isDraft ? draft.name : selectedRole?.name" :readonly="!isDraft" @input="draft.name = $event.target.value" />
                </label>
                <label class="form-group">
                  <span class="form-label">Dashboard flavor</span>
                  <select class="form-select" :value="roleConfig.flavor" @change="updateConfig('flavor', $event.target.value)">
                    <option value="default">Default dashboard</option>
                    <option value="music">Music dashboard</option>
                  </select>
                </label>
              </div>
              <div class="field-grid">
                <label class="form-group">
                  <span class="form-label">Badge-farge</span>
                  <div class="color-row">
                    <input type="color" class="color-picker" :value="currentColor" @input="onColor($event.target.value)" />
                    <input class="form-input" :value="currentColor" :readonly="!isDraft" @input="onHex($event.target.value)" />
                  </div>
                </label>
                <div class="form-group">
                  <span class="form-label">Forhåndsvisning</span>
                  <div class="preview-box">
                    <span class="role-badge" :style="badgeStyle(currentColor)">{{ (isDraft ? (draft.name || 'Ny rolle') : selectedRole?.name || 'Rolle').toUpperCase() }}</span>
                    <span class="preview-note">{{ roleFlavorLabel(selectedRole) }}</span>
                  </div>
                </div>
              </div>
              <div class="editor-note">Nye roller starter trygt med null permissions. Flavor styrer kun visning, ikke tilgang.</div>
            </section>

            <section class="editor-card">
              <div class="editor-title">Permissions</div>
              <div v-for="group in permissionGroups" :key="group.label" class="perm-group">
                <div class="perm-group-title">{{ group.label }}</div>
                <label v-for="perm in group.items" :key="perm.key" class="perm-row">
                  <div>
                    <div class="perm-name">{{ perm.label }}</div>
                    <div class="perm-desc">{{ perm.description }}</div>
                  </div>
                  <input type="checkbox" :checked="roleConfig.permissions.includes(perm.key)" @change="togglePermission(perm.key)" />
                </label>
              </div>
            </section>
          </div>

          <section class="editor-card members-card">
            <div class="editor-title">Members</div>
            <div class="member-toolbar">
              <div class="member-picker-stack">
                <label class="form-group member-picker-search">
                  <span class="form-label">Søk etter bruker</span>
                  <input
                    v-model="memberSearch"
                    class="form-input"
                    type="text"
                    placeholder="Søk på navn eller e-post"
                  />
                </label>
              </div>
            </div>
            <div v-if="roleFeedback" class="form-message" :class="{ success: roleFeedbackSuccess, error: !roleFeedbackSuccess }">{{ roleFeedback }}</div>
            <div v-if="!isDraft" class="add-results">
              <div v-if="memberSearch.trim() && filteredAddableUsers.length" class="member-list">
                <div v-for="user in filteredAddableUsers" :key="user.id" class="member-row member-row-add">
                  <router-link :to="`/users/${user.id}`" class="member-link">
                    <div class="member-name">{{ user.username || user.email }}</div>
                    <div class="member-meta">{{ user.email || 'Ingen e-post registrert' }}</div>
                  </router-link>
                  <button class="btn btn-red btn-sm" @click="addMember(user)">Legg til rolle</button>
                </div>
              </div>
              <div v-else-if="memberSearch.trim()" class="empty-hint">Ingen tilgjengelige brukere matcher søket.</div>
            </div>
            <div v-if="members.length" class="member-list">
              <div v-for="member in members" :key="member.id" class="member-row">
                <router-link :to="`/users/${member.id}`" class="member-link">
                  <div class="member-name">{{ member.username || member.email }}</div>
                  <div class="member-meta">{{ member.email || 'Ingen e-post registrert' }}</div>
                </router-link>
                <button class="btn btn-ghost btn-sm" :disabled="isDraft" @click="removeMember(member)">Fjern rolle</button>
              </div>
            </div>
            <div v-else class="empty-hint">Ingen medlemmer har denne rollen ennå.</div>
          </section>
        </div>
      </div>
    </div>

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
            <label v-for="achv in userAchievements" :key="achv.achievement_id" class="ach-admin-card" :class="[achvRarityClass(achv), { 'is-selected': selectedAchievements.includes(achv.achievement_id) }]">
              <input v-model="selectedAchievements" type="checkbox" :value="achv.achievement_id" class="ach-checkbox" />
              <div class="ach-admin-icon">
                <img v-if="isImgUrl(achv.svg || achv.icon)" :src="achv.svg || achv.icon" :alt="achv.name || achv.title" />
                <span v-else-if="achv.svg || achv.icon" v-html="achv.svg || achv.icon" />
                <span v-else>T</span>
              </div>
              <div class="ach-admin-info">
                <div class="ach-admin-name">{{ achv.name || achv.title }}</div>
                <div class="ach-admin-meta">
                  <span class="badge" :class="achvRarityBadge(achv)">{{ achv.rarity || 'common' }}</span>
                  <span v-if="achv.unlocked_at" class="ach-admin-date">{{ achv.unlocked_at.slice(0,10) }}</span>
                </div>
              </div>
              <div v-if="selectedAchievements.includes(achv.achievement_id)" class="ach-admin-check">OK</div>
            </label>
          </div>
          <div v-else class="empty-hint">Ingen achievements låst opp ennå.</div>
          <div style="display:flex;align-items:center;gap:12px;margin-top:14px;flex-wrap:wrap;">
            <button class="btn btn-danger btn-sm" @click="deleteUserAchievement" :disabled="!selectedAchievements.length">Fjern valgte ({{ selectedAchievements.length }})</button>
            <span v-if="selectedAchievements.length" style="font-size:11px;color:var(--muted);">{{ selectedAchievements.length }} valgt</span>
          </div>
          <div v-if="achvRemoveMessage" class="form-message" :class="{ success: achvRemoveSuccess, error: !achvRemoveSuccess }">{{ achvRemoveMessage }}</div>
        </template>
      </div>
    </div>
  </section>
</template>

<script>
const SYSTEM_ROLES = ['admin', 'developer', 'producer', 'member'];
const PERMISSION_GROUPS = [
  { label: 'Management', items: [
    { key: 'access_management', label: 'Access management', description: 'Gir tilgang til management-dashboardet.' },
    { key: 'manage_users', label: 'Manage users', description: 'Kan håndtere brukere og medlemskap.' },
    { key: 'manage_roles', label: 'Manage roles', description: 'Kan opprette og slette roller.' },
  ]},
  { label: 'Content', items: [
    { key: 'publish_bedriftsmeldinger', label: 'Publish bedriftsmeldinger', description: 'Kan publisere nye bedriftsmeldinger.' },
    { key: 'edit_bedriftsmeldinger', label: 'Edit bedriftsmeldinger', description: 'Kan redigere eksisterende bedriftsmeldinger.' },
    { key: 'delete_bedriftsmeldinger', label: 'Delete bedriftsmeldinger', description: 'Kan slette bedriftsmeldinger.' },
  ]},
  { label: 'Music', items: [
    { key: 'manage_music', label: 'Manage music', description: 'Kan laste opp og styre Bangerfabrikken.' },
  ]},
];

export default {
  props: ['userRoles', 'userPermissions', 'usersList', 'userRoleUpdate', 'availableRoles', 'updateUserMessage', 'updateUserSuccess', 'selectedUserRoles', 'userRoleRemove', 'selectedUserRolesToRemove', 'rolesToRemove', 'removeRoleMessage', 'removeRoleSuccess', 'newRole', 'createRoleMessage', 'createRoleSuccess'],
  emits: ['updateUserRole', 'fetchUserRolesToRemove', 'removeSelectedRoles', 'createRole', 'deleteRole', 'update:userRoleUpdate', 'update:userRoleRemove', 'update:rolesToRemove', 'update:newRole'],
  data() {
    return {
      achvUserId: '',
      userAchievements: [],
      selectedAchievements: [],
      achvRemoveMessage: '',
      achvRemoveSuccess: false,
      selectedRoleKey: '',
      draft: { name: '', badge_color: '#5865f2' },
      roleConfigs: {},
      memberSearch: '',
      roleFeedback: '',
      roleFeedbackSuccess: true,
    };
  },
  computed: {
    permissionGroups() { return PERMISSION_GROUPS; },
    roleItems() { return this.availableRoles.map(role => ({ ...role, key: `role-${role.id}` })); },
    isDraft() { return this.selectedRoleKey === 'new'; },
    selectedRole() { return this.isDraft ? { id: null, name: this.draft.name || 'Ny rolle', badge_color: this.draft.badge_color } : this.availableRoles.find(role => `role-${role.id}` === this.selectedRoleKey) || this.availableRoles[0] || null; },
    roleConfig() {
      if (!this.selectedRole) return { permissions: [], flavor: 'default' };
      const key = this.isDraft ? 'new' : `role-${this.selectedRole.id}`;
      return this.roleConfigs[key] || this.defaultConfig(this.selectedRole);
    },
    currentColor() { return this.roleConfig.previewColor || this.roleColor(this.isDraft ? this.draft.badge_color : this.selectedRole?.badge_color); },
    members() {
      if (!this.selectedRole || this.isDraft) return [];
      return this.usersList.filter(user => Array.isArray(user.roles) && user.roles.some(role => role.id === this.selectedRole.id));
    },
    addableUsers() {
      const ids = new Set(this.members.map(user => String(user.id)));
      return this.usersList.filter(user => !ids.has(String(user.id)));
    },
    filteredAddableUsers() {
      const query = this.memberSearch.trim().toLowerCase();
      if (!query) return this.addableUsers;
      return this.addableUsers.filter(user => {
        const username = String(user.username || '').toLowerCase();
        const email = String(user.email || '').toLowerCase();
        return username.includes(query) || email.includes(query);
      });
    },
  },
  watch: {
    availableRoles: {
      immediate: true,
      handler(roles) {
        const next = {};
        roles.forEach(role => { next[`role-${role.id}`] = this.roleConfigs[`role-${role.id}`] || this.defaultConfig(role); });
        if (this.roleConfigs.new) next.new = this.roleConfigs.new;
        this.roleConfigs = next;
        if (!this.isDraft && roles.length && !roles.some(role => `role-${role.id}` === this.selectedRoleKey)) {
          this.selectedRoleKey = `role-${roles[0].id}`;
        }
      },
    },
  },
  methods: {
    roleColor(color) { return /^#[0-9a-fA-F]{6}$/.test(color || '') ? color : '#888888'; },
    rgba(hex, opacity) {
      const c = this.roleColor(hex);
      const r = parseInt(c.slice(1, 3), 16);
      const g = parseInt(c.slice(3, 5), 16);
      const b = parseInt(c.slice(5, 7), 16);
      return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    },
    badgeStyle(color) { return { background: this.rgba(color, 0.1), color: this.roleColor(color), border: `1px solid ${this.rgba(color, 0.2)}` }; },
    isSystemRole(role) { return !!role && SYSTEM_ROLES.includes((role.name || '').toLowerCase()); },
    memberCount(roleId) { return this.usersList.filter(user => Array.isArray(user.roles) && user.roles.some(role => role.id === roleId)).length; },
    roleFlavorLabel(role) { return (this.roleConfigs[role?.id ? `role-${role.id}` : 'new'] || this.defaultConfig(role)).flavor === 'music' ? 'Music dashboard' : 'Default dashboard'; },
    defaultConfig(role) {
      const name = (role?.name || '').toLowerCase();
      if (name === 'admin') return { permissions: PERMISSION_GROUPS.flatMap(group => group.items.map(item => item.key)), flavor: 'default' };
      if (name === 'developer') return { permissions: ['access_management', 'manage_users', 'manage_roles', 'publish_bedriftsmeldinger', 'edit_bedriftsmeldinger', 'delete_bedriftsmeldinger', 'manage_music'], flavor: 'default' };
      if (name === 'producer') return { permissions: ['access_management', 'publish_bedriftsmeldinger', 'edit_bedriftsmeldinger', 'manage_music'], flavor: 'music' };
      return { permissions: [], flavor: 'default' };
    },
    updateConfig(field, value) {
      const key = this.isDraft ? 'new' : `role-${this.selectedRole.id}`;
      this.roleConfigs = { ...this.roleConfigs, [key]: { ...this.roleConfig, [field]: value } };
    },
    togglePermission(permission) {
      const permissions = this.roleConfig.permissions.includes(permission)
        ? this.roleConfig.permissions.filter(item => item !== permission)
        : [...this.roleConfig.permissions, permission];
      this.updateConfig('permissions', permissions);
    },
    startDraft() {
      this.selectedRoleKey = 'new';
      this.draft = { name: '', badge_color: '#5865f2' };
      this.roleConfigs = { ...this.roleConfigs, new: { permissions: [], flavor: 'default' } };
      this.memberSearch = '';
    },
    onColor(value) { this.isDraft ? this.draft.badge_color = value : this.updateConfig('previewColor', value); },
    onHex(value) { if (/^#[0-9a-fA-F]{6}$/.test(value)) this.isDraft ? this.draft.badge_color = value : this.updateConfig('previewColor', value); },
    createDraft() {
      this.$emit('update:newRole', {
        name: this.draft.name.trim(),
        badge_color: this.roleColor(this.draft.badge_color),
        badge_icon: '',
        dashboard_flavor: this.roleConfig.flavor || 'default',
      });
      this.$emit('createRole');
      this.roleFeedback = 'Ny rolle sendes til backend med trygg standard uten permissions.';
      this.roleFeedbackSuccess = true;
    },
    async saveSelectedRole() {
      if (!this.selectedRole || this.isDraft) return;
      try {
        const apiBase = import.meta.env.VITE_API_URL;
        const authHeader = { Authorization: `Bearer ${localStorage.getItem('access_token')}` };

        const displayRes = await fetch(`${apiBase}/roles/${this.selectedRole.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            ...authHeader,
          },
          body: JSON.stringify({
            name: this.selectedRole.name,
            badge_color: this.currentColor,
            badge_icon: this.selectedRole.badge_icon || '',
            dashboard_flavor: this.roleConfig.flavor || 'default',
          }),
        });
        if (!displayRes.ok) throw new Error('Failed to update role display');
        const displayPayload = await displayRes.json();

        const permissionRes = await fetch(`${apiBase}/roles/${this.selectedRole.id}/permissions`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            ...authHeader,
          },
          body: JSON.stringify({
            permissions: this.roleConfig.permissions,
          }),
        });
        if (!permissionRes.ok) throw new Error('Failed to update role permissions');
        const permissionPayload = await permissionRes.json();
        const savedRole = permissionPayload.role || displayPayload.role;

        const roleIndex = this.availableRoles.findIndex(role => role.id === savedRole.id);
        if (roleIndex !== -1) {
          this.availableRoles.splice(roleIndex, 1, savedRole);
        }

        this.roleConfigs = {
          ...this.roleConfigs,
          [`role-${savedRole.id}`]: {
            permissions: savedRole.permissions || [],
            flavor: savedRole.dashboard_flavor || 'default',
          },
        };

        this.roleFeedback = 'Rollen ble oppdatert.';
        this.roleFeedbackSuccess = true;
      } catch (error) {
        this.roleFeedback = 'Klarte ikke å lagre rolleendringene.';
        this.roleFeedbackSuccess = false;
      }
    },
    async addMember(user) {
      if (!this.selectedRole || !user) return;
      try {
        const apiBase = import.meta.env.VITE_API_URL;
        const res = await fetch(`${apiBase}/roles/${this.selectedRole.id}/members`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
          body: JSON.stringify({ user_id: user.id }),
        });
        if (!res.ok) throw new Error('Failed to add role');
        const payload = await res.json();
        if (Array.isArray(user.roles)) {
          user.roles = payload.user?.roles || user.roles;
        }
        this.memberSearch = '';
        this.roleFeedback = 'Rolle ble lagt til brukeren.';
        this.roleFeedbackSuccess = true;
      } catch (error) {
        this.roleFeedback = 'Klarte ikke å legge til rollen på brukeren.';
        this.roleFeedbackSuccess = false;
      }
    },
    async removeMember(member) {
      if (!this.selectedRole) return;
      try {
        const apiBase = import.meta.env.VITE_API_URL;
        const res = await fetch(`${apiBase}/roles/${this.selectedRole.id}/members/${member.id}`, {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        });
        if (!res.ok) throw new Error('Failed to remove role');
        const payload = await res.json();
        if (Array.isArray(member.roles)) member.roles = payload.user?.roles || [];
        this.roleFeedback = `Rollen ${this.selectedRole.name} ble fjernet fra ${member.username || member.email}.`;
        this.roleFeedbackSuccess = true;
      } catch (e) {
        this.roleFeedback = 'Klarte ikke å fjerne rollen fra brukeren.';
        this.roleFeedbackSuccess = false;
      }
    },
    achvRarityClass(achv) { return (achv.rarity || 'common').toLowerCase(); },
    achvRarityBadge(achv) { return ({ legendary: 'b-gold', epic: 'b-purple', rare: 'b-cyan', common: 'b-muted' })[(achv.rarity || 'common').toLowerCase()] || 'b-muted'; },
    isImgUrl(src) { return typeof src === 'string' && (src.startsWith('http') || src.startsWith('data:image') || /\.(svg|png|jpe?g)$/.test(src)); },
    async fetchUserAchievements() {
      if (!this.achvUserId) { this.userAchievements = []; return; }
      try {
        const apiBase = import.meta.env.VITE_API_URL;
        const res = await fetch(`${apiBase}/user/${this.achvUserId}/achievements`, { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } });
        if (!res.ok) throw new Error('Failed to fetch achievements');
        this.userAchievements = await res.json();
        this.selectedAchievements = [];
        this.achvRemoveMessage = '';
        this.achvRemoveSuccess = false;
      } catch (e) {
        this.userAchievements = [];
        this.achvRemoveMessage = 'Klarte ikke å hente achievements.';
        this.achvRemoveSuccess = false;
      }
    },
    async deleteUserAchievement() {
      if (!this.selectedAchievements.length) return;
      try {
        const apiBase = import.meta.env.VITE_API_URL;
        for (const achvId of this.selectedAchievements) {
          await fetch(`${apiBase}/admin/delete-user-achievement`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('access_token')}` },
            body: JSON.stringify({ user_id: this.achvUserId, achievement_id: achvId }),
          });
        }
        this.achvRemoveMessage = 'Valgte achievements er fjernet.';
        this.achvRemoveSuccess = true;
        this.selectedAchievements = [];
        await this.fetchUserAchievements();
      } catch (e) {
        this.achvRemoveMessage = 'Klarte ikke å fjerne achievements.';
        this.achvRemoveSuccess = false;
      }
    },
  },
};
</script>

<style scoped>
.rp-layout,.editor-grid{display:grid;gap:16px}.rp-layout{grid-template-columns:320px minmax(0,1fr)}.editor-grid{grid-template-columns:repeat(2,minmax(0,1fr));margin-bottom:16px}
.role-list{display:flex;flex-direction:column;gap:8px}.role-item{display:flex;gap:12px;align-items:flex-start;width:100%;padding:12px;border:1px solid var(--border);border-radius:8px;background:rgba(255,255,255,.02);color:var(--text);text-align:left;cursor:pointer;transition:.18s}.role-item:hover{border-color:var(--border2);background:rgba(255,255,255,.04)}.role-item.active{border-color:rgba(0,184,208,.25);background:rgba(0,184,208,.08)}
.role-dot{width:10px;height:10px;border-radius:50%;margin-top:6px;flex-shrink:0}.role-copy{min-width:0;flex:1}.role-line{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:5px}.role-name,.editor-title,.role-badge,.tiny-pill{font-family:'Barlow Condensed',sans-serif;text-transform:uppercase}.role-name{font-size:15px;font-weight:700;letter-spacing:.04em;color:var(--text-bright)}.role-meta,.panel-subtitle,.perm-desc,.member-meta,.preview-note,.empty-hint{font-size:11px;color:var(--text-muted)}
.tiny-pill{display:inline-flex;align-items:center;justify-content:center;padding:3px 8px;border-radius:999px;font-size:9px;font-weight:700;letter-spacing:.08em;background:rgba(216,152,32,.08);color:var(--gold);border:1px solid rgba(216,152,32,.18)}.tiny-pill.muted{background:rgba(255,255,255,.03);color:var(--text-muted);border-color:var(--border2)}
.head-actions{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.editor-card{padding:16px;border:1px solid var(--border);border-radius:10px;background:rgba(255,255,255,.02)}.editor-title{font-size:14px;font-weight:800;letter-spacing:.08em;color:var(--text-bright);margin-bottom:14px}.field-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.color-row{display:grid;grid-template-columns:40px minmax(0,1fr);gap:8px;align-items:center}.color-picker{width:40px;height:40px;border:1px solid var(--border2);border-radius:8px;padding:3px;background:var(--surface2);cursor:pointer}
.preview-box{min-height:40px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:8px 10px;border:1px solid var(--border);border-radius:8px;background:rgba(255,255,255,.02)}.role-badge{display:inline-flex;align-items:center;padding:5px 11px;border-radius:4px;font-size:10px;font-weight:700;letter-spacing:.07em}.editor-note{margin-top:14px;padding:12px 13px;border:1px solid rgba(0,184,208,.12);border-radius:8px;background:rgba(0,184,208,.05);font-size:11px;color:rgba(255,255,255,.62);line-height:1.6}
.perm-group{border:1px solid var(--border);border-radius:8px;overflow:hidden}.perm-group+.perm-group{margin-top:12px}.perm-group-title{padding:10px 12px;border-bottom:1px solid var(--border);background:rgba(255,255,255,.02);font-family:'Barlow Condensed',sans-serif;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--cyan)}.perm-row{display:flex;justify-content:space-between;gap:12px;padding:12px;border-top:1px solid rgba(255,255,255,.04)}.perm-row:first-of-type{border-top:none}.perm-name,.member-name{font-size:13px;font-weight:600;color:var(--text-bright);margin-bottom:4px}.perm-row input[type=checkbox]{width:18px;height:18px;accent-color:var(--green);margin-top:2px;flex-shrink:0}
.member-toolbar{display:flex;justify-content:space-between;align-items:flex-end;gap:14px;flex-wrap:wrap;margin-bottom:14px}.member-picker-stack{display:flex;flex-direction:column;gap:10px;min-width:260px;flex:1}.member-picker-search{margin-bottom:0}.add-results{margin-bottom:14px}.member-list{display:flex;flex-direction:column;gap:8px}.member-row{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:10px 12px;border:1px solid var(--border);border-radius:8px;background:rgba(255,255,255,.02)}.member-row-add{border-color:rgba(0,184,208,.14);background:rgba(0,184,208,.04)}
.ach-admin-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:8px;margin-bottom:4px}.ach-admin-card{display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:8px;border:1px solid var(--border);background:rgba(255,255,255,.02);cursor:pointer;transition:.15s;position:relative;overflow:hidden}.ach-admin-card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:2px}.ach-admin-card.legendary{border-color:rgba(216,152,32,.2);background:rgba(216,152,32,.04)}.ach-admin-card.legendary::before{background:var(--gold)}.ach-admin-card.epic{border-color:rgba(112,80,216,.2);background:rgba(112,80,216,.04)}.ach-admin-card.epic::before{background:#9070f0}.ach-admin-card.rare{border-color:rgba(0,184,208,.18);background:rgba(0,184,208,.03)}.ach-admin-card.rare::before{background:var(--cyan)}.ach-admin-card.common::before{background:rgba(255,255,255,.15)}.ach-admin-card:hover{border-color:var(--border2);background:rgba(255,255,255,.04);transform:translateX(2px)}.ach-admin-card.is-selected{border-color:rgba(200,16,46,.3);background:rgba(200,16,46,.06)}.ach-checkbox{display:none}.ach-admin-icon{width:36px;height:36px;border-radius:7px;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:18px;background:rgba(255,255,255,.05);border:1px solid var(--border);overflow:hidden}.ach-admin-icon img{width:100%;height:100%;object-fit:contain;border-radius:6px}.ach-admin-info{flex:1;min-width:0}.ach-admin-name{font-size:13px;font-weight:600;color:var(--text-bright);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-bottom:4px}.ach-admin-meta{display:flex;align-items:center;gap:6px}.ach-admin-date{font-size:10px;color:var(--text-muted);font-family:var(--font-display);letter-spacing:.04em}.ach-admin-check{min-width:28px;height:20px;border-radius:999px;background:var(--red);color:#fff;font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;box-shadow:0 0 8px rgba(200,16,46,.4)}
.member-link{text-decoration:none;color:inherit;flex:1;min-width:0}.member-link:hover .member-name{color:var(--cyan)}
@media (max-width:1100px){.rp-layout,.editor-grid{grid-template-columns:1fr}}@media (max-width:720px){.field-grid{grid-template-columns:1fr}.member-picker{min-width:100%}.member-row{flex-direction:column;align-items:stretch}}
</style>
