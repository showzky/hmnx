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

    <div class="preview-wrap">
      <div class="preview-head">
        <span class="preview-title">Forhåndsvisning</span>
        <span class="preview-meta">Slik ser Om oss-kortene ut offentlig</span>
      </div>

      <div class="preview-grid">
        <div
          v-for="(member, index) in previewMembers"
          :key="member.id || `preview-${index}`"
          class="team-card"
        >
          <div class="team-avatar" :class="avatarColorClass(index)">
            <img v-if="member.avatar" :src="member.avatar" :alt="member.name || 'Teammedlem'" />
            <span v-else>{{ getInitials(member.name) }}</span>
          </div>
          <div class="team-name">{{ member.name || 'Ukjent medlem' }}</div>
          <div class="team-role">{{ member.title || 'Staff' }}</div>
          <div v-if="member.bio" class="team-bio">"{{ member.bio }}"</div>
          <div class="team-badges">
            <span
              v-for="badge in getMemberBadges(member)"
              :key="badge.label"
              class="badge"
              :class="badge.cls"
            >{{ badge.label }}</span>
          </div>
        </div>

        <div v-if="!previewMembers.length" class="team-card classified empty-preview">
          <div class="team-avatar">?</div>
          <div class="team-name">Ingen teamkort ennå</div>
          <div class="team-classified-label">Legg til et medlem for å se live preview</div>
          <div class="team-badges" style="margin-top:8px;">
            <span class="badge badge-locked">Forhåndsvisning venter</span>
          </div>
        </div>
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
  computed: {
    previewMembers() {
      return (this.teamMembers || []).slice(0, 6);
    }
  },
  methods: {
    updateMemberField(index, field, value) {
      const updatedMembers = [...this.teamMembers];
      updatedMembers[index] = { 
        ...updatedMembers[index], 
        [field]: value 
      };
      this.$emit('update:teamMembers', updatedMembers);
    },
    getInitials(name) {
      if (!name) return '?';
      return name.trim().charAt(0).toUpperCase();
    },
    avatarColorClass(index) {
      const colors = ['av-red', 'av-blue', 'av-green', 'av-gold', 'av-purple', 'av-cyan'];
      return colors[index % colors.length];
    },
    getMemberBadges(member) {
      const role = (member?.title || '').toLowerCase();
      if (role.includes('admin') || role.includes('overlege') || role.includes('sjef')) {
        return [{ label: 'Admin', cls: 'badge-red' }, { label: 'Developer', cls: 'badge-cyan' }];
      }
      if (role.includes('producer')) return [{ label: 'Producer', cls: 'badge-green' }];
      if (role.includes('developer') || role.includes('dev')) return [{ label: 'Developer', cls: 'badge-cyan' }];
      if (role.includes('junior')) return [{ label: 'Junior', cls: 'badge-gold' }];
      return [{ label: member?.title || 'Staff', cls: 'badge-cyan' }];
    }
  }
}
</script>

<style scoped>
.preview-wrap {
  margin-top: 22px;
}

.preview-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.preview-title {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 11px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.preview-meta {
  font-size: 11px;
  color: var(--muted);
  font-family: 'Barlow', sans-serif;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}

.team-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 24px 20px;
  text-align: center;
  transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
}

.team-card:hover {
  border-color: var(--border2);
  transform: translateY(-3px);
  box-shadow: 0 16px 40px rgba(0,0,0,0.4);
}

.team-card.classified {
  opacity: 0.7;
}

.team-card.empty-preview:hover {
  transform: none;
}

.team-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--s2), var(--s3));
  border: 2px solid var(--border2);
  margin: 0 auto 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 22px;
  font-weight: 900;
  color: var(--muted);
  overflow: hidden;
}

.team-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.team-avatar.av-red { background: linear-gradient(135deg, var(--red), #7a0e1e); color: white; }
.team-avatar.av-blue { background: linear-gradient(135deg, #1a4a7a, #0a2a5a); color: white; }
.team-avatar.av-green { background: linear-gradient(135deg, #1a6a3a, #0a3a1a); color: white; }
.team-avatar.av-gold { background: linear-gradient(135deg, #7a5a10, #5a3800); color: white; }
.team-avatar.av-purple { background: linear-gradient(135deg, #4a2a8a, #2a0a6a); color: white; }
.team-avatar.av-cyan { background: linear-gradient(135deg, #0a5a6a, #003a4a); color: white; }

.team-name {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 18px;
  font-weight: 800;
  color: var(--bright);
  letter-spacing: 0.04em;
  margin-bottom: 6px;
}

.team-role {
  font-size: 11px;
  color: var(--cyan);
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-family: 'Barlow Condensed', sans-serif;
  margin-bottom: 8px;
}

.team-bio {
  font-size: 12px;
  color: rgba(255,255,255,0.3);
  line-height: 1.65;
  font-style: italic;
  font-family: 'Barlow', sans-serif;
  margin-bottom: 12px;
}

.team-badges {
  display: flex;
  gap: 6px;
  justify-content: center;
  flex-wrap: wrap;
}

.team-classified-label {
  font-size: 13px;
  color: rgba(255,255,255,0.2);
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 8px;
}

.badge {
  display: inline-block;
  font-size: 9px;
  padding: 3px 9px;
  border-radius: 4px;
  font-weight: 700;
  letter-spacing: 0.07em;
  font-family: 'Barlow Condensed', sans-serif;
  text-transform: uppercase;
}

.badge-cyan { background: rgba(0,184,208,0.1); color: var(--cyan); border: 1px solid rgba(0,184,208,0.2); }
.badge-red { background: rgba(200,16,46,0.12); color: var(--red2); border: 1px solid rgba(200,16,46,0.22); }
.badge-gold { background: rgba(216,152,32,0.1); color: var(--gold); border: 1px solid rgba(216,152,32,0.2); }
.badge-green { background: rgba(40,184,96,0.1); color: var(--green); border: 1px solid rgba(40,184,96,0.2); }
.badge-locked { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.2); border: 1px solid var(--border); }

@media (max-width: 900px) {
  .preview-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
