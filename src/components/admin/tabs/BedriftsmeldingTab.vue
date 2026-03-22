<template>
  <section class="bedriftsmelding-admin">
    <!-- Header -->
    <div class="sec-head mb24">
      <div>
        <div class="sec-title">Bedrifts<em>meldinger</em></div>
        <div class="sec-subtitle">Kunngjøringer og nyheter fra HMN. Vises på forsiden og Bedriftsmeldinger-siden.</div>
      </div>
    </div>

    <div class="bed-grid">
      <!-- ── LEFT: EDITOR ── -->
      <div class="bed-left">

        <!-- EDITOR PANEL -->
        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">Skriv melding</span>
            <div v-if="editing" class="editing-badge">
              <span class="editing-dot"></span>Redigerer: {{ form.ref }}
            </div>
          </div>
          <div class="panel-body">

            <!-- TITLE -->
            <div class="form-group">
              <label class="form-label">Tittel</label>
              <input class="form-input" v-model="form.title" placeholder="Tittel på meldingen..." />
            </div>

            <!-- RICH TEXT -->
            <div class="form-group">
              <div class="form-label-row">
                <label class="form-label">Innhold</label>
                <div class="callout-btns">
                  <button type="button" class="callout-btn callout-btn-red" @click="insertCallout" title="Sett inn rød § callout-boks">
                    § Callout
                  </button>
                  <button type="button" class="callout-btn callout-btn-info" @click="insertInfoCallout" title="Sett inn blå info-boks">
                    ℹ Info
                  </button>
                </div>
              </div>
              <quill-editor
                ref="quillEditor"
                v-model:content="form.content"
                content-type="html"
                :toolbar="toolbarOptions"
                style="background:var(--s2);border:1px solid var(--border2);border-radius:6px;color:var(--text);"
              />
            </div>

            <!-- KATEGORI + REF -->
            <div class="form-grid" style="margin-bottom:14px;">
              <div class="form-group" style="margin-bottom:0;">
                <label class="form-label">Kategori</label>
                <select class="form-select" v-model="form.category">
                  <option value="oppdatering">Oppdatering</option>
                  <option value="kaos">Kaos</option>
                  <option value="hendelse">Hendelse</option>
                  <option value="viktig">Viktig</option>
                  <option value="thomas-relatert">Thomas-relatert</option>
                </select>
              </div>
              <div class="form-group" style="margin-bottom:0;">
                <label class="form-label">Referanse (auto)</label>
                <input class="form-input" :value="form.ref || nextRef" readonly style="opacity:0.55;" />
              </div>
            </div>

            <!-- RASK TAG CHIPS -->
            <div class="form-group">
              <label class="form-label">Rask tag</label>
              <div class="tag-row">
                <div
                  v-for="t in tags" :key="t.value"
                  class="tag-chip"
                  :class="[t.cls, { selected: form.tag === t.value }]"
                  @click="form.tag = form.tag === t.value ? null : t.value"
                >
                  <span class="tc-dot"></span>{{ t.label }}
                </div>
              </div>
            </div>

          </div>
        </div>

        <!-- PUBLISERINGSVALG -->
        <div class="panel" style="margin-top:16px;">
          <div class="panel-head"><span class="panel-title">Publiseringsvalg</span></div>
          <div class="panel-body" style="padding:14px 16px;">

            <div class="toggle-row">
              <div class="tr-info">
                <div class="tr-label">📌 Fest til forsiden</div>
                <div class="tr-sub">Vises som featured melding øverst på forsiden. Kun én kan være festet om gangen.</div>
              </div>
              <label class="hmn-toggle">
                <input type="checkbox" v-model="form.pinned" />
                <div class="toggle-track" :class="{ 'track-gold': form.pinned }"></div>
                <div class="toggle-thumb" :class="{ 'thumb-gold': form.pinned }"></div>
              </label>
            </div>

            <div class="toggle-row" style="margin-bottom:0;">
              <div class="tr-info">
                <div class="tr-label">🔔 Varsle brukere</div>
                <div class="tr-sub">Sender notifikasjon til alle registrerte pasienter.</div>
              </div>
              <label class="hmn-toggle">
                <input type="checkbox" v-model="form.notify_users" />
                <div class="toggle-track" :class="{ 'track-cyan': form.notify_users }"></div>
                <div class="toggle-thumb" :class="{ 'thumb-cyan': form.notify_users }"></div>
              </label>
            </div>

          </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div style="display:flex;gap:8px;margin-top:14px;">
          <button class="btn btn-red" @click="savemelding">
            {{ editing ? 'Oppdater melding' : 'Publiser melding' }}
          </button>
          <button v-if="editing" class="btn btn-ghost" @click="cancelEdit">Avbryt redigering</button>
        </div>

        <div v-if="statusMsg" class="status-msg" :class="{ success: statusOk, error: !statusOk }">
          {{ statusMsg }}
        </div>

      </div>

      <!-- ── RIGHT: FEED ── -->
      <div class="bed-right">

        <div class="panel">
          <div class="panel-head">
            <span class="panel-title">Publiserte meldinger</span>
            <span class="panel-meta">{{ meldinger.length }} totalt</span>
          </div>

          <!-- FILTERS -->
          <div style="padding:10px 12px 4px;">
            <div class="feed-filters">
              <div
                v-for="f in filters" :key="f.value"
                class="ff"
                :class="{ active: activeFilter === f.value }"
                @click="activeFilter = f.value"
              >{{ f.label }}</div>
            </div>
          </div>

          <!-- MELDING LIST -->
          <div class="melding-list" style="padding:0 8px 12px;">
            <div
              v-for="m in filteredMeldinger" :key="m.id"
              class="melding-card"
              :class="{ pinned: m.pinned, editing: editing && form.id === m.id }"
            >
              <div class="mc-head">
                <span v-if="m.pinned" class="mc-pin-icon">📌</span>
                <span class="mc-tag badge" :class="tagBadgeClass(m.category)">{{ categoryLabel(m.category) }}</span>
                <span class="mc-ref">{{ m.ref }}</span>
                <span class="mc-date">{{ formatDate(m.created_at) }}</span>
              </div>
              <div class="mc-body">
                <div class="mc-title">{{ m.title }}</div>
                <div class="mc-preview" v-html="stripHtml(m.content)"></div>
              </div>
              <div class="mc-foot">
                <button class="btn btn-cyan btn-sm" @click="editMelding(m)">Rediger</button>
                <button class="btn btn-sm" :class="m.pinned ? 'btn-gold' : 'btn-ghost'" @click="togglePin(m)">
                  {{ m.pinned ? 'Fjern pin' : 'Pin' }}
                </button>
                <button class="btn btn-danger btn-sm" style="margin-left:auto;" @click="deleteMelding(m.id)">Slett</button>
              </div>
            </div>

            <div v-if="filteredMeldinger.length === 0" class="feed-empty">
              Ingen meldinger funnet.
            </div>
          </div>
        </div>

        <!-- STATISTIKK -->
        <div class="panel" style="margin-top:14px;">
          <div class="panel-head"><span class="panel-title">Statistikk</span></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;">
            <div style="padding:14px 16px;border-right:1px solid var(--border);text-align:center;">
              <div class="stat-big cyan">{{ meldinger.length }}</div>
              <div class="stat-lbl">Publisert</div>
            </div>
            <div style="padding:14px 16px;text-align:center;">
              <div class="stat-big gold">{{ meldinger.filter(m => m.pinned).length }}</div>
              <div class="stat-lbl">Festet</div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </section>
