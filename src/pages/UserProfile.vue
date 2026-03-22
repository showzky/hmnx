<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <div class="profile-page">

    <!-- Banner -->
    <div class="profile-banner">
      <div class="banner-grid"></div>
    </div>

    <!-- Profile Header -->
    <div class="profile-header-wrap">
      <div class="hmn-container">
        <div v-if="loading" class="loading-state">Laster profil…</div>
        <div v-else-if="!user" class="loading-state">Bruker ikke funnet.</div>
        <template v-else>
          <div class="profile-top">
            <div class="profile-left">
              <div class="avatar-wrap">
                <div class="avatar">
                  <img v-if="user.avatar" :src="user.avatar" class="avatar-img" alt="avatar" />
                  <span v-else>{{ initials }}</span>
                </div>
                <div class="avatar-online"></div>
              </div>
              <div class="profile-info">
                <div class="profile-name-row">
                  <span class="profile-name">{{ user.username || user.email }}</span>
                  <div class="pbadges">
                    <span v-for="r in user.roles" :key="r.id" class="pbadge" :class="badgeClass(r.name)">{{ r.name }}</span>
                  </div>
                </div>
                <div class="profile-sub">
                  <span class="profile-joined">Pasient siden januar 2024</span>
                  <span class="profile-online"><span class="online-dot"></span>Online nå</span>
                </div>
              </div>
            </div>
            <div class="profile-actions">
              <button v-if="isOwnProfile" class="btn btn-ghost btn-sm" @click="$router.push('/settings')">Innstillinger</button>
            </div>
          </div>
          <div class="profile-tabs">
            <div v-for="t in TABS" :key="t.id" class="ptab" :class="{ active: activeTab === t.id }" @click="activeTab = t.id">{{ t.label }}</div>
          </div>
        </template>
      </div>
    </div>

    <!-- Body -->
    <div class="profile-body" v-if="user">
      <div class="hmn-container">

        <!-- ── OVERSIKT ── -->
        <div v-show="activeTab === 'oversikt'" class="pg">

          <!-- Sidebar -->
          <div class="col">
            <RankCard
              v-if="primaryRole"
              :variant="primaryRole.name.toLowerCase()"
              :name="primaryRole.name"
            />
            <div class="scard" v-if="user.bio">
              <div class="sch"><span class="sch-t">Om meg</span></div>
              <div class="sb"><p class="bio-text">"{{ user.bio }}"</p></div>
            </div>
            <div class="scard">
              <div class="sch"><span class="sch-t">Pasientstatus</span></div>
              <div class="stat-rows">
                <div class="sr"><span class="sr-label">Krenkethetsnivå</span><span class="sr-val c-red">{{ krenketDisplay }}</span></div>
                <div class="sr"><span class="sr-label">Achievements</span><span class="sr-val c-cyan">—</span></div>
                <div class="sr"><span class="sr-label">Hendelser deltatt</span><span class="sr-val c-gold">—</span></div>
                <div class="sr"><span class="sr-label">Uforklarte hendelser</span><span class="sr-val c-green">∞</span></div>
              </div>
            </div>
            <div class="scard">
              <div class="sch"><span class="sch-t">Tilkoblede kontoer</span></div>
              <div class="sb">
                <div class="conn-list">
                  <div v-for="c in CONNECTIONS" :key="c.id" class="conn">
                    <div class="conn-icon" :class="c.cls">{{ c.abbr }}</div>
                    <div class="conn-info">
                      <div class="conn-name">{{ c.name }}</div>
                      <div class="conn-user">Ikke tilkoblet</div>
                    </div>
                    <div class="conn-dot cd-off"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Main -->
          <div class="col">
            <div class="mc">
              <div class="mc-head"><span class="mc-title">Helsejournal</span><span class="mc-meta">§ 4.4 kontinuerlig</span></div>
              <div class="krenket">
                <div class="kr-row">
                  <span class="kr-label">Krenkethetsnivå</span>
                  <span class="kr-val">{{ krenketDisplay }} · {{ krenketLabel }}</span>
                </div>
                <div class="kr-track"><div class="kr-fill" :style="{ width: krenketPercent }"></div></div>
                <div class="kr-sub">Stigende etter torsdagsmøtet. Behandles med kebab.</div>
              </div>
              <div class="kr-stats">
                <div class="krs"><div class="krs-val c-gold">—</div><div class="krs-label">Kaffe i dag</div></div>
                <div class="krs"><div class="krs-val c-cyan">—</div><div class="krs-label">Sist sett ute</div></div>
                <div class="krs"><div class="krs-val c-green">Stabil</div><div class="krs-label">Diagnose</div></div>
              </div>
            </div>
            <div class="mc">
              <div class="mc-head"><span class="mc-title">Nylig aktivitet</span></div>
              <div class="act-list">
                <div v-for="a in ACTIVITY" :key="a.id" class="act">
                  <div class="act-dot" :class="a.dot"></div>
                  <span class="act-text" v-html="a.text"></span>
                  <span class="act-time">{{ a.time }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ── GAMING ── -->
        <div v-show="activeTab === 'gaming'" class="tab-single">
          <div class="mc">
            <div class="mc-head"><span class="mc-title">Gaming</span><span class="mc-meta">koble til kontoer</span></div>
            <div class="empty-state">Koble til Steam, Xbox eller Battle.net fra Innstillinger for å se gaming-statistikk her.</div>
          </div>
        </div>

        <!-- ── ACHIEVEMENTS ── -->
        <div v-show="activeTab === 'achievements'" class="tab-single">
          <div class="mc">
            <div class="mc-head"><span class="mc-title">Achievements</span><span class="mc-meta">0 låst opp</span></div>
            <div class="empty-state">Ingen achievements låst opp ennå. Gjør noe interessant.</div>
          </div>
        </div>

        <!-- ── AKTIVITET ── -->
        <div v-show="activeTab === 'aktivitet'" class="tab-single">
          <div class="mc">
            <div class="mc-head"><span class="mc-title">All aktivitet</span></div>
            <div class="act-list">
              <div v-for="a in ACTIVITY" :key="a.id" class="act">
                <div class="act-dot" :class="a.dot"></div>
                <span class="act-text" v-html="a.text"></span>
                <span class="act-time">{{ a.time }}</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { fetchUsers } from '@/services/userService'
import RankCard from '@/components/RankCard.vue'

const TABS = [
  { id: 'oversikt',     label: 'Oversikt' },
  { id: 'gaming',       label: 'Gaming' },
  { id: 'achievements', label: 'Achievements' },
  { id: 'aktivitet',    label: 'Aktivitet' },
]
const RANK_PRIORITY = ['admin', 'overlege', 'developer', 'producer', 'junior', 'testrolle', 'member']
const BADGE_CLASS   = {
  admin: 'pb-red', overlege: 'pb-gold', developer: 'pb-cyan',
  producer: 'pb-green', junior: 'pb-gold', member: 'pb-muted', testrolle: 'pb-purple',
}
const CONNECTIONS = [
  { id: 1, name: 'Steam',   abbr: 'S', cls: 'ci-s' },
  { id: 2, name: 'Xbox',    abbr: 'X', cls: 'ci-x' },
  { id: 3, name: 'Discord', abbr: 'D', cls: 'ci-d' },
]
const ACTIVITY = [
  { id: 1, dot: 'ad-m', text: 'Logget inn for første gang · <strong>Velkommen, pasient</strong>', time: 'jan 2024' },
]

const route     = useRoute()
const auth      = useAuthStore()
const user      = ref(null)
const loading   = ref(true)
const activeTab = ref('oversikt')

const initials     = computed(() => (user.value?.username || user.value?.email || '?').charAt(0).toUpperCase())
const isOwnProfile = computed(() => auth.user?.id === user.value?.id)

const primaryRole = computed(() => {
  if (!user.value?.roles?.length) return null
  return [...user.value.roles].sort((a, b) => {
    const ai = RANK_PRIORITY.indexOf(a.name.toLowerCase())
    const bi = RANK_PRIORITY.indexOf(b.name.toLowerCase())
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi)
  })[0]
})

