<template>
  <section class="changelog-admin">
    <div class="sec-head mb24">
      <div>
        <div class="sec-title">Changelog / <em>Versjoner</em></div>
        <div class="sec-subtitle">Dokumenter endringer og nye funksjoner for hver versjon.</div>
      </div>
    </div>
    <div class="g2">
      <div class="panel">
        <div class="panel-head"><span class="panel-title">Legg til ny versjon</span></div>
        <div class="panel-body">
          <form @submit.prevent="$emit('submitChangelogEntry')">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Versjon</label>
                <input class="form-input" :value="newChangelog.version" @input="updateChangelog('version', $event.target.value)" placeholder="f.eks. 1.1.0" required />
              </div>
              <div class="form-group">
                <label class="form-label">Dato</label>
                <input class="form-input" type="date" :value="newChangelog.date" @input="updateChangelog('date', $event.target.value)" required />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Lagt til</label>
              <textarea class="form-textarea" :value="newChangelog.added" @input="updateChangelog('added', $event.target.value)" placeholder="Ny funksjonalitet, én per linje" rows="3"></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">Endret</label>
              <textarea class="form-textarea" :value="newChangelog.changed" @input="updateChangelog('changed', $event.target.value)" placeholder="Endringer, én per linje" rows="3"></textarea>
            </div>
            <button type="submit" class="btn btn-red">Legg til versjon</button>
            <div v-if="changelogMessage" class="form-message" :class="{ success: changelogSuccess, error: !changelogSuccess }" style="margin-top:10px;">{{ changelogMessage }}</div>
          </form>
        </div>
      </div>
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Versjonshistorikk</span>
          <span class="panel-meta">{{ changelogEntries.length }} versjoner</span>
        </div>
        <div class="panel-body" style="padding:0;">
          <table class="data-table">
            <thead>
              <tr><th>Versjon</th><th>Dato</th><th>Lagt til</th><th>Endret</th><th></th></tr>
            </thead>
            <tbody>
              <tr v-for="entry in changelogEntries" :key="entry.id">
                <td><span class="badge b-cyan">v{{ entry.version }}</span></td>
                <td style="color:var(--muted);font-size:12px;">{{ entry.date }}</td>
                <td style="font-size:12px;">
                  <ul style="margin:0;padding-left:14px;">
                    <li v-for="item in entry.added" :key="item">{{ item }}</li>
                  </ul>
                </td>
                <td style="font-size:12px;">
                  <ul style="margin:0;padding-left:14px;">
                    <li v-for="item in entry.changed" :key="item">{{ item }}</li>
                  </ul>
                </td>
                <td><button class="btn btn-danger btn-sm" @click="$emit('deleteChangelogEntry', entry.id)">Slett</button></td>
              </tr>
              <tr v-if="!changelogEntries.length">
                <td colspan="5" style="color:var(--muted);font-style:italic;">Ingen versjoner ennå.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  props: [
    'newChangelog',
    'changelogEntries',
    'changelogMessage',
    'changelogSuccess'
  ],
  emits: [
    'submitChangelogEntry', 
    'deleteChangelogEntry', 
    'update:newChangelog'
  ],
  methods: {
    updateChangelog(field, value) {
      const updatedChangelog = { ...this.newChangelog, [field]: value };
      this.$emit('update:newChangelog', updatedChangelog);
    }
  }
}
</script>

<style scoped>
/* Add your styles here if needed */
</style>
