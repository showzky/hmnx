<template>
  <section>
    <div class="sec-head mb24">
      <div>
        <div class="sec-title">Hen<em>delser</em></div>
        <div class="sec-subtitle">Opprett og administrer hendelser. Vises på forsiden og egne event-sider.</div>
      </div>
    </div>

    <!-- ── EXISTING EVENTS ── -->
    <div class="panel mb20">
      <div class="panel-head">
        <span class="panel-title">Eksisterende hendelser</span>
        <span class="count-badge">{{ upcomingEventsData.length }} hendelser</span>
        <div class="ev-search-wrap">
          <span class="ev-search-icon">🔍</span>
          <input
            class="search-input ev-search"
            :value="searchQuery"
            @input="$emit('update:searchQuery', $event.target.value)"
            placeholder="Søk hendelser..."
          />
        </div>
      </div>
      <div class="panel-body-flush">
        <table class="ev-table">
          <thead>
            <tr>
              <th class="ev-drag-col"></th>
              <th>Navn</th>
              <th>Dato</th>
              <th>Tid</th>
              <th class="ev-actions-col">Handlinger</th>
            </tr>
          </thead>
          <tbody ref="eventsTable">
            <tr v-for="event in filteredEvents" :key="event.id">
              <td><span class="ev-drag">⠿</span></td>
              <td>
                <div class="ev-name-cell">
                  <span class="ev-emoji">📅</span>
                  <span class="ev-name">{{ event.event_name }}</span>
                </div>
              </td>
              <td>
                <span v-if="event.event_date" class="ev-date">{{ formatDate(event.event_date) }}</span>
                <span v-else class="ev-tbd">TBD</span>
              </td>
              <td>
                <span v-if="event.event_time">{{ event.event_time }}</span>
                <span v-else class="ev-tbd">TBD</span>
              </td>
              <td>
                <div class="ev-row-actions">
                  <button class="btn btn-cyan btn-xs" @click="$emit('editEvent', event)">Rediger</button>
                  <button class="btn btn-danger btn-xs" @click="$emit('deleteEvent', event.id)">Slett</button>
                </div>
              </td>
            </tr>
            <tr v-if="!filteredEvents.length">
              <td colspan="5">
                <div class="ev-empty">
                  <div class="ev-empty-icon">📭</div>
                  <div class="ev-empty-title">Ingen hendelser</div>
                  <div class="ev-empty-sub">Ingen hendelser matchet søket ditt.</div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── CREATE FORM ── -->
    <div class="panel">
      <div class="panel-head"><span class="panel-title">Opprett ny hendelse</span></div>
      <div class="panel-body">

        <!-- Row 1: Name / Date / Time -->
        <div class="form-grid-3 mb14">
          <div class="form-group">
            <label class="form-label">Navn</label>
            <input class="form-input" :value="newEvent.event_name"
              @input="updateField('event_name', $event.target.value)" placeholder="Event tittel..." />
          </div>
          <div class="form-group">
            <label class="form-label">Dato</label>
            <input class="form-input" type="date" :value="newEvent.event_date"
              @input="updateField('event_date', $event.target.value)" />
          </div>
          <div class="form-group">
            <label class="form-label">Tid</label>
            <input class="form-input" type="time" :value="newEvent.event_time"
              @input="updateField('event_time', $event.target.value)" />
          </div>
        </div>

        <!-- Row 2: Template / Image upload -->
        <div class="form-grid-2 mb14">
          <div class="form-group">
            <label class="form-label">Template</label>
            <select class="form-select" :value="newEvent.template_name"
              @change="updateField('template_name', $event.target.value)">
              <option value="" disabled>Velg template</option>
              <option value="template1">Template 1 — Bilde-fokusert</option>
              <option value="template2">Template 2 — Tekst-fokusert</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Bilde (valgfritt)</label>
            <label class="ev-file-zone">
              <input type="file" @change="$emit('handleImageUpload', $event)" accept="image/*" class="ev-file-input" />
              <div class="ev-file-icon">🖼️</div>
              <div class="ev-file-text">Dra og slipp eller <span>velg fil</span></div>
            </label>
          </div>
        </div>

        <!-- Row 3: Description -->
        <div class="form-group mb14">
          <label class="form-label">Beskrivelse (valgfritt)</label>
          <textarea class="form-textarea" :value="newEvent.event_description"
            @input="updateField('event_description', $event.target.value)"
            placeholder="Kort beskrivelse av hendelsen..."></textarea>
        </div>

        <!-- Row 4: Checkboxes + Submit -->
        <div class="ev-form-footer">
          <div class="ev-checks">
            <label class="ev-check-row">
              <input type="checkbox" :checked="newEvent.notify_users"
                @change="updateField('notify_users', $event.target.checked)" />
              <span class="ev-check-label">Varsle alle brukere når hendelsen opprettes</span>
            </label>
            <label class="ev-check-row">
              <input type="checkbox" :checked="newEvent.show_countdown"
                @change="updateField('show_countdown', $event.target.checked)" />
              <span class="ev-check-label">Vis nedtellingstimer på event-siden</span>
            </label>
          </div>
          <button class="btn btn-red" @click="$emit('createEvent')">Opprett hendelse</button>
        </div>

        <div v-if="createEventMessage" class="ev-msg" :class="{ success: createEventSuccess, error: !createEventSuccess }">
          {{ createEventMessage }}
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  props: ['searchQuery', 'upcomingEventsData', 'newEvent', 'createEventMessage', 'createEventSuccess'],
  emits: ['deleteEvent', 'editEvent', 'handleImageUpload', 'createEvent', 'update:searchQuery', 'update:newEvent'],
  computed: {
    filteredEvents() {
      if (!this.searchQuery) return this.upcomingEventsData;
      const q = this.searchQuery.toLowerCase();
      return this.upcomingEventsData.filter(e => e.event_name?.toLowerCase().includes(q));
    }
  },
  methods: {
    formatDate(d) { return d ? new Date(d).toLocaleDateString('no-NO') : 'TBD'; },
    updateField(field, value) {
      this.$emit('update:newEvent', { ...this.newEvent, [field]: value });
    }
  }
}
</script>

