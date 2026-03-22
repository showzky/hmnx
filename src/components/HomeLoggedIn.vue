<template>
  <div class="hli">
    <div class="wb">
      <div class="c">
        <div class="wb-inner">
          <div class="wb-left">
            <div class="av av-lg" :style="avatarStyle">{{ userInitial }}</div>
            <div>
              <div class="wb-hi">Velkommen tilbake, <em>{{ user.username }}</em> 👋</div>
              <div class="wb-sub">{{ topRole }} · Pasient siden januar 2024</div>
            </div>
          </div>
          <div class="wb-right">
            <div class="wstat"><div class="wv cyan">{{ user.achievements_count ?? '—' }}</div><div class="wl">Achievements</div></div>
            <div class="ws"></div>
            <div class="wstat"><div class="wv gold">{{ currentPoints.toLocaleString('nb-NO') }}</div><div class="wl">Fitte Points</div></div>
            <div class="ws"></div>
            <div class="wstat"><div class="wv red">{{ user.krenket_level ?? 55 }}%</div><div class="wl">Krenket</div></div>
            <div class="ws"></div>
            <button class="dr-btn" :class="{ claimed: dailyClaimed }" :disabled="dailyClaimed" @click="claimDaily">
              <span>🎁</span>
              <div><div class="dr-label">{{ dailyClaimed ? formatTime(countdown) : 'Daglig belønning' }}</div><span class="dr-sub">🔥 hent poeng</span></div>
              <span v-if="!dailyClaimed" class="dr-pill">Hent</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="main">
      <div class="c">
        <div class="layout">
          <div>
            <div class="mb20">
              <div class="sh"><span class="sh-t">Gjengen <em>spiller nå</em></span><div class="sh-l"></div><span class="sh-a">Se alle profiler →</span></div>
              <div class="np-grid">
                <div v-if="!nowPlaying.length" class="card empty-txt">Ingen gaming-aktivitet ennå.</div>
                <div v-for="p in nowPlaying" :key="p.username" class="np-card" :class="{ playing: p.online }">
                  <div class="np-top">
                    <div class="av av-sm" :style="avatarStyleForEntity(p)">{{ p.username[0] }}<span class="np-dot" :class="{ on: p.online }"></span></div>
                    <span class="np-name">{{ p.username }}</span>
                    <span class="plat" :class="'fp-' + p.platform">{{ p.platformLabel || (p.platform === 'offline' ? 'Offline' : p.platform) }}</span>
                  </div>
                  <div v-if="p.online" class="np-art" :style="artStyleForItem(p)">{{ p.imageUrl ? '' : p.code }}</div>
                  <div v-else class="np-offline">Sist sett {{ p.lastSeen }}</div>
                  <div class="np-game" :class="{ muted: !p.online }">{{ p.game }}</div>
                  <div class="np-meta">{{ p.meta }}</div>
                </div>
              </div>
            </div>

            <div class="mb20">
              <div class="sh"><span class="sh-t">Gruppe<em>aktivitet</em></span><div class="sh-l"></div><span class="sh-a">Last mer →</span></div>
              <div class="card">
                <div v-if="!activityFeed.length" class="empty-txt">Ingen fersk gruppeaktivitet ennå.</div>
                <div v-for="(item, i) in activityFeed" :key="i" class="fi" :class="{ 'fi-new': item.isNew }">
                  <div v-if="item.avatar" class="av av-sm" :style="avatarStyleForEntity(item)">{{ item.avatar }}<span v-if="item.online" class="fi-online"></span></div>
                  <div v-else class="fi-ico" :class="item.icoClass">{{ item.ico }}</div>
                  <div class="fi-body">
                    <div class="fi-txt" v-html="item.text"></div>
                    <div class="fi-meta">
                      <span>{{ item.time }}</span>
                      <span class="plat" :class="'fp-' + item.plat">{{ item.platLabel }}</span>
                      <span v-if="item.game">{{ item.game }}</span>
                    </div>
                  </div>
                  <div v-if="item.thumb" class="fi-thumb" :style="thumbStyleForItem(item.thumb)">{{ item.thumb.imageUrl ? '' : item.thumb.code }}</div>
                </div>
              </div>
            </div>

            <div>
              <div class="sh"><span class="sh-t">Gjengens <em>gaming</em></span><div class="sh-l"></div></div>
              <div class="card gs-grid">
                <div class="gs"><div class="gv cyan">5,840t</div><div class="gl">Total spilltid</div></div>
                <div class="gs"><div class="gv gold">284,200</div><div class="gl">Gamerscore</div></div>
                <div class="gs"><div class="gv green">1,247</div><div class="gl">Achievements</div></div>
                <div class="gs"><div class="gv red">Ukjent</div><div class="gl">Årsak under utredning</div></div>
              </div>
            </div>
          </div>

          <div class="sidebar">
            <div>
              <div class="sh mb16"><span class="sh-t">Siste <em>melding</em></span><div class="sh-l"></div></div>
              <div class="card">
                <div v-if="latestMelding" class="mp">
                  <div class="mp-top">
                    <span class="mp-tag" :class="tagClass(latestMelding.category)">{{ categoryLabel(latestMelding.category) }}</span>
                    <span class="mp-ref">{{ latestMelding.ref }}</span>
                  </div>
                  <div class="mp-title">{{ latestMelding.title }}</div>
                  <div class="mp-body">{{ stripHtml(latestMelding.content) }}</div>
                  <div class="mp-foot">
                    <router-link :to="`/bedriftsmeldinger/${latestMelding.id}`" class="btn btn-red btn-sm">Les melding</router-link>
                    <router-link to="/bedriftsmeldinger" class="btn btn-ghost btn-sm">Alle meldinger</router-link>
                  </div>
                </div>
                <div v-else class="empty-txt">Ingen meldinger ennå.</div>
              </div>
            </div>

            <div>
              <div class="sh mb16"><span class="sh-t">🔥 CoD-<em>toppen</em></span><div class="sh-l"></div></div>
              <div class="card">
                <div v-if="!leaderboard.length" class="empty-txt">Ingen CoD-data ennå.</div>
                <div v-for="(u, i) in leaderboard" :key="u.name" class="lb-row">
                  <div class="lb-pos" :class="['p1','p2','p3'][i] || ''">{{ u.position || i + 1 }}</div>
                  <div class="av av-xs" :style="leaderboardAvatarStyle(u)">{{ u.name[0] }}</div>
                  <div class="lb-info"><div class="lb-name">{{ u.name }}</div><div class="lb-sub">{{ u.subtitle }}</div></div>
                  <div class="lb-bar"><div class="lb-track"><div class="lb-fill" :style="{ width: u.pct + '%' }"></div></div></div>
                  <div class="lb-val">{{ u.valueLabel || (u.pct + '%') }}</div>
                </div>
              </div>
            </div>

            <div>
              <div class="sh mb16"><span class="sh-t">Kommende <em>hendelser</em></span><div class="sh-l"></div></div>
              <div class="card">
                <div v-if="!events.length" class="empty-txt">Ingen kommende hendelser.</div>
                <router-link v-for="ev in events.slice(0,3)" :key="ev.id" :to="`/events/${ev.id}`" class="ev-row">
                  <div class="ev-badge"><div class="ev-day">{{ ev.day }}</div><div class="ev-month">{{ ev.month }}</div></div>
                  <div class="ev-info"><div class="ev-name">{{ ev.name }}</div><div class="ev-time">{{ ev.time }}</div></div>
                  <div class="ev-rsvp" :class="{ confirmed: ev.rsvp }">{{ ev.rsvp ? '✓ Påmeldt' : 'RSVP' }}</div>
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/axios';
import { io } from 'socket.io-client';

