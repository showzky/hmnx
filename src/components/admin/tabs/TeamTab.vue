<template>
  <section class="team-manager">
    <div class="sec-head mb24">
      <div>
        <div class="sec-title">Team <em>Manager</em></div>
        <div class="sec-subtitle">Administrer Om oss-siden. Teamkort vises dynamisk fra disse dataene.</div>
      </div>
      <button class="btn btn-red" @click="$emit('addNewTeamMember')">+ Legg til medlem</button>
    </div>
    <div class="panel">
      <div class="panel-head">
        <span class="panel-title">Teammedlemmer</span>
        <span class="panel-meta">{{ teamMembers.length }} synlige</span>
      </div>
      <table class="data-table">
        <thead>
          <tr><th>Bruker</th><th>Tittel</th><th>Bio</th><th>Handlinger</th></tr>
        </thead>
        <tbody>
          <tr v-for="(member, index) in teamMembers" :key="member.id">
            <td>
              <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,var(--red),#7a0e1e);display:flex;align-items:center;justify-content:center;font-size:11px;color:white;font-family:'Barlow Condensed',sans-serif;font-weight:900;overflow:hidden;">
                  <img v-if="member.avatar" :src="member.avatar" style="width:100%;height:100%;object-fit:cover;" :alt="member.name" />
                  <span v-else>{{ (member.name || '?')[0].toUpperCase() }}</span>
                </div>
                <input class="form-input" style="max-width:120px;" :value="member.name"
                  @input="updateMemberField(index, 'name', $event.target.value)" placeholder="Navn" />
              </div>
            </td>
            <td>
              <input class="form-input" :value="member.title" @input="updateMemberField(index, 'title', $event.target.value)" placeholder="Tittel" />
            </td>
            <td>
              <input class="form-input" :value="member.bio" @input="updateMemberField(index, 'bio', $event.target.value)" placeholder="Bio" style="max-width:200px;" />
            </td>
            <td>
              <div style="display:flex;gap:6px;">
                <button class="btn btn-cyan btn-sm" @click="$emit('saveTeamMember', member)">Lagre</button>
                <button class="btn btn-danger btn-sm" @click="$emit('deleteTeamMember', member.id)">Slett</button>
                <button class="btn btn-ghost btn-sm" @click="$emit('triggerAvatarUpload', member.id)">Bilde</button>
              </div>
            </td>
          </tr>
          <tr v-if="!teamMembers.length">
            <td colspan="4" style="color:var(--muted);font-style:italic;">Ingen teammedlemmer ennå.</td>
          </tr>
        </tbody>
      </table>
      <div v-if="teamMessage" class="msg" :class="{ success: teamSuccess, error: !teamSuccess }" style="margin:12px 16px;">
        {{ teamMessage }}
      </div>
    </div>
  </section>
</template>

<script>
export default {
  props: [
    'teamMembers',
    'defaultAvatar',
    'teamMessage',
    'teamSuccess'
  ],
  emits: [
    'saveTeamMember', 
    'deleteTeamMember', 
    'addNewTeamMember', 
    'triggerAvatarUpload', 
    'update:teamMembers'
  ],
  methods: {
    updateMemberField(index, field, value) {
      const updatedMembers = [...this.teamMembers];
      updatedMembers[index] = { 
        ...updatedMembers[index], 
        [field]: value 
      };
      this.$emit('update:teamMembers', updatedMembers);
    }
  }
}
</script>

<style scoped>
/* Add your styles here if needed */
</style>