</template>

<script>
import { QuillEditor } from '@vueup/vue-quill';
import '@vueup/vue-quill/dist/vue-quill.snow.css';
import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

export default {
  components: { QuillEditor },

  data() {
    return {
      meldinger: [],
      editing: false,
      form: { id: null, ref: null, title: '', content: '', category: 'oppdatering', tag: null, pinned: false, notify_users: false },
      statusMsg: '',
      statusOk: true,
      activeFilter: 'alle',
      toolbarOptions: [
        ['bold', 'italic', 'underline'],
        [{ header: [1, 2, false] }],
        [{ list: 'ordered' }, { list: 'bullet' }],
        ['link'],
        ['clean'],
      ],
      tags: [
        { value: 'kaos',           label: 'Kaos',           cls: 't-kaos' },
        { value: 'hendelse',       label: 'Hendelse',       cls: 't-hendelse' },
        { value: 'oppdatering',    label: 'Oppdatering',    cls: 't-oppdatering' },
        { value: 'viktig',         label: 'Viktig',         cls: 't-viktig' },
        { value: 'thomas-relatert',label: 'Thomas-relatert',cls: 't-thomas' },
      ],
      filters: [
        { value: 'alle',           label: 'Alle' },
        { value: 'festet',         label: 'Festet' },
        { value: 'oppdatering',    label: 'Oppdatering' },
        { value: 'kaos',           label: 'Kaos' },
        { value: 'thomas-relatert',label: 'Thomas' },
      ],
    };
  },

  computed: {
    nextRef() {
      return `HMN-MSG-${String(this.meldinger.length + 1).padStart(3, '0')}`;
    },
    filteredMeldinger() {
      if (this.activeFilter === 'alle') return this.meldinger;
      if (this.activeFilter === 'festet') return this.meldinger.filter(m => m.pinned);
      return this.meldinger.filter(m => m.category === this.activeFilter || m.tag === this.activeFilter);
    },
  },

  methods: {
    authHeader() {
      const auth = useAuthStore();
      return { Authorization: `Bearer ${auth.token}` };
    },

    insertCallout() {
      this._insertCalloutHtml('⚠️', 'Viktig');
    },

    insertInfoCallout() {
      this._insertCalloutHtml('ℹ️', 'Info');
    },

    _insertCalloutHtml(icon, label) {
      const quill = this.$refs.quillEditor?.getQuill?.();
      if (!quill) return;
      const range = quill.getSelection(true);
      const selectedText = range?.length ? quill.getText(range.index, range.length) : '';
      const html = `<p>${icon} <strong>${label}:</strong> ${selectedText || 'Skriv tekst her...'}</p><p><br></p>`;
      if (range?.length) {
        quill.deleteText(range.index, range.length);
        quill.clipboard.dangerouslyPasteHTML(range.index, html);
      } else {
        const idx = range ? range.index : quill.getLength();
        quill.clipboard.dangerouslyPasteHTML(idx, html);
      }
    },

    async fetchMeldinger() {
      try {
        const res = await axios.get(`${import.meta.env.VITE_API_URL}/bedriftsmeldinger`);
        this.meldinger = Array.isArray(res.data) ? res.data : [];
      } catch (err) {
        console.error('Failed to fetch bedriftsmeldinger:', err);
      }
    },

    async savemelding() {
      if (!this.form.title.trim() || !this.form.content) {
        this.showStatus('Tittel og innhold er påkrevd.', false);
        return;
      }
      try {
        const payload = { ...this.form };
        if (this.editing) {
          await axios.put(`${import.meta.env.VITE_API_URL}/bedriftsmeldinger/${this.form.id}`, payload, { headers: this.authHeader() });
          this.showStatus('Melding oppdatert!', true);
        } else {
          await axios.post(`${import.meta.env.VITE_API_URL}/bedriftsmeldinger`, payload, { headers: this.authHeader() });
          this.showStatus('Melding publisert!', true);
        }
        await this.fetchMeldinger();
        this.resetForm();
      } catch (err) {
        this.showStatus('Noe gikk galt. Prøv igjen.', false);
        console.error(err);
      }
    },

    editMelding(m) {
      this.form = { ...m };
      this.editing = true;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    cancelEdit() {
      this.resetForm();
    },

    async deleteMelding(id) {
      if (!confirm('Slett denne meldingen?')) return;
      try {
        await axios.delete(`${import.meta.env.VITE_API_URL}/bedriftsmeldinger/${id}`, { headers: this.authHeader() });
        await this.fetchMeldinger();
      } catch (err) {
        console.error('Delete failed:', err);
      }
    },

    async togglePin(m) {
      try {
        await axios.put(
          `${import.meta.env.VITE_API_URL}/bedriftsmeldinger/${m.id}`,
          { ...m, pinned: !m.pinned },
          { headers: this.authHeader() }
        );
        await this.fetchMeldinger();
      } catch (err) {
        console.error('Toggle pin failed:', err);
      }
    },

    resetForm() {
      this.form = { id: null, ref: null, title: '', content: '', category: 'oppdatering', tag: null, pinned: false, notify_users: false };
      this.editing = false;
    },

    showStatus(msg, ok) {
      this.statusMsg = msg;
      this.statusOk = ok;
      setTimeout(() => { this.statusMsg = ''; }, 3500);
    },

    tagBadgeClass(cat) {
      const map = {
        oppdatering: 'b-green',
        kaos: 'b-red',
        hendelse: 'b-cyan',
        viktig: 'b-gold',
        'thomas-relatert': 'b-purple',
      };
      return map[cat] || 'b-muted';
    },

    categoryLabel(cat) {
      const map = {
        oppdatering: 'Oppdatering',
        kaos: 'Kaos',
        hendelse: 'Hendelse',
        viktig: 'Viktig',
        'thomas-relatert': 'Thomas-relatert',
      };
      return map[cat] || cat;
    },

    formatDate(iso) {
      if (!iso) return '';
      const d = new Date(iso);
      return d.toLocaleDateString('nb-NO', { day: 'numeric', month: 'long', year: 'numeric' });
    },

    stripHtml(html) {
      if (!html) return '';
      const tmp = document.createElement('div');
      tmp.innerHTML = html;
      const text = tmp.textContent || tmp.innerText || '';
      return text.length > 80 ? text.slice(0, 80) + '…' : text;
    },
  },

  mounted() {
    this.fetchMeldinger();
  },
};
</script>

<style scoped>
/* Label row with callout buttons */
.form-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}
.form-label-row .form-label {
  margin-bottom: 0;
}
.callout-btns {
  display: flex;
  gap: 6px;
}
.callout-btn {
  font-size: 11px;
  font-family: var(--font-display);
  font-weight: 700;
  letter-spacing: 0.06em;
  border-radius: 4px;
  padding: 3px 10px;
  cursor: pointer;
  transition: all 0.15s;
  text-transform: uppercase;
}
.callout-btn-red {
  color: var(--red2);
  background: rgba(200,16,46,0.08);
  border: 1px solid rgba(200,16,46,0.2);
}
.callout-btn-red:hover {
  background: rgba(200,16,46,0.14);
  border-color: rgba(200,16,46,0.35);
}
.callout-btn-info {
  color: var(--cyan);
  background: rgba(0,184,208,0.07);
  border: 1px solid rgba(0,184,208,0.2);
}
.callout-btn-info:hover {
  background: rgba(0,184,208,0.13);
  border-color: rgba(0,184,208,0.35);
}

