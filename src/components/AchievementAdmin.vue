<template>
  <div class="ach-grid">

    <!-- ── LEFT: Creator ── -->
    <div>
      <!-- LIVE PREVIEW -->
      <div class="panel mb14">
        <div class="panel-head"><span class="panel-title">Forhåndsvisning</span></div>
        <div class="panel-body" style="padding:14px 18px;">
          <div class="ach-preview" :style="{ '--pglow': rarCfg.glow }">
            <div class="ap-icon" :style="{ background: rarCfg.bg }">
              <img v-if="svgPreviewUrl" :src="svgPreviewUrl" class="icon-img" />
              <span v-else style="font-size:24px;">{{ form.icon || '🏆' }}</span>
              <span class="ap-ring" :style="{ borderColor: rarCfg.color }"></span>
            </div>
            <div class="ap-info">
              <div class="ap-rar" :style="{ color: rarCfg.color }">{{ rarCfg.label }}</div>
              <div class="ap-title">{{ form.title || 'Achievement navn' }}</div>
              <div class="ap-desc">{{ form.description || 'Beskrivelse...' }}</div>
              <div class="ap-cond">{{ previewCondText }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- FORM -->
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">{{ form.id ? 'Rediger achievement' : 'Opprett / Rediger achievement' }}</span>
        </div>
        <div class="panel-body">

          <div class="fg">
            <label class="fl">Tittel</label>
            <input class="fi" v-model="form.title" placeholder="Achievement navn..." />
          </div>

          <div class="fg">
            <label class="fl">Beskrivelse</label>
            <textarea class="fta" v-model="form.description" rows="2" placeholder="Beskrivelse..."></textarea>
          </div>

          <div class="fg2 mb14">
            <div class="fg" style="margin-bottom:0;">
              <label class="fl">Badge-ikon (emoji · brukes hvis ingen SVG er lastet opp)</label>
              <input class="fi" v-model="form.icon" placeholder="🏆" style="font-size:18px;" />
            </div>
            <div class="fg" style="margin-bottom:0;">
              <label class="fl">Glow-farge</label>
              <div class="glow-row">
                <div class="glow-dot" :style="glowDotStyle"></div>
                <input class="fi" v-model="form.glow_color" placeholder="#d89820" style="flex:1;" />
              </div>
            </div>
          </div>

          <div class="fg">
            <label class="fl">Raritet</label>
            <div class="rarity-grid">
              <div v-for="r in RARITIES" :key="r.key"
                   class="rarity-chip" :class="[r.cls, { selected: form.rarity === r.key }]"
                   @click="form.rarity = r.key">
                <div class="rn">{{ r.label }}</div>
                <div class="rs">{{ r.sub }}</div>
              </div>
            </div>
          </div>

          <div class="fg">
            <label class="fl">Betingelse</label>
            <select class="fs" v-model="form.condition_type">
              <option value="">Custom / Manuell</option>
              <option value="login_streak">Login Streak</option>
              <option value="active_hours">Active Hours</option>
              <option value="daily_claims">Daily Reward Claims</option>
            </select>
          </div>

          <div class="cond-box mb14">
            <div class="cond-icon">{{ condCfg.icon }}</div>
            <div class="cond-info">
              <div class="cond-label">{{ condCfg.label }}</div>
              <div class="cond-desc">{{ condCfg.desc }}</div>
            </div>
            <div v-if="form.condition_type" class="cond-right">
              <input class="cond-num" type="number" v-model.number="form.condition_value" min="1" />
              <span class="cond-unit">{{ condCfg.unit }}</span>
            </div>
          </div>

          <div class="fg">
            <label class="fl">SVG-ikon (valgfritt, overstyrer emoji)</label>
            <div class="img-upload" :class="{ 'has-file': svgPreviewUrl }" @click="$refs.fileInput.click()">
              <input ref="fileInput" class="iu-file-input" type="file" accept=".svg,.png" @change="handleFileUpload" />
              <div v-if="!svgPreviewUrl" class="iu-empty">
                <div class="iu-icon">🎨</div>
                <div class="iu-text">Dra og slipp eller <span>velg fil</span></div>
                <div class="iu-format-badges">
                  <span class="iu-fmt iu-fmt-svg">SVG anbefalt</span>
                  <span class="iu-fmt iu-fmt-png">PNG støttes</span>
                </div>
              </div>
              <div v-else class="iu-preview" @click.stop>
                <img class="iu-preview-img" :src="svgPreviewUrl" alt="Preview" />
                <div class="iu-preview-name">{{ svgFileName }}</div>
                <span class="iu-svg-badge" :style="svgBadgeStyle">{{ svgFileType }}</span>
                <div class="iu-preview-remove" @click.stop="clearFile">Fjern fil</div>
              </div>
            </div>
          </div>

          <div class="btn-row">
            <button class="btn btn-red" @click="submitForm">{{ form.id ? 'Oppdater achievement' : 'Opprett achievement' }}</button>
            <button class="btn btn-ghost" @click="resetForm">Nullstill</button>
          </div>

        </div>
      </div>
    </div>

    <!-- ── RIGHT: Give + List ── -->
    <div>

      <!-- GI TIL BRUKER -->
      <div class="panel mb14">
        <div class="panel-head">
          <span class="panel-title">Gi til bruker</span>
          <span class="panel-meta">manuell tildeling</span>
        </div>
        <div class="panel-body">
          <div class="give-row">
            <div class="fg">
              <label class="fl">Bruker</label>
              <select class="fs" v-model="giveUserId">
                <option disabled value="">Velg bruker</option>
                <option v-for="u in users" :key="u.id" :value="u.id">{{ u.username }}</option>
              </select>
            </div>
            <div class="fg">
              <label class="fl">Achievement</label>
              <select class="fs" v-model="giveAchId">
                <option disabled value="">Velg achievement</option>
                <option v-for="a in achievements" :key="a.id" :value="a.id">{{ a.title }}</option>
              </select>
            </div>
            <button class="btn btn-cyan btn-sm" style="flex-shrink:0;align-self:flex-end;" @click="giveAchievement">Gi</button>
          </div>
        </div>
      </div>

      <!-- ALLE ACHIEVEMENTS -->
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Alle achievements</span>
          <span class="panel-meta">{{ achievements.length }} opprettet</span>
        </div>
        <div style="padding:12px 14px 6px;">
          <input class="search-inp" v-model="searchQuery" placeholder="Søk achievements..." />
          <div class="ach-filters">
            <div v-for="f in FILTERS" :key="f.key"
                 class="af" :class="{ active: filterRarity === f.key }"
                 @click="filterRarity = f.key">{{ f.label }}</div>
          </div>
        </div>
        <div class="ach-list" style="padding:0 8px 12px;">
          <div v-for="ach in filteredAchievements" :key="ach.id"
               class="ach-card" :class="rarCardClass(ach.rarity)">
            <div class="acc-inner">
              <div class="acc-icon">
                <img v-if="ach.icon && (ach.icon.startsWith('http') || ach.icon.startsWith('data:'))"
                     :src="ach.icon" style="width:100%;height:100%;object-fit:contain;border-radius:7px;" />
                <span v-else>{{ ach.icon }}</span>
              </div>
              <div class="acc-info">
                <div class="acc-top">
                  <span class="acc-title">{{ ach.title }}</span>
                  <span class="rtag" :class="rarTagClass(ach.rarity)">{{ ach.rarity }}</span>
                </div>
                <div class="acc-desc">{{ ach.description }}</div>
                <div class="acc-cond">
                  <span class="cdot" :style="{ background: condDotColor(ach.condition_type) }"></span>
                  {{ condLabel(ach) }}
                </div>
              </div>
              <div class="acc-unlocked">{{ ach.unlocked_count || 0 }} / {{ users.length }}</div>
              <div class="acc-actions">
                <button class="btn btn-cyan btn-xs" @click="startEdit(ach)">Rediger</button>
                <button class="btn btn-danger btn-xs" @click="deleteAchievement(ach.id)">Slett</button>
              </div>
            </div>
          </div>
          <div v-if="!filteredAchievements.length" class="empty-state">
            Ingen achievements funnet.
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import axios from '@/axios';

const RARITIES = [
  { key: 'common',    label: 'Common',    sub: 'Vanlig',     cls: 'rc', color: 'rgba(255,255,255,0.4)', bg: 'rgba(255,255,255,0.05)', glow: 'rgba(255,255,255,0.04)' },
  { key: 'rare',      label: 'Rare',      sub: 'Sjelden',    cls: 'rr', color: '#00b8d0',              bg: 'rgba(0,184,208,0.1)',    glow: 'rgba(0,184,208,0.07)' },
  { key: 'epic',      label: 'Epic',      sub: 'Episk',      cls: 're', color: '#9070f0',              bg: 'rgba(112,80,216,0.12)',  glow: 'rgba(112,80,216,0.08)' },
  { key: 'legendary', label: 'Legendary', sub: 'Legendarisk', cls: 'rl', color: '#d89820',             bg: 'rgba(216,152,32,0.12)', glow: 'rgba(216,152,32,0.08)' },
];

const CONDITIONS = {
  login_streak: { icon: '🔥', label: 'Login Streak',       desc: 'Låses opp automatisk når brukeren logger inn X dager på rad.', unit: 'dager' },
  active_hours: { icon: '⏱️', label: 'Active Hours',        desc: 'Låses opp når brukeren har vært aktiv i X timer totalt.',       unit: 'timer' },
  daily_claims: { icon: '🎁', label: 'Daily Reward Claims', desc: 'Låses opp etter X daglige belønninger er hentet.',              unit: 'claims' },
  '':           { icon: '✋', label: 'Custom / Manuell',    desc: 'Gis manuelt av admin — ingen automatisk trigger.',              unit: '' },
};

const FILTERS = [
  { key: 'all', label: 'Alle' },
  { key: 'legendary', label: 'Legendary' },
  { key: 'epic', label: 'Epic' },
  { key: 'rare', label: 'Rare' },
  { key: 'common', label: 'Common' },
  { key: 'custom', label: 'Manuell' },
];

function emptyForm() {
  return { id: null, title: '', description: '', icon: '🏆', condition_type: '', condition_value: 1, rarity: 'legendary', glow_color: '#d89820' };
}

export default {
  name: 'AchievementAdmin',
  data() {
    return {
      achievements: [],
      users: [],
      form: emptyForm(),
      svgPreviewUrl: null,
      svgFileName: '',
      svgFileType: 'SVG',
      giveUserId: '',
      giveAchId: '',
      searchQuery: '',
      filterRarity: 'all',
      RARITIES,
      FILTERS,
    };
  },

  computed: {
    rarCfg() {
      return RARITIES.find(r => r.key === this.form.rarity) || RARITIES[0];
    },
    condCfg() {
      return CONDITIONS[this.form.condition_type] || CONDITIONS[''];
    },
    previewCondText() {
      if (!this.form.condition_type) return '✋ Manuell tildeling';
      const c = this.condCfg;
      const v = this.form.condition_value;
      return `⚡ ${c.label}${v ? ` · ${v} ${c.unit}` : ''}`;
    },
    glowDotStyle() {
      const c = this.form.glow_color || '#d89820';
      return { background: c, boxShadow: `0 0 12px ${c}`, width: '32px', height: '32px', borderRadius: '50%', flexShrink: 0, border: '2px solid rgba(255,255,255,0.1)' };
    },
    svgBadgeStyle() {
      return this.svgFileType === 'SVG'
        ? { background: 'rgba(0,184,208,0.12)', color: 'var(--hmn-cyan)', borderColor: 'rgba(0,184,208,0.22)' }
        : { background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.4)', borderColor: 'rgba(255,255,255,0.11)' };
    },
    filteredAchievements() {
      return this.achievements.filter(a => {
        const q = this.searchQuery.toLowerCase();
        const matchQ = !q || a.title?.toLowerCase().includes(q) || a.description?.toLowerCase().includes(q);
        let matchR = true;
        if (this.filterRarity !== 'all') {
          if (this.filterRarity === 'custom') matchR = !a.condition_type;
          else matchR = a.rarity === this.filterRarity;
        }
        return matchQ && matchR;
      });
    },
  },

  methods: {
    async fetchAchievements() {
      const { data } = await axios.get('/all-achievements');
      this.achievements = data;
    },
    async fetchUsers() {
      const { data } = await axios.get('/users');
      this.users = data.users || [];
    },

    rarCardClass(rarity) {
      return { legendary: 'al', epic: 'ae', rare: 'ar', common: 'ac-c' }[rarity] || 'ac-c';
    },
    rarTagClass(rarity) {
      return { legendary: 'rtl', epic: 'rte', rare: 'rtr', common: 'rtc' }[rarity] || 'rtc';
    },
    condDotColor(type) {
      return { login_streak: 'var(--hmn-cyan)', active_hours: 'var(--hmn-gold)', daily_claims: 'var(--hmn-gold)', '': 'var(--hmn-purple)' }[type || ''] || 'rgba(255,255,255,0.3)';
    },
    condLabel(ach) {
      const c = CONDITIONS[ach.condition_type] || CONDITIONS[''];
      if (!ach.condition_type) return 'Custom · Manuell';
      return `${c.label} · ${ach.condition_value} ${c.unit}`;
    },

    startEdit(ach) {
      this.form = {
        id: ach.id,
        title: ach.title,
        description: ach.description,
        icon: ach.icon || '🏆',
        condition_type: ach.condition_type || '',
        condition_value: ach.condition_value || 1,
        rarity: ach.rarity || 'common',
        glow_color: ach.glow_color || '#d89820',
      };
      if (ach.icon && (ach.icon.startsWith('http') || ach.icon.startsWith('data:'))) {
        this.svgPreviewUrl = ach.icon;
        this.svgFileName = ach.icon.split('/').pop();
        this.svgFileType = ach.icon.endsWith('.svg') ? 'SVG' : 'PNG';
      } else {
        this.svgPreviewUrl = null;
        this.svgFileName = '';
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    resetForm() {
      this.form = emptyForm();
      this.svgPreviewUrl = null;
      this.svgFileName = '';
    },

    async submitForm() {
      if (!this.form.title || !this.form.description) return alert('Tittel og beskrivelse er påkrevd.');
      const payload = {
        title: this.form.title,
        description: this.form.description,
        icon: this.form.icon,
        condition_type: this.form.condition_type || null,
        condition_value: this.form.condition_type ? this.form.condition_value : null,
        rarity: this.form.rarity,
        glow_color: this.form.glow_color,
      };
      try {
        if (this.form.id) {
          await axios.put(`/achievements/${this.form.id}`, payload);
        } else {
          await axios.post('/achievements', payload);
        }
        this.resetForm();
        await this.fetchAchievements();
      } catch (e) {
        alert('Feil: ' + (e.response?.data?.msg || e.message));
      }
    },

    async deleteAchievement(id) {
      if (!confirm('Slett dette achievementet?')) return;
      await axios.delete(`/achievements/${id}`);
      await this.fetchAchievements();
    },

    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      const isSvg = file.name.toLowerCase().endsWith('.svg') || file.type === 'image/svg+xml';
      const isPng = file.name.toLowerCase().endsWith('.png') || file.type === 'image/png';
      if (!isSvg && !isPng) { alert('Kun SVG og PNG støttes.'); return; }

      // Local preview immediately
      const reader = new FileReader();
      reader.onload = e => {
        this.svgPreviewUrl = e.target.result;
        this.svgFileName = file.name;
        this.svgFileType = isSvg ? 'SVG' : 'PNG';
      };
      reader.readAsDataURL(file);

      // Upload to server
      try {
        const fd = new FormData();
        fd.append('svg_file', file);
        const { data } = await axios.post('/upload-svg', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
        this.form.icon = data.url;
        this.svgPreviewUrl = data.url;
      } catch (e) {
        alert('Opplasting feilet: ' + (e.response?.data?.msg || e.message));
      }
    },

    clearFile() {
      this.svgPreviewUrl = null;
      this.svgFileName = '';
      if (this.$refs.fileInput) this.$refs.fileInput.value = '';
      // Restore emoji in form icon if cleared
    },

    async giveAchievement() {
      if (!this.giveUserId || !this.giveAchId) return alert('Velg bruker og achievement.');
      try {
        await axios.post('/admin/give-achievement', { user_id: this.giveUserId, achievement_id: this.giveAchId });
        alert('Achievement gitt!');
        this.giveUserId = '';
        this.giveAchId = '';
        await this.fetchAchievements();
      } catch (e) {
        const msg = e.response?.data?.msg || e.message;
        alert(msg === 'Already unlocked' ? 'Brukeren har allerede dette achievementet.' : 'Feil: ' + msg);
      }
    },
  },

  mounted() {
    this.fetchAchievements();
    this.fetchUsers();
  },
};
</script>

<style scoped>
/* ── Layout ── */
.ach-grid { display:grid; grid-template-columns:400px 1fr; gap:18px; align-items:start; }
.mb14 { margin-bottom:14px; }

/* ── Panel ── */
.panel { background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.11); border-radius:12px; overflow:hidden; }
.panel-head { padding:13px 18px; border-bottom:1px solid rgba(255,255,255,0.07); background:rgba(255,255,255,0.02); display:flex; align-items:center; gap:10px; }
.panel-title { font-family:'Barlow Condensed',sans-serif; font-size:13px; font-weight:800; color:var(--hmn-bright); letter-spacing:0.1em; text-transform:uppercase; flex:1; }
.panel-meta { font-size:11px; color:var(--hmn-muted); }
.panel-body { padding:18px; }

/* ── Live Preview ── */
.ach-preview { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); border-radius:10px; padding:14px; display:flex; align-items:center; gap:14px; position:relative; overflow:hidden; }
.ach-preview::before { content:''; position:absolute; inset:0; pointer-events:none; background:radial-gradient(ellipse 60% 80% at 20% 50%, var(--pglow,rgba(216,152,32,0.1)), transparent 70%); }
.ap-icon { width:48px; height:48px; border-radius:10px; flex-shrink:0; display:flex; align-items:center; justify-content:center; position:relative; }
.ap-ring { position:absolute; inset:-2px; border-radius:12px; border:2px solid; opacity:0.5; pointer-events:none; }
.icon-img { width:100%; height:100%; object-fit:contain; border-radius:8px; }
.ap-info { flex:1; position:relative; z-index:1; }
.ap-rar { font-size:9px; letter-spacing:0.1em; font-family:'Barlow Condensed',sans-serif; font-weight:700; text-transform:uppercase; margin-bottom:3px; }
.ap-title { font-size:15px; font-weight:600; color:var(--hmn-bright); font-family:'Barlow',sans-serif; margin-bottom:3px; }
.ap-desc { font-size:12px; color:rgba(255,255,255,0.4); font-family:'Barlow',sans-serif; line-height:1.5; }
.ap-cond { font-size:10px; color:var(--hmn-muted); font-family:'Barlow Condensed',sans-serif; margin-top:6px; letter-spacing:0.06em; text-transform:uppercase; }

/* ── Form fields ── */
.fg { display:flex; flex-direction:column; gap:5px; margin-bottom:14px; }
.fl { font-size:10px; color:var(--hmn-muted); letter-spacing:0.1em; text-transform:uppercase; font-family:'Barlow Condensed',sans-serif; font-weight:700; }
.fi, .fs, .fta { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.11); border-radius:7px; padding:10px 13px; font-size:13px; color:var(--hmn-bright); font-family:'DM Sans',sans-serif; outline:none; transition:all 0.15s; width:100%; }
.fi:focus, .fs:focus, .fta:focus { border-color:var(--hmn-cyan); box-shadow:0 0 0 3px rgba(0,184,208,0.1); }
.fi::placeholder, .fta::placeholder { color:var(--hmn-muted); }
.fta { resize:none; line-height:1.6; }
.fs { cursor:pointer; appearance:none; background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%233d5668' d='M6 8L1 3h10z'/%3E%3C/svg%3E"); background-repeat:no-repeat; background-position:right 12px center; padding-right:32px; background-color:rgba(255,255,255,0.04); }
.fs option { background:#131e28; }
.fg2 { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.glow-row { display:flex; align-items:center; gap:10px; }

/* ── Rarity chips ── */
.rarity-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; }
.rarity-chip { padding:8px 6px; border-radius:7px; text-align:center; cursor:pointer; border:1px solid; transition:all 0.15s; user-select:none; }
.rarity-chip:hover, .rarity-chip.selected { transform:translateY(-1px); }
.rarity-chip.selected { box-shadow:0 0 0 2px currentColor; }
.rn { font-family:'Barlow Condensed',sans-serif; font-size:11px; font-weight:800; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:2px; }
.rs { font-size:9px; opacity:0.7; }
.rc { background:rgba(255,255,255,0.04); border-color:rgba(255,255,255,0.12); color:rgba(255,255,255,0.5); }
.rr { background:rgba(0,184,208,0.08); border-color:rgba(0,184,208,0.2); color:var(--hmn-cyan); }
.re { background:rgba(112,80,216,0.1); border-color:rgba(112,80,216,0.25); color:#9070f0; }
.rl { background:rgba(216,152,32,0.1); border-color:rgba(216,152,32,0.25); color:var(--hmn-gold); }

/* ── Condition box ── */
.cond-box { background:rgba(0,184,208,0.05); border:1px solid rgba(0,184,208,0.15); border-radius:8px; padding:12px 14px; display:flex; align-items:center; gap:12px; }
.cond-icon { font-size:20px; flex-shrink:0; }
.cond-info { flex:1; }
.cond-label { font-size:12px; color:var(--hmn-cyan); font-family:'Barlow Condensed',sans-serif; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:3px; }
.cond-desc { font-size:12px; color:rgba(255,255,255,0.4); font-family:'Barlow',sans-serif; }
.cond-right { display:flex; align-items:center; gap:6px; flex-shrink:0; }
.cond-num { width:64px; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.11); border-radius:6px; padding:8px 10px; font-size:14px; font-weight:700; color:var(--hmn-cyan); font-family:'Barlow Condensed',sans-serif; outline:none; text-align:center; }
.cond-num:focus { border-color:var(--hmn-cyan); }
.cond-unit { font-size:10px; color:var(--hmn-muted); font-family:'Barlow Condensed',sans-serif; text-transform:uppercase; letter-spacing:0.06em; }

/* ── Image upload ── */
.img-upload { border:1px dashed rgba(0,184,208,0.2); border-radius:8px; padding:16px; text-align:center; cursor:pointer; transition:all 0.18s; background:rgba(0,184,208,0.02); position:relative; overflow:hidden; }
.img-upload:hover { border-color:rgba(0,184,208,0.4); background:rgba(0,184,208,0.05); }
.img-upload.has-file { border-color:rgba(40,184,96,0.35); background:rgba(40,184,96,0.04); cursor:default; }
.iu-file-input { position:absolute; inset:0; opacity:0; cursor:pointer; width:100%; height:100%; }
.iu-empty { display:flex; flex-direction:column; align-items:center; }
.iu-icon { font-size:20px; margin-bottom:5px; }
.iu-text { font-size:12px; color:var(--hmn-muted); font-family:'Barlow',sans-serif; }
.iu-text span { color:var(--hmn-cyan); }
.iu-format-badges { display:flex; gap:6px; justify-content:center; margin-top:7px; }
.iu-fmt { font-size:9px; padding:2px 7px; border-radius:3px; font-weight:700; letter-spacing:0.07em; font-family:'Barlow Condensed',sans-serif; text-transform:uppercase; }
.iu-fmt-svg { background:rgba(0,184,208,0.12); color:var(--hmn-cyan); border:1px solid rgba(0,184,208,0.22); }
.iu-fmt-png { background:rgba(255,255,255,0.05); color:rgba(255,255,255,0.4); border:1px solid rgba(255,255,255,0.11); }
.iu-preview { display:flex; flex-direction:column; align-items:center; gap:8px; position:relative; z-index:1; }
.iu-preview-img { width:64px; height:64px; object-fit:contain; }
.iu-preview-name { font-size:11px; color:var(--hmn-green); font-family:'Barlow',sans-serif; }
.iu-svg-badge { display:inline-flex; align-items:center; gap:4px; font-size:9px; padding:2px 7px; border-radius:3px; font-family:'Barlow Condensed',sans-serif; font-weight:700; letter-spacing:0.07em; text-transform:uppercase; border:1px solid; }
.iu-preview-remove { font-size:10px; color:var(--hmn-red2); cursor:pointer; font-family:'Barlow Condensed',sans-serif; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; padding:3px 9px; background:rgba(200,16,46,0.1); border:1px solid rgba(200,16,46,0.2); border-radius:4px; transition:all 0.15s; }
.iu-preview-remove:hover { background:rgba(200,16,46,0.2); }

/* ── Buttons ── */
.btn { display:inline-flex; align-items:center; gap:7px; padding:9px 18px; border-radius:7px; font-size:13px; font-weight:600; font-family:'Barlow',sans-serif; cursor:pointer; border:none; transition:all 0.18s; }
.btn:hover { transform:translateY(-1px); }
.btn-red { background:linear-gradient(145deg,var(--hmn-red),#8a0e1e); color:white; box-shadow:0 4px 16px rgba(200,16,46,0.28); }
.btn-ghost { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.11); color:var(--hmn-text); }
.btn-ghost:hover { background:rgba(255,255,255,0.08); }
.btn-danger { background:rgba(200,16,46,0.1); color:var(--hmn-red2); border:1px solid rgba(200,16,46,0.2); }
.btn-danger:hover { background:rgba(200,16,46,0.18); }
.btn-cyan { background:rgba(0,184,208,0.1); color:var(--hmn-cyan); border:1px solid rgba(0,184,208,0.2); }
.btn-cyan:hover { background:rgba(0,184,208,0.18); }
.btn-sm { padding:6px 13px; font-size:12px; }
.btn-xs { padding:4px 10px; font-size:11px; }
.btn-row { display:flex; gap:8px; }

/* ── Give row ── */
.give-row { display:flex; gap:10px; align-items:flex-end; }
.give-row .fg { flex:1; margin-bottom:0; }

/* ── Search + filters ── */
.search-inp { width:100%; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.11); border-radius:7px; padding:9px 12px; font-size:13px; color:var(--hmn-bright); font-family:'DM Sans',sans-serif; outline:none; margin-bottom:10px; }
.search-inp:focus { border-color:var(--hmn-cyan); }
.search-inp::placeholder { color:var(--hmn-muted); }
.ach-filters { display:flex; gap:6px; flex-wrap:wrap; }
.af { padding:5px 12px; border-radius:5px; font-size:11px; font-weight:600; font-family:'Barlow Condensed',sans-serif; letter-spacing:0.06em; text-transform:uppercase; cursor:pointer; border:1px solid rgba(255,255,255,0.07); background:rgba(255,255,255,0.03); color:var(--hmn-muted); transition:all 0.15s; }
.af:hover { color:var(--hmn-text); border-color:rgba(255,255,255,0.11); }
.af.active { background:rgba(0,184,208,0.08); border-color:rgba(0,184,208,0.2); color:var(--hmn-cyan); }

/* ── Achievement cards ── */
.ach-list { display:flex; flex-direction:column; gap:8px; }
.ach-card { background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.07); border-radius:10px; overflow:hidden; transition:all 0.18s; }
.ach-card:hover { border-color:rgba(255,255,255,0.11); transform:translateY(-1px); box-shadow:0 8px 28px rgba(0,0,0,0.3); }
.acc-inner { display:flex; align-items:center; gap:14px; padding:12px 16px; }
.acc-icon { width:44px; height:44px; border-radius:9px; flex-shrink:0; display:flex; align-items:center; justify-content:center; font-size:20px; position:relative; }
.acc-icon::after { content:''; position:absolute; inset:-1px; border-radius:10px; border:1px solid; opacity:0.45; }
.al .acc-icon { background:rgba(216,152,32,0.12); } .al .acc-icon::after { border-color:var(--hmn-gold); }
.ae .acc-icon { background:rgba(112,80,216,0.12); } .ae .acc-icon::after { border-color:#9070f0; }
.ar .acc-icon { background:rgba(0,184,208,0.1);  } .ar .acc-icon::after { border-color:var(--hmn-cyan); }
.ac-c .acc-icon { background:rgba(255,255,255,0.05); } .ac-c .acc-icon::after { border-color:rgba(255,255,255,0.2); }
.acc-info { flex:1; min-width:0; }
.acc-top { display:flex; align-items:center; gap:8px; margin-bottom:3px; }
.acc-title { font-size:14px; font-weight:600; color:var(--hmn-bright); font-family:'Barlow',sans-serif; }
.rtag { font-size:9px; padding:2px 7px; border-radius:3px; font-weight:700; letter-spacing:0.07em; font-family:'Barlow Condensed',sans-serif; text-transform:uppercase; }
.rtl { background:rgba(216,152,32,0.1); color:var(--hmn-gold); border:1px solid rgba(216,152,32,0.22); }
.rte { background:rgba(112,80,216,0.1); color:#9070f0; border:1px solid rgba(112,80,216,0.22); }
.rtr { background:rgba(0,184,208,0.1); color:var(--hmn-cyan); border:1px solid rgba(0,184,208,0.2); }
.rtc { background:rgba(255,255,255,0.05); color:rgba(255,255,255,0.4); border:1px solid rgba(255,255,255,0.11); }
.acc-desc { font-size:12px; color:rgba(255,255,255,0.35); font-family:'Barlow',sans-serif; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; margin-bottom:4px; }
.acc-cond { display:inline-flex; align-items:center; gap:5px; font-size:10px; color:var(--hmn-muted); font-family:'Barlow Condensed',sans-serif; text-transform:uppercase; letter-spacing:0.07em; }
.cdot { width:5px; height:5px; border-radius:50%; flex-shrink:0; }
.acc-unlocked { font-size:11px; color:var(--hmn-muted); flex-shrink:0; white-space:nowrap; font-family:'Barlow',sans-serif; padding:0 8px; }
.acc-actions { display:flex; gap:6px; flex-shrink:0; }

/* ── Empty state ── */
.empty-state { text-align:center; padding:24px; font-size:13px; color:var(--hmn-muted); font-family:'Barlow',sans-serif; }

/* ── Responsive ── */
@media (max-width:1100px) {
  .ach-grid { grid-template-columns:360px 1fr; }
}
@media (max-width:900px) {
  .ach-grid { grid-template-columns:1fr; }
  .give-row { flex-wrap:wrap; }
}
</style>