const krenketVal     = computed(() => Math.min(100, Math.max(0, user.value?.krenke_level || 0)))
const krenketDisplay = computed(() => `${Math.round(krenketVal.value)}%`)
const krenketPercent = computed(() => `${krenketVal.value}%`)
const krenketLabel   = computed(() => {
  const k = krenketVal.value
  if (k < 20) return 'Lav'
  if (k < 50) return 'Moderat'
  if (k < 75) return 'Forhøyet'
  return 'Kritisk'
})

function badgeClass(name) {
  return BADGE_CLASS[name.toLowerCase()] || 'pb-muted'
}

onMounted(async () => {
  try {
    const res = await fetchUsers()
    user.value = res.data.users.find(u => u.id === +route.params.userId) || null
  } catch (e) {
    console.error('Profile load error:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* ── Root ── */
.profile-page { background: var(--bg); min-height: 100vh; color: var(--text); }

/* ── Banner ── */
.profile-banner { height: 200px; position: relative; overflow: hidden; background: linear-gradient(135deg,#0a1628 0%,#1a3a6a 40%,#0d1f40 70%,#1a0a28 100%); }
.profile-banner::before { content: ''; position: absolute; inset: 0; background: radial-gradient(ellipse 60% 80% at 80% 50%,rgba(0,184,208,0.08),transparent 60%),radial-gradient(ellipse 40% 60% at 10% 80%,rgba(200,16,46,0.07),transparent 50%); }
.banner-grid { position: absolute; inset: 0; background-image: linear-gradient(rgba(0,184,208,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(0,184,208,0.03) 1px,transparent 1px); background-size: 40px 40px; }

/* ── Profile Header ── */
.profile-header-wrap { background: var(--bg2); border-bottom: 1px solid var(--border); }
.loading-state { padding: 24px 0; font-size: 14px; color: var(--muted); font-family: var(--font-body); font-style: italic; }
.profile-top { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; padding-bottom: 14px; }
.profile-left { display: flex; align-items: flex-end; gap: 16px; }
.avatar-wrap { position: relative; margin-top: -48px; flex-shrink: 0; }
.avatar { width: 96px; height: 96px; border-radius: 50%; background: linear-gradient(135deg,var(--red),#7a0e1e); border: 4px solid var(--bg2); display: flex; align-items: center; justify-content: center; font-family: var(--font-display); font-size: 34px; font-weight: 900; color: white; box-shadow: 0 0 24px rgba(200,16,46,0.3); overflow: hidden; position: relative; }
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-online { position: absolute; bottom: 4px; right: 4px; width: 14px; height: 14px; background: var(--green); border-radius: 50%; border: 2px solid var(--bg2); box-shadow: 0 0 8px var(--green); }
.profile-info { padding-top: 10px; }
.profile-name-row { display: flex; align-items: center; gap: 10px; margin-bottom: 5px; flex-wrap: wrap; }
.profile-name { font-family: var(--font-display); font-size: 26px; font-weight: 900; color: var(--bright); letter-spacing: 0.02em; line-height: 1; }
.pbadges { display: flex; gap: 5px; flex-wrap: wrap; }
.pbadge { font-size: 10px; padding: 3px 10px; border-radius: 4px; font-weight: 700; letter-spacing: 0.07em; font-family: var(--font-display); text-transform: uppercase; }
.pb-red    { background: rgba(200,16,46,0.15);  color: var(--red2);   border: 1px solid rgba(200,16,46,0.25); }
.pb-cyan   { background: rgba(0,184,208,0.1);   color: var(--cyan);   border: 1px solid rgba(0,184,208,0.2); }
.pb-gold   { background: rgba(216,152,32,0.12); color: var(--gold);   border: 1px solid rgba(216,152,32,0.22); }
.pb-green  { background: rgba(40,184,96,0.1);   color: var(--green);  border: 1px solid rgba(40,184,96,0.2); }
.pb-purple { background: rgba(112,80,216,0.1);  color: var(--purple); border: 1px solid rgba(112,80,216,0.2); }
.pb-muted  { background: rgba(255,255,255,0.05); color: var(--muted); border: 1px solid var(--border); }
.profile-sub { display: flex; align-items: center; gap: 14px; }
.profile-joined { font-size: 12px; color: var(--muted); }
.profile-online { display: flex; align-items: center; gap: 5px; font-size: 12px; color: var(--green); }
.online-dot { width: 6px; height: 6px; background: var(--green); border-radius: 50%; box-shadow: 0 0 6px var(--green); }
.profile-actions { display: flex; gap: 8px; padding-top: 10px; flex-shrink: 0; }
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 18px; border-radius: 6px; font-size: 13px; font-weight: 600; font-family: var(--font-body); cursor: pointer; border: none; transition: all 0.18s; }
.btn-ghost { background: rgba(255,255,255,0.04); border: 1px solid var(--border2); color: var(--text); }
.btn-ghost:hover { background: rgba(255,255,255,0.08); transform: translateY(-1px); }
.btn-sm { padding: 6px 14px; font-size: 12px; }

/* ── Tabs ── */
.profile-tabs { display: flex; border-top: 1px solid var(--border); margin-top: 6px; }
.ptab { padding: 11px 18px; font-family: var(--font-display); font-size: 13px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.18s; }
.ptab:hover { color: var(--text); }
.ptab.active { color: var(--cyan); border-bottom-color: var(--cyan); }

/* ── Body Layout ── */
.profile-body { padding: 24px 0 72px; }
.pg { display: grid; grid-template-columns: 280px 1fr; gap: 16px; align-items: start; }
.col { display: flex; flex-direction: column; gap: 12px; }
.tab-single { max-width: 700px; }

/* ── Sidebar Cards ── */
.scard { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
.sch { padding: 10px 14px; background: rgba(255,255,255,0.02); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
.sch-t { font-family: var(--font-display); font-size: 12px; font-weight: 800; color: var(--bright); letter-spacing: 0.1em; text-transform: uppercase; }
.sb { padding: 12px 14px; }
.bio-text { font-size: 13px; color: rgba(255,255,255,0.38); line-height: 1.75; font-family: var(--font-body); font-style: italic; }
.stat-rows {}
.sr { display: flex; align-items: center; justify-content: space-between; padding: 9px 14px; border-bottom: 1px solid var(--border); }
.sr:last-child { border-bottom: none; }
.sr-label { font-size: 12px; color: var(--muted); }
.sr-val { font-family: var(--font-display); font-size: 16px; font-weight: 800; }
.c-red { color: var(--red2); } .c-cyan { color: var(--cyan); } .c-gold { color: var(--gold); } .c-green { color: var(--green); }

/* ── Connections ── */
.conn-list { display: flex; flex-direction: column; gap: 7px; }
.conn { display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 7px; border: 1px solid var(--border); background: rgba(255,255,255,0.02); }
.conn-icon { width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 900; font-family: var(--font-display); flex-shrink: 0; }
.ci-s { background: rgba(27,159,212,0.15); color: #4ab8e8; border: 1px solid rgba(27,159,212,0.25); }
.ci-x { background: rgba(16,124,16,0.15);  color: #4ec84e; border: 1px solid rgba(16,124,16,0.25); }
.ci-d { background: rgba(88,101,242,0.15); color: #8891f8; border: 1px solid rgba(88,101,242,0.25); }
.conn-info { flex: 1; min-width: 0; }
.conn-name { font-size: 11px; font-weight: 600; color: var(--text); }
.conn-user { font-size: 10px; color: var(--muted); }
.conn-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.cd-on  { background: var(--green); box-shadow: 0 0 5px var(--green); }
.cd-off { background: var(--muted); }

/* ── Main Cards ── */
.mc { background: rgba(255,255,255,0.025); border: 1px solid var(--border2); border-radius: 10px; overflow: hidden; }
.mc-head { padding: 11px 16px; border-bottom: 1px solid var(--border); background: rgba(255,255,255,0.02); display: flex; align-items: center; justify-content: space-between; }
.mc-title { font-family: var(--font-display); font-size: 13px; font-weight: 800; color: var(--bright); letter-spacing: 0.08em; text-transform: uppercase; }
.mc-meta { font-size: 11px; color: var(--muted); }

/* ── Health ── */
.krenket { padding: 14px 16px; }
.kr-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 7px; }
.kr-label { font-size: 12px; color: var(--muted); }
.kr-val { font-family: var(--font-display); font-size: 18px; font-weight: 800; color: var(--red2); }
.kr-track { background: rgba(255,255,255,0.06); height: 5px; border-radius: 3px; overflow: hidden; margin-bottom: 6px; }
.kr-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg,var(--red),var(--red2)); box-shadow: 0 0 8px rgba(200,16,46,0.35); transition: width 0.6s ease; }
.kr-sub { font-size: 11px; color: var(--muted); font-style: italic; font-family: var(--font-body); }
.kr-stats { display: grid; grid-template-columns: 1fr 1fr 1fr; border-top: 1px solid var(--border); }
.krs { padding: 10px 12px; text-align: center; }
.krs:not(:last-child) { border-right: 1px solid var(--border); }
.krs-val { font-family: var(--font-display); font-size: 17px; font-weight: 800; line-height: 1; }
.krs-label { font-size: 10px; color: var(--muted); margin-top: 3px; }

/* ── Activity ── */
.act-list { display: flex; flex-direction: column; }
.act { display: flex; align-items: center; gap: 12px; padding: 9px 16px; border-bottom: 1px solid var(--border); transition: background 0.15s; }
.act:last-child { border-bottom: none; }
.act:hover { background: rgba(255,255,255,0.02); }
.act-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.ad-g { background: var(--green); box-shadow: 0 0 5px var(--green); } .ad-c { background: var(--cyan); }
.ad-o { background: var(--gold); } .ad-r { background: var(--red2); } .ad-m { background: var(--muted); }
.act-text { flex: 1; font-size: 13px; color: rgba(255,255,255,0.45); font-family: var(--font-body); }
.act-time { font-size: 11px; color: var(--muted); flex-shrink: 0; }

/* ── Empty ── */
.empty-state { padding: 24px 16px; font-size: 14px; color: rgba(255,255,255,0.3); font-family: var(--font-body); font-style: italic; text-align: center; line-height: 1.7; }

/* ── Responsive ── */
@media (max-width: 768px) {
  .pg { grid-template-columns: 1fr; }
  .profile-name { font-size: 20px; }
}
</style>
