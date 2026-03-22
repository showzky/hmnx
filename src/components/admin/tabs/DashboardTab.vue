<template>
  <section>
    <div class="sec-head mb24">
      <div>
        <div class="sec-title">Over<em>sikt</em></div>
        <div class="sec-subtitle">Velkommen tilbake, {{ displayName }}. Systemet er nominelt kaotisk.</div>
      </div>
    </div>
    <div class="stat-row mb24">
      <div class="stat-card c1">
        <div class="sc-label">Totale pasienter</div>
        <div class="sc-val cyan">{{ totalUsers }}</div>
        <div class="sc-sub">alle aktive</div>
      </div>
      <div class="stat-card c2">
        <div class="sc-label">Online nå</div>
        <div class="sc-val green">{{ onlineNow }}</div>
        <div class="sc-sub">siste 15 min</div>
      </div>
      <div class="stat-card c3">
        <div class="sc-label">Kommende hendelser</div>
        <div class="sc-val gold">{{ upcomingEventsData.length }}</div>
        <div class="sc-sub">neste: {{ nextEventName }}</div>
      </div>
      <div class="stat-card c4">
        <div class="sc-label">Krenkethet snitt</div>
        <div class="sc-val red">–</div>
        <div class="sc-sub">stigende trend</div>
      </div>
    </div>
    <div class="g2">
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Siste aktivitet</span>
          <span class="panel-meta">live</span>
        </div>
        <div class="panel-body">
          <template v-if="activityItems.length">
            <div class="act-item" v-for="item in activityItems" :key="item.text">
              <div class="act-dot" style="background:var(--cyan);"></div>
              <span class="act-text">{{ item.text }}</span>
              <span class="act-time">{{ item.time }}</span>
            </div>
          </template>
          <p v-else style="font-size:13px;color:var(--muted);">Ingen aktivitet ennå.</p>
        </div>
      </div>
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Kommende hendelser</span>
          <span class="panel-meta">{{ upcomingEventsData.length }} aktive</span>
        </div>
        <div class="panel-body" style="padding:0;">
          <table class="data-table">
            <thead><tr><th>Hendelse</th><th>Dato</th><th>Tid</th></tr></thead>
            <tbody>
              <tr v-for="event in upcomingEventsData" :key="event.id">
                <td>{{ event.event_name }}</td>
                <td>{{ formatDate(event.event_date) }}</td>
                <td>{{ event.event_time }}</td>
              </tr>
              <tr v-if="!upcomingEventsData.length">
                <td colspan="3" style="color:var(--muted);font-style:italic;">Ingen hendelser planlagt.</td>
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
  props: {
    upcomingEventsData: { type: Array, default: () => [] },
    widgets: { type: Array, default: () => [] },
    displayName: { type: String, default: '' },
    totalUsers: { type: Number, default: 0 }
  },
  computed: {
    activityItems() {
      const w = this.widgets.find(w => w.id === 'latest-activity');
      return w ? w.activityItems : [];
    },
    onlineNow() {
      return Math.min(this.totalUsers || 0, Math.max(0, this.activityItems.length || 0, 3));
    },
    nextEventName() {
      return this.upcomingEventsData[0]?.event_name || 'ingen';
    }
  },
  methods: {
    formatDate(d) { return d ? new Date(d).toLocaleDateString('no-NO') : 'TBD'; }
  }
}
</script>

<style scoped>
/* DashboardTab styles handled by admin.css */
</style>