export default {
  name: 'HomeLoggedIn',
  props: { user: Object },

  data: () => ({
    events: [],
    latestMelding: null,
    fittePoints: 0,
    dailyClaimed: false,
    countdown: 0,
    _timer: null,
    nowPlaying: [],
    activityFeed: [],
    leaderboard: [
      { name: 'Pasient #7', rank: 'Junior', pct: 78, color: 'linear-gradient(135deg,#1a4a7a,#0a2a5a)' },
      { name: 'Andre', rank: 'Pasient', pct: 61, color: 'linear-gradient(135deg,#1a3a5a,#0a1a3a)' },
      { name: 'Showzky', rank: 'Developer', pct: 55, color: 'linear-gradient(135deg,#c8102e,#7a0e1e)' },
      { name: 'Oliver', rank: 'Spesialist', pct: 42, color: 'linear-gradient(135deg,#4a1a7a,#2a0a5a)' },
      { name: 'Whiskey69', rank: 'Producer', pct: 30, color: 'linear-gradient(135deg,#1a6a3a,#0a3a1a)' },
      { name: 'Håkon', rank: 'Tekniker', pct: 18, color: 'linear-gradient(135deg,#5a5a1a,#3a3a0a)' },
    ],
  }),

  computed: {
    userInitial() { return (this.user?.username || 'H')[0].toUpperCase(); },
    topRole() {
      const roles = (this.user?.roles || []).map(r => r.name?.toLowerCase());
      for (const r of ['superadmin', 'admin', 'developer', 'staff', 'moderator', 'producer']) {
        if (roles.includes(r)) return r.charAt(0).toUpperCase() + r.slice(1);
      }
      return this.user?.roles?.[0]?.name || 'Pasient';
    },
    avatarStyle() {
      return this.user?.avatar
        ? { backgroundImage: `url(${this.user.avatar})`, backgroundSize: 'cover', backgroundPosition: 'center' }
        : { background: 'linear-gradient(135deg,var(--red),#7a0e1e)' };
    },
    currentPoints() { return this.fittePoints || this.user?.fittePoints || 0; },
  },

  methods: {
    authH() { return { Authorization: `Bearer ${this.user?.token}` }; },

    async fetchAll() {
      await Promise.all([
        this.fetchEvents(),
        this.fetchMelding(),
        this.fetchFittePoints(),
        this.fetchDailyStatus(),
        this.fetchHomeSummary(),
        this.fetchCodLeaderboard(),
      ]);
    },

    async fetchEvents() {
      try {
        const { data } = await axios.get('events', { headers: this.authH() });
        const list = data.events || data || [];
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        this.events = list
          .filter(e => {
            const rawDate = e.event_date || e.date;
            if (!rawDate) return false;
            const eventDate = new Date(rawDate);
            eventDate.setHours(0, 0, 0, 0);
            return eventDate >= today;
          })
          .slice(0, 3)
          .map(e => {
          const d = new Date(e.event_date || e.date);
          return {
            id: e.id,
            name: e.event_name || e.name,
            day: d.getDate(),
            month: d.toLocaleString('nb-NO', { month: 'short' }),
            time: (e.event_time || e.time || '').slice(0, 5),
            rsvp: e.rsvp || false,
          };
        });
      } catch {
        this.events = [];
      }
    },

    async fetchMelding() {
      try {
        const { data } = await axios.get('/bedriftsmeldinger');
        const items = Array.isArray(data) ? data : [];
        this.latestMelding = items.find(m => m.pinned) || items[0] || null;
      } catch {
        this.latestMelding = null;
      }
    },

    async fetchFittePoints() {
      try {
        const { data } = await axios.get('get-fitte-points', { headers: this.authH() });
        this.fittePoints = data.points ?? 0;
      } catch {
        this.fittePoints = this.user?.fittePoints || 0;
      }
    },

    async fetchDailyStatus() {
      try {
        const { data } = await axios.get('get-daily-claim-status', { headers: this.authH() });
        this.dailyClaimed = data.dailyClaimed;
        if (data.dailyClaimed && data.nextClaimTime) {
          const diff = Math.floor((new Date(data.nextClaimTime) - Date.now()) / 1000);
          if (diff > 0) {
            this.countdown = diff;
            this.startCountdown();
          }
        }
      } catch {}
    },

    async fetchHomeSummary() {
      try {
        const { data } = await axios.get('home/social-summary', { headers: this.authH() });
        this.nowPlaying = Array.isArray(data.now_playing) ? data.now_playing : [];
        this.activityFeed = Array.isArray(data.activity_feed) ? data.activity_feed : [];
      } catch (error) {
        console.error('Failed to fetch home social summary:', error);
        this.nowPlaying = [];
        this.activityFeed = [];
      }
    },

    async fetchCodLeaderboard() {
      try {
        const { data } = await axios.get('cod/leaderboard', { headers: this.authH() });
        const rows = Array.isArray(data?.leaderboard) ? data.leaderboard : [];
        this.leaderboard = rows.map((row, index) => ({
          position: row.position || index + 1,
          name: row.name || 'Ukjent spiller',
          subtitle: row.subtitle || 'CoD esports',
          pct: row.pct || 0,
          valueLabel: row.value_label || '$0',
          avatarUrl: row.avatar_url || '',
          color: row.color || 'linear-gradient(135deg,#0b5cad,#103f73)',
        }));
      } catch (error) {
        console.error('Failed to fetch CoD leaderboard:', error);
        this.leaderboard = [];
      }
    },

    async claimDaily() {
      if (this.dailyClaimed) return;
      try {
        const { data } = await axios.post(
          'update-fitte-points',
          { points: this.currentPoints + 50, is_daily_reward: true },
          { headers: this.authH() }
        );
        this.fittePoints = data.points ?? this.fittePoints;
        this.dailyClaimed = true;
        if (data.nextClaimTime) {
          const diff = Math.floor((new Date(data.nextClaimTime) - Date.now()) / 1000);
          if (diff > 0) {
            this.countdown = diff;
            this.startCountdown();
          }
        }
      } catch (e) {
        console.error('Claim failed:', e);
      }
    },

    startCountdown() {
      clearInterval(this._timer);
      this._timer = setInterval(() => {
        if (this.countdown > 0) this.countdown--;
        else {
          clearInterval(this._timer);
          this.dailyClaimed = false;
        }
      }, 1000);
    },

    formatTime(s) {
      const h = Math.floor(s / 3600);
      const m = Math.floor((s % 3600) / 60);
      const sec = s % 60;
      return h ? `${h}t ${m}m` : m ? `${m}m ${sec}s` : `${sec}s`;
    },

    avatarStyleForEntity(entity) {
      if (entity?.avatarUrl) {
        return {
          backgroundImage: `url(${entity.avatarUrl})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        };
      }
      return { background: entity?.color || 'linear-gradient(135deg,var(--red),#7a0e1e)' };
    },

    artStyleForItem(item) {
      if (item?.imageUrl) {
        return {
          backgroundImage: `linear-gradient(rgba(8,12,18,0.18), rgba(8,12,18,0.18)), url(${item.imageUrl})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        };
      }
      return { background: item?.artBg || 'linear-gradient(135deg,#0a1628,#1a3a6a)' };
    },

    thumbStyleForItem(thumb) {
      if (thumb?.imageUrl) {
        return {
          backgroundImage: `linear-gradient(rgba(8,12,18,0.12), rgba(8,12,18,0.12)), url(${thumb.imageUrl})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        };
      }
      return { background: thumb?.bg || 'linear-gradient(135deg,#0a1628,#1a3a6a)' };
    },

    leaderboardAvatarStyle(entry) {
      if (entry?.avatarUrl) {
        return {
          backgroundImage: `url(${entry.avatarUrl})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        };
      }
      return { background: entry?.color || 'linear-gradient(135deg,#0b5cad,#103f73)' };
    },

    stripHtml(html) {
      if (!html) return '';
      const d = document.createElement('div');
      d.innerHTML = html;
      const txt = d.textContent || '';
      return txt.length > 110 ? `${txt.slice(0, 110)}…` : txt;
    },

    tagClass(cat) {
      return { oppdatering: 'tag-green', kaos: 'tag-red', hendelse: 'tag-cyan', viktig: 'tag-gold', 'thomas-relatert': 'tag-purple' }[cat] || 'tag-cyan';
    },

    categoryLabel(cat) {
      return { oppdatering: 'Oppdatering', kaos: 'Kaos', hendelse: 'Hendelse', viktig: 'Viktig', 'thomas-relatert': 'Sporadisk' }[cat] || cat;
    },
  },

  mounted() {
    this.leaderboard = [];
    this.fetchAll();
    const apiBase = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
    const socketBase = (import.meta.env.VITE_SOCKET_URL || '').replace(/\/$/, '') || (apiBase.endsWith('/api') ? apiBase.slice(0, -4) : apiBase) || 'http://localhost:5000';
    const socket = io(socketBase, {
      path: '/socket.io',
      transports: ['websocket', 'polling'],
      reconnectionAttempts: 5,
    });
    socket.on('connect', () => { if (this.user?.id) socket.emit('setUserId', this.user.id); });
    socket.on('daily_reward_claimed', d => {
      if (d.user_id === this.user?.id) {
        this.dailyClaimed = true;
        this.countdown = d.cooldown || 86400;
        this.startCountdown();
      }
    });
  },

  beforeUnmount() {
    clearInterval(this._timer);
  },
};
</script>