<style scoped>
/* ── Search in panel-head ── */
.ev-search-wrap { position: relative; width: 220px; }
.ev-search-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); font-size: 12px; pointer-events: none; }
.ev-search { padding-left: 30px !important; font-size: 12px; }

/* ── Table ── */
.ev-table { width: 100%; border-collapse: collapse; }
.ev-table th {
  padding: 10px 14px; text-align: left; font-size: 10px;
  color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase;
  font-family: 'Barlow Condensed', sans-serif; font-weight: 700;
  border-bottom: 1px solid var(--border); background: rgba(255,255,255,0.02);
  white-space: nowrap;
}
.ev-table td {
  padding: 12px 14px; font-size: 13px; color: var(--text);
  border-bottom: 1px solid var(--border);
  font-family: 'Barlow', sans-serif; vertical-align: middle;
}
.ev-table tr:last-child td { border-bottom: none; }
.ev-table tr { transition: background 0.12s; }
.ev-table tr:hover td { background: rgba(255,255,255,0.025); }
.ev-drag-col { width: 28px; }
.ev-actions-col { width: 130px; }
.ev-drag { color: var(--muted); cursor: grab; font-size: 15px; }
.ev-drag:hover { color: var(--text); }
.ev-name-cell { display: flex; align-items: center; gap: 10px; }
.ev-emoji { font-size: 15px; flex-shrink: 0; }
.ev-name { font-weight: 500; color: var(--bright); }
.ev-date { font-size: 13px; }
.ev-tbd {
  display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 3px;
  background: rgba(216,152,32,0.1); color: var(--gold);
  border: 1px solid rgba(216,152,32,0.2);
  font-family: 'Barlow Condensed', sans-serif; font-weight: 700; letter-spacing: 0.06em;
}
.ev-row-actions { display: flex; gap: 6px; align-items: center; }

/* ── Count badge ── */
.count-badge {
  font-size: 10px; padding: 2px 8px; border-radius: 10px;
  background: rgba(255,255,255,0.06); color: var(--muted);
  font-family: 'Barlow Condensed', sans-serif; font-weight: 700; letter-spacing: 0.06em;
}

/* ── Empty state ── */
.ev-empty { padding: 28px; text-align: center; }
.ev-empty-icon { font-size: 26px; margin-bottom: 8px; }
.ev-empty-title {
  font-family: 'Barlow Condensed', sans-serif; font-size: 15px; font-weight: 800;
  color: rgba(255,255,255,0.25); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px;
}
.ev-empty-sub { font-size: 12px; color: var(--muted); font-family: 'Barlow', sans-serif; }

/* ── Form grids ── */
.form-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
.form-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.mb14 { margin-bottom: 14px; }

/* ── File upload zone ── */
.ev-file-zone {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  border: 1px dashed rgba(0,184,208,0.25); border-radius: 8px; padding: 16px;
  text-align: center; cursor: pointer; transition: all 0.18s;
  background: rgba(0,184,208,0.02); min-height: 68px;
}
.ev-file-zone:hover { border-color: rgba(0,184,208,0.45); background: rgba(0,184,208,0.06); }
.ev-file-input { display: none; }
.ev-file-icon { font-size: 20px; margin-bottom: 5px; }
.ev-file-text { font-size: 12px; color: var(--muted); font-family: 'Barlow', sans-serif; }
.ev-file-text span { color: var(--cyan); }

/* ── Form footer (checkbox + submit) ── */
.ev-form-footer {
  display: flex; align-items: flex-end; justify-content: space-between;
  flex-wrap: wrap; gap: 14px;
}
.ev-checks { display: flex; flex-direction: column; gap: 8px; }
.ev-check-row { display: flex; align-items: center; gap: 9px; cursor: pointer; }
.ev-check-row input[type="checkbox"] { width: 16px; height: 16px; border-radius: 4px; accent-color: var(--cyan); cursor: pointer; flex-shrink: 0; }
.ev-check-label { font-size: 13px; color: var(--text); font-family: 'Barlow', sans-serif; }

/* ── Message ── */
.ev-msg {
  margin-top: 14px; padding: 9px 13px; border-radius: 6px;
  font-size: 12px; font-family: 'Barlow', sans-serif;
}
.ev-msg.success { background: rgba(40,184,96,0.08); color: var(--green); border: 1px solid rgba(40,184,96,0.18); }
.ev-msg.error   { background: rgba(200,16,46,0.08); color: var(--red2); border: 1px solid rgba(200,16,46,0.18); }

/* ── Responsive ── */
@media (max-width: 700px) {
  .form-grid-3 { grid-template-columns: 1fr; }
  .form-grid-2 { grid-template-columns: 1fr; }
  .ev-search-wrap { width: 100%; }
}
</style>