/* Layout */
.bed-grid {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 18px;
  align-items: start;
}
.bed-left { display: flex; flex-direction: column; }
.bed-right { display: flex; flex-direction: column; }

/* Editing badge */
.editing-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px; border-radius: 4px;
  background: rgba(0,184,208,0.1); border: 1px solid rgba(0,184,208,0.22);
  color: var(--cyan); font-size: 10px;
  font-family: 'Barlow Condensed', sans-serif; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
}
.editing-dot {
  width: 6px; height: 6px; background: var(--cyan); border-radius: 50%;
  box-shadow: 0 0 6px var(--cyan); animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

/* Tag chips */
.tag-row { display: flex; gap: 7px; flex-wrap: wrap; }
.tag-chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 12px; border-radius: 6px; font-size: 11px; font-weight: 600;
  font-family: 'Barlow Condensed', sans-serif; letter-spacing: 0.06em; text-transform: uppercase;
  cursor: pointer; border: 1px solid; transition: all 0.15s; user-select: none;
}
.tag-chip:hover { transform: translateY(-1px); }
.tag-chip.selected { box-shadow: 0 0 0 2px currentColor; }
.tc-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.t-kaos         { background:rgba(200,16,46,0.1);  color:var(--red2);  border-color:rgba(200,16,46,0.25); }
.t-kaos .tc-dot         { background:var(--red2); }
.t-hendelse     { background:rgba(0,184,208,0.1);  color:var(--cyan);  border-color:rgba(0,184,208,0.25); }
.t-hendelse .tc-dot     { background:var(--cyan); }
.t-oppdatering  { background:rgba(40,184,96,0.1);  color:var(--green); border-color:rgba(40,184,96,0.25); }
.t-oppdatering .tc-dot  { background:var(--green); }
.t-viktig       { background:rgba(216,152,32,0.1); color:var(--gold);  border-color:rgba(216,152,32,0.25); }
.t-viktig .tc-dot       { background:var(--gold); }
.t-thomas       { background:rgba(112,80,216,0.1); color:#9070f0;      border-color:rgba(112,80,216,0.25); }
.t-thomas .tc-dot       { background:#9070f0; }

/* Toggle */
.toggle-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 14px; background: rgba(255,255,255,0.02);
  border: 1px solid var(--border); border-radius: 7px; margin-bottom: 14px;
}
.tr-info { flex: 1; }
.tr-label { font-size: 13px; color: var(--bright); font-family: 'Barlow', sans-serif; font-weight: 500; margin-bottom: 2px; }
.tr-sub { font-size: 11px; color: var(--muted); font-family: 'Barlow', sans-serif; }
.hmn-toggle { position: relative; width: 40px; height: 22px; cursor: pointer; flex-shrink: 0; }
.hmn-toggle input { opacity: 0; width: 0; height: 0; position: absolute; }
.toggle-track {
  position: absolute; inset: 0; border-radius: 11px;
  background: rgba(255,255,255,0.08); border: 1px solid var(--border2); transition: all 0.2s;
}
.toggle-track.track-gold { background: rgba(216,152,32,0.3); border-color: rgba(216,152,32,0.5); }
.toggle-track.track-cyan { background: rgba(0,184,208,0.25); border-color: rgba(0,184,208,0.45); }
.toggle-thumb {
  position: absolute; top: 3px; left: 3px;
  width: 14px; height: 14px; border-radius: 50%; background: var(--muted); transition: all 0.2s; pointer-events: none;
}
.toggle-thumb.thumb-gold { left: 21px; background: var(--gold); box-shadow: 0 0 6px rgba(216,152,32,0.5); }
.toggle-thumb.thumb-cyan { left: 21px; background: var(--cyan); box-shadow: 0 0 6px rgba(0,184,208,0.5); }

/* Feed filters */
.feed-filters { display: flex; gap: 6px; flex-wrap: wrap; }
.ff {
  padding: 5px 12px; border-radius: 5px; font-size: 11px; font-weight: 600;
  font-family: 'Barlow Condensed', sans-serif; letter-spacing: 0.06em; text-transform: uppercase;
  cursor: pointer; border: 1px solid var(--border); background: rgba(255,255,255,0.03); color: var(--muted); transition: all 0.15s;
}
.ff:hover { color: var(--text); border-color: var(--border2); }
.ff.active { background: rgba(0,184,208,0.08); border-color: rgba(0,184,208,0.2); color: var(--cyan); }

/* Melding cards */
.melding-list { display: flex; flex-direction: column; gap: 8px; }
.melding-card {
  background: rgba(255,255,255,0.025); border: 1px solid var(--border);
  border-radius: 10px; overflow: hidden; transition: all 0.2s;
}
.melding-card:hover { border-color: var(--border2); }
.melding-card.pinned { border-color: rgba(216,152,32,0.3); background: rgba(216,152,32,0.04); }
.melding-card.editing { border-color: rgba(0,184,208,0.3); background: rgba(0,184,208,0.04); }
.mc-head {
  padding: 10px 14px; display: flex; align-items: center; gap: 8px;
  border-bottom: 1px solid var(--border);
}
.mc-pin-icon { font-size: 12px; color: var(--gold); flex-shrink: 0; }
.mc-tag { flex-shrink: 0; }
.mc-ref { font-size: 10px; color: var(--muted); font-family: 'Barlow Condensed', sans-serif; letter-spacing: 0.06em; flex: 1; }
.mc-date { font-size: 10px; color: var(--muted); flex-shrink: 0; }
.mc-body { padding: 10px 14px; }
.mc-title { font-size: 14px; font-weight: 600; color: var(--bright); font-family: 'Barlow', sans-serif; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mc-preview { font-size: 12px; color: rgba(255,255,255,0.35); font-family: 'Barlow', sans-serif; line-height: 1.55; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mc-foot {
  padding: 8px 14px; border-top: 1px solid var(--border);
  background: rgba(0,0,0,0.15); display: flex; align-items: center; gap: 6px;
}
.feed-empty { padding: 32px; text-align: center; color: var(--muted); font-size: 13px; font-family: 'Barlow', sans-serif; font-style: italic; }

/* Stat */
.stat-big { font-family: 'Barlow Condensed', sans-serif; font-size: 24px; font-weight: 900; line-height: 1; }
.stat-big.cyan { color: var(--cyan); }
.stat-big.gold { color: var(--gold); }
.stat-lbl { font-size: 10px; color: var(--muted); margin-top: 3px; font-family: 'Barlow Condensed', sans-serif; text-transform: uppercase; letter-spacing: 0.07em; }

/* Status message */
.status-msg { margin-top: 10px; padding: 8px 12px; border-radius: 6px; font-size: 13px; font-family: 'Barlow', sans-serif; }
.status-msg.success { background: rgba(40,184,96,0.1); color: var(--green); border: 1px solid rgba(40,184,96,0.2); }
.status-msg.error { background: rgba(200,16,46,0.1); color: var(--red2); border: 1px solid rgba(200,16,46,0.2); }

/* Quill dark overrides */
:deep(.ql-toolbar) { background: var(--s3); border-color: var(--border2); border-radius: 6px 6px 0 0; }
:deep(.ql-toolbar .ql-stroke) { stroke: var(--muted); }
:deep(.ql-toolbar .ql-fill) { fill: var(--muted); }
:deep(.ql-toolbar .ql-picker) { color: var(--muted); }
:deep(.ql-container) { border-color: var(--border2); font-family: inherit; font-size: 14px; border-radius: 0 0 6px 6px; }
:deep(.ql-editor) { min-height: 140px; color: var(--text); background: var(--s2); }
</style>