<style scoped>
.hli { min-height: 100vh; }
.c { width: min(calc(100% - 2.5rem), 1200px); margin: 0 auto; }

.wb { background: linear-gradient(135deg, rgba(200,16,46,0.07), rgba(0,184,208,0.04)); border-bottom: 1px solid var(--border); padding: 18px 0; }
.wb-inner { display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap; }
.wb-left { display: flex; align-items: center; gap: 14px; }
.wb-hi { font-family: var(--font-display); font-size: 20px; font-weight: 900; color: var(--text-bright); letter-spacing: 0.02em; }
.wb-hi em { color: var(--cyan); font-style: normal; }
.wb-sub { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.wb-right { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.wstat { text-align: center; }
.wv { font-family: var(--font-display); font-size: 20px; font-weight: 900; line-height: 1; }
.wv.cyan { color: var(--cyan); }
.wv.gold { color: var(--gold); }
.wv.red { color: var(--red2); }
.wl { font-size: 10px; color: var(--text-muted); letter-spacing: 0.07em; margin-top: 2px; font-family: var(--font-display); text-transform: uppercase; }
.ws { width: 1px; height: 32px; background: var(--border); }

.dr-btn { display: flex; align-items: center; gap: 10px; padding: 9px 14px; background: rgba(216,152,32,0.08); border: 1px solid rgba(216,152,32,0.22); border-radius: 8px; cursor: pointer; transition: all 0.18s; color: inherit; }
.dr-btn:hover:not(:disabled) { background: rgba(216,152,32,0.15); }
.dr-btn.claimed { opacity: 0.6; cursor: default; }
.dr-label { font-size: 12px; color: var(--gold); font-family: var(--font-body); font-weight: 500; }
.dr-sub { font-size: 10px; color: rgba(216,152,32,0.6); display: block; margin-top: 1px; }
.dr-pill { background: var(--gold); color: #080c12; font-size: 11px; font-weight: 700; font-family: var(--font-display); letter-spacing: 0.08em; text-transform: uppercase; padding: 5px 12px; border-radius: 5px; border: none; cursor: pointer; }

.av { border-radius: 50%; display: flex; align-items: center; justify-content: center; font-family: var(--font-display); font-weight: 900; color: white; flex-shrink: 0; position: relative; }
.av-lg { width: 44px; height: 44px; font-size: 16px; border: 2px solid rgba(200,16,46,0.35); }
.av-sm { width: 34px; height: 34px; font-size: 13px; }
.av-xs { width: 30px; height: 30px; font-size: 12px; }

.main { padding: 24px 0 64px; }
.layout { display: grid; grid-template-columns: 1fr 320px; gap: 20px; align-items: start; }
.sidebar { display: flex; flex-direction: column; gap: 20px; }
.mb16 { margin-bottom: 16px; }
.mb20 { margin-bottom: 20px; }

.sh { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
.sh-t { font-family: var(--font-display); font-size: 16px; font-weight: 800; color: var(--text-bright); letter-spacing: 0.08em; text-transform: uppercase; white-space: nowrap; }
.sh-t em { color: var(--cyan); font-style: normal; }
.sh-l { flex: 1; height: 1px; background: linear-gradient(90deg, var(--border2), transparent); }
.sh-a { font-size: 11px; color: var(--cyan); cursor: pointer; font-family: var(--font-body); white-space: nowrap; }
.sh-a:hover { text-decoration: underline; }

.card { background: rgba(255,255,255,0.025); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }

.np-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
.np-card { background: rgba(255,255,255,0.025); border: 1px solid var(--border); border-radius: 9px; padding: 12px; transition: all 0.18s; }
.np-card.playing { border-color: rgba(40,184,96,0.2); }
.np-top { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.np-name { font-size: 12px; font-weight: 600; color: var(--text-bright); font-family: var(--font-body); flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.np-dot { position: absolute; bottom: 0; right: 0; width: 8px; height: 8px; border-radius: 50%; border: 1.5px solid var(--bg); background: #2a3a4a; }
.np-dot.on { background: var(--green); box-shadow: 0 0 5px var(--green); }
.np-art { width: 100%; height: 52px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-family: var(--font-display); font-size: 11px; font-weight: 800; color: rgba(255,255,255,0.2); margin-bottom: 7px; }
.np-offline { font-size: 12px; color: var(--text-muted); font-style: italic; text-align: center; padding: 10px 0 7px; }
.np-game { font-size: 12px; color: var(--text); font-family: var(--font-body); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.np-game.muted { color: var(--text-muted); }
.np-meta { font-size: 10px; color: var(--text-muted); margin-top: 2px; }

.plat { font-size: 9px; padding: 2px 6px; border-radius: 3px; font-family: var(--font-display); font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; flex-shrink: 0; }
.fp-steam { background: rgba(27,159,212,0.12); color: #4ab8e8; }
.fp-xbox { background: rgba(16,124,16,0.12); color: #4ec84e; }
.fp-hmn { background: rgba(200,16,46,0.12); color: var(--red2); }
.fp-sc { background: rgba(255,85,0,0.12); color: #ff6633; }
.fp-bnet { background: rgba(20,142,255,0.12); color: #60aeff; }
.fp-offline { background: rgba(255,255,255,0.05); color: var(--text-muted); }

.fi { display: flex; align-items: flex-start; gap: 12px; padding: 12px 16px; border-bottom: 1px solid var(--border); transition: background 0.15s; position: relative; }
.fi:last-child { border-bottom: none; }
.fi:hover { background: rgba(255,255,255,0.02); }
.fi-new::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 2px; background: var(--cyan); }
.fi-online { position: absolute; bottom: 0; right: 0; width: 9px; height: 9px; background: var(--green); border-radius: 50%; border: 1.5px solid var(--bg); box-shadow: 0 0 5px var(--green); }
.fi-ico { width: 34px; height: 34px; border-radius: 8px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 16px; }
.ico-event { background: rgba(0,184,208,0.1); border: 1px solid rgba(0,184,208,0.2); }
.ico-ach { background: rgba(216,152,32,0.12); border: 1px solid rgba(216,152,32,0.2); }
.fi-body { flex: 1; min-width: 0; }
.fi-txt { font-size: 13px; color: var(--text); font-family: var(--font-body); line-height: 1.55; }
.fi-txt :deep(strong) { color: var(--text-bright); font-weight: 500; }
.fi-txt :deep(em) { color: var(--cyan); font-style: normal; }
.fi-meta { font-size: 11px; color: var(--text-muted); margin-top: 3px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.fi-thumb { width: 48px; height: 32px; border-radius: 5px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 9px; font-family: var(--font-display); font-weight: 800; color: rgba(255,255,255,0.3); }

.gs-grid { display: grid; grid-template-columns: 1fr 1fr; }
.gs { padding: 14px; border-bottom: 1px solid var(--border); }
.gs:nth-child(odd) { border-right: 1px solid var(--border); }
.gs:nth-last-child(-n+2) { border-bottom: none; }
.gv { font-family: var(--font-display); font-size: 20px; font-weight: 900; color: var(--text-bright); line-height: 1; }
.gv.cyan { color: var(--cyan); }
.gv.gold { color: var(--gold); }
.gv.green { color: var(--green); }
.gv.red { color: var(--red2); }
.gl { font-size: 10px; color: var(--text-muted); margin-top: 3px; font-family: var(--font-display); text-transform: uppercase; letter-spacing: 0.07em; }

.mp { padding: 14px 16px; }
.mp-top { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.mp-tag { display: inline-block; font-size: 9px; padding: 2px 7px; border-radius: 3px; font-weight: 700; letter-spacing: 0.07em; font-family: var(--font-display); text-transform: uppercase; }
.tag-green { background: rgba(40,184,96,0.1); color: var(--green); border: 1px solid rgba(40,184,96,0.2); }
.tag-red { background: rgba(200,16,46,0.12); color: var(--red2); border: 1px solid rgba(200,16,46,0.22); }
.tag-cyan { background: rgba(0,184,208,0.1); color: var(--cyan); border: 1px solid rgba(0,184,208,0.2); }
.tag-gold { background: rgba(216,152,32,0.1); color: var(--gold); border: 1px solid rgba(216,152,32,0.2); }
.tag-purple { background: rgba(112,80,216,0.1); color: #9070f0; border: 1px solid rgba(112,80,216,0.22); }
.mp-ref { font-size: 10px; color: var(--text-muted); font-family: var(--font-display); }
.mp-title { font-size: 15px; font-weight: 600; color: var(--text-bright); font-family: var(--font-body); margin-bottom: 5px; }
.mp-body { font-size: 12px; color: rgba(255,255,255,0.35); font-family: var(--font-body); line-height: 1.6; margin-bottom: 12px; }
.mp-foot { display: flex; gap: 8px; }

.btn { display: inline-flex; align-items: center; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; font-family: var(--font-body); cursor: pointer; border: none; transition: all 0.15s; text-decoration: none; }
.btn:hover { transform: translateY(-1px); }
.btn-red { background: linear-gradient(145deg, var(--red), #8a0e1e); color: white; }
.btn-ghost { background: rgba(255,255,255,0.04); border: 1px solid var(--border2); color: var(--text); }
.btn-ghost:hover { background: rgba(255,255,255,0.08); }

.lb-row { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-bottom: 1px solid var(--border); }
.lb-row:last-child { border-bottom: none; }
.lb-pos { width: 22px; font-family: var(--font-display); font-size: 15px; font-weight: 900; color: var(--text-muted); text-align: center; flex-shrink: 0; }
.lb-pos.p1 { color: var(--gold); }
.lb-pos.p2 { color: rgba(192,192,192,0.8); }
.lb-pos.p3 { color: rgba(180,100,40,0.8); }
.lb-info { flex: 1; min-width: 0; }
.lb-name { font-size: 13px; color: var(--text); font-family: var(--font-body); font-weight: 500; }
.lb-sub { font-size: 10px; color: var(--text-muted); }
.lb-bar { flex: 0 0 56px; }
.lb-track { background: rgba(255,255,255,0.06); height: 3px; border-radius: 2px; overflow: hidden; margin-top: 4px; }
.lb-fill { height: 100%; border-radius: 2px; background: linear-gradient(90deg, var(--red), var(--red2)); }
.lb-val { font-family: var(--font-display); font-size: 15px; font-weight: 800; color: var(--red2); }

.ev-row { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border-bottom: 1px solid var(--border); transition: background 0.15s; text-decoration: none; }
.ev-row:last-child { border-bottom: none; }
.ev-row:hover { background: rgba(255,255,255,0.025); }
.ev-badge { width: 36px; height: 36px; border-radius: 7px; background: rgba(0,184,208,0.1); border: 1px solid rgba(0,184,208,0.2); display: flex; flex-direction: column; align-items: center; justify-content: center; flex-shrink: 0; }
.ev-day { font-family: var(--font-display); font-size: 15px; font-weight: 900; color: var(--cyan); line-height: 1; }
.ev-month { font-size: 8px; color: var(--cyan); opacity: 0.7; letter-spacing: 0.06em; text-transform: uppercase; font-family: var(--font-display); }
.ev-info { flex: 1; min-width: 0; }
.ev-name { font-size: 13px; color: var(--text-bright); font-family: var(--font-body); font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ev-time { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.ev-rsvp { font-size: 11px; padding: 4px 10px; border-radius: 5px; background: rgba(0,184,208,0.1); color: var(--cyan); border: 1px solid rgba(0,184,208,0.2); font-family: var(--font-display); font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; cursor: pointer; flex-shrink: 0; transition: all 0.15s; }
.ev-rsvp:hover { background: rgba(0,184,208,0.2); }
.ev-rsvp.confirmed { background: rgba(40,184,96,0.1); color: var(--green); border-color: rgba(40,184,96,0.2); }

.empty-txt { padding: 16px; font-size: 12px; color: var(--text-muted); text-align: center; font-style: italic; }

@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
  .np-grid { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 600px) {
  .np-grid { grid-template-columns: 1fr; }
  .wb-right { display: none; }
}
</style>
