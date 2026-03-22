<template>
  <div class="about-page">
    <!-- Page Hero -->
    <div class="page-hero">
      <div class="hmn-container page-hero-inner">
        <div class="page-eyebrow">
          <span class="page-eyebrow-dot"></span>
          <span class="page-eyebrow-text">REF: HMN-ORG-001 · Offisiell personaloversikt</span>
        </div>
        <h1 class="page-title">Om <em>oss</em></h1>
        <p class="page-desc">Et dedikert team som forstår at noen ganger trengs det både alkohol og en god kopp kaffe. Alle titler er selvpålagte og juridisk bindende.</p>
      </div>
    </div>

    <div class="about-body">
      <div class="hmn-container">

        <!-- Stats Band -->
        <div class="sh mb-sm">
          <span class="sh-title">Tall vi <em>fant på</em></span>
          <div class="sh-line"></div>
          <span class="sh-tag">§ 5.5 kan være oppdiktet</span>
        </div>
        <div class="stats-band mb-lg">
          <div class="stat-card sc1">
            <div class="stat-label">Registrerte pasienter</div>
            <div class="stat-val sv-cyan">{{ team.length > 0 ? team.length : 6 }}</div>
            <div class="stat-sub">alle aktive, dessverre</div>
          </div>
          <div class="stat-card sc2">
            <div class="stat-label">Uforklarte hendelser</div>
            <div class="stat-val sv-red">∞</div>
            <div class="stat-sub">under kontinuerlig utredning</div>
          </div>
          <div class="stat-card sc3">
            <div class="stat-label">Kaffe konsumert</div>
            <div class="stat-val sv-gold">10K+</div>
            <div class="stat-sub">kopper siden 2024</div>
          </div>
          <div class="stat-card sc4">
            <div class="stat-label">Eksistensielle kriser løst</div>
            <div class="stat-val sv-green">1+</div>
            <div class="stat-sub">kanskje</div>
          </div>
        </div>

        <!-- Team -->
        <div class="sh mb-sm">
          <span class="sh-title">Vårt <em>team</em></span>
          <div class="sh-line"></div>
          <span class="sh-tag">dynamisk · administreres fra admin</span>
        </div>
        <div class="team-grid mb-lg">
          <div
            v-for="(member, i) in team"
            :key="member.id"
            class="team-card"
          >
            <div class="team-avatar" :class="avatarColorClass(i)">{{ getInitials(member.name) }}</div>
            <div class="team-name">{{ member.name }}</div>
            <div class="team-role">{{ member.title }}</div>
            <div class="team-bio" v-if="member.bio">"{{ member.bio }}"</div>
            <div class="team-badges">
              <span
                v-for="badge in getMemberBadges(member)"
                :key="badge.label"
                class="badge"
                :class="badge.cls"
              >{{ badge.label }}</span>
            </div>
          </div>
          <div
            v-for="n in classifiedSlots"
            :key="'cls-' + n"
            class="team-card classified"
          >
            <div class="team-avatar">?</div>
            <div class="team-name">???</div>
            <div class="team-classified-label">Klassifisert · § 9.1</div>
            <div class="team-badges" style="margin-top:8px;">
              <span class="badge badge-locked">Tilgang nektet</span>
            </div>
          </div>
        </div>

        <!-- Timeline -->
        <div class="sh mb-sm">
          <span class="sh-title">Historien <em>hittil</em></span>
          <div class="sh-line"></div>
        </div>
        <div class="timeline mb-lg">
          <div v-for="(item, i) in timeline" :key="i" class="tl-item">
            <div class="tl-dot">{{ item.icon }}</div>
            <div class="tl-content">
              <div class="tl-date">{{ item.date }}</div>
              <div class="tl-title">{{ item.title }}</div>
              <div class="tl-desc">{{ item.desc }}</div>
            </div>
          </div>
        </div>

        <!-- Values -->
        <div class="sh mb-sm">
          <span class="sh-title">Våre <em>verdier</em></span>
          <div class="sh-line"></div>
          <span class="sh-tag">§ 1.1 offisielt vedtatt</span>
        </div>
        <div class="values-grid">
          <div v-for="(value, i) in values" :key="i" class="value-card">
            <div class="value-icon">{{ value.icon }}</div>
            <div class="value-title">{{ value.title }}</div>
            <div class="value-desc">{{ value.description }}</div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/axios';

const AVATAR_COLORS = ['av-red', 'av-blue', 'av-green', 'av-gold', 'av-purple', 'av-cyan'];

export default {
  name: "About",
  data() {
    return {
      team: [],
      timeline: [
        { icon: '🧠', date: '2024 — Starten', title: 'Født i kaos', desc: '"Vi møttes faktisk først i 2024 alle sammen face to face." Ingen visste hva de hadde begynt på.' },
        { icon: '🔥', date: 'August 2024 — REF: HMN-001', title: 'Den store Sunndalsøra-konspirasjonen', desc: 'Hva skjedde egentlig der oppe? Verden vil aldri vite. Etterforskning pågår. Journalen er forseglet.' },
        { icon: '💻', date: '2025 — Nå', title: 'Portalen åpner', desc: 'HMN Mental Pasienter lanserer offisielt. § 7.7 garanterer ingenting. Årsaken til deployment-feilen er fortsatt under utredning.' },
      ],
      values: [
        { icon: '🤝', title: 'Forståelse', description: 'Vi lytter først, diagnostiserer senere. Eller ikke i det hele tatt. Begge deler er greit.' },
        { icon: '👁️', title: 'Åpenhet', description: 'Ingen skjulte agendaer eller kostnader. Journalene er tilgjengelig for alle involverte parter.' },
        { icon: '💡', title: 'Innovasjon', description: 'Kombinerer tradisjonell og digital hjelp. Begge er like ubrukelige, men på en sjarmerende måte.' },
      ],
    };
  },
  computed: {
    classifiedSlots() {
      return Math.max(0, 6 - this.team.length);
    },
  },
  methods: {
    async fetchTeamMembers() {
      try {
        const response = await axios.get('/team-members');
        this.team = response.data.team_members;
      } catch (error) {
        console.error('Error fetching team members:', error);
      }
    },
    getInitials(name) {
      if (!name) return '?';
      return name.trim().charAt(0).toUpperCase();
    },
    avatarColorClass(index) {
      return AVATAR_COLORS[index % AVATAR_COLORS.length];
    },
    getMemberBadges(member) {
      const role = (member.title || '').toLowerCase();
      if (role.includes('admin') || role.includes('overlege') || role.includes('sjef')) {
        return [{ label: 'Admin', cls: 'badge-red' }, { label: 'Developer', cls: 'badge-cyan' }];
      }
      if (role.includes('producer')) return [{ label: 'Producer', cls: 'badge-green' }];
      if (role.includes('developer') || role.includes('dev')) return [{ label: 'Developer', cls: 'badge-cyan' }];
      if (role.includes('junior')) return [{ label: 'Junior', cls: 'badge-gold' }];
      return [{ label: member.title || 'Staff', cls: 'badge-cyan' }];
    },
  },
  mounted() {
    this.fetchTeamMembers();
  },
};
</script>

<style scoped>
/* ── Root ── */
.about-page {
  background: var(--bg);
  min-height: 100vh;
  color: var(--text);
}

/* ── Page Hero ── */
.page-hero {
  background: linear-gradient(180deg, #06090f, var(--bg));
  border-bottom: 1px solid var(--border);
  padding: 48px 0 40px;
  position: relative;
  overflow: hidden;
}
.page-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0,184,208,0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,184,208,0.02) 1px, transparent 1px);
  background-size: 52px 52px;
  mask-image: linear-gradient(180deg, rgba(0,0,0,0.5), transparent);
}
.page-hero-inner { position: relative; z-index: 1; }
.page-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(0,184,208,0.07);
  border: 1px solid rgba(0,184,208,0.16);
  padding: 5px 14px;
  border-radius: 4px;
  margin-bottom: 14px;
}
.page-eyebrow-dot {
  width: 6px; height: 6px;
  background: var(--green);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--green);
  animation: blink 2.5s infinite;
}
.page-eyebrow-text {
  color: var(--cyan);
  font-size: 10px;
  letter-spacing: 0.1em;
  font-family: var(--font-display);
  font-weight: 600;
  text-transform: uppercase;
}
.page-title {
  font-family: var(--font-display);
  font-size: clamp(2.8rem, 5vw, 5rem);
  font-weight: 900;
  color: var(--bright);
  text-transform: uppercase;
  line-height: 0.92;
  letter-spacing: -0.01em;
  margin-bottom: 10px;
}
.page-title em {
  background: linear-gradient(92deg, var(--cyan), var(--cyan2));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-style: normal;
}
.page-desc {
  font-size: 15px;
  color: rgba(255,255,255,0.35);
  line-height: 1.8;
  max-width: 520px;
}

/* ── Body ── */
.about-body { padding: 52px 0 72px; }

/* ── Stats Band ── */
.stats-band {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 18px;
  position: relative;
  overflow: hidden;
}
.stat-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  border-radius: 10px 10px 0 0;
}
.stat-card.sc1::before { background: linear-gradient(90deg, var(--cyan), transparent); }
.stat-card.sc2::before { background: linear-gradient(90deg, var(--red), transparent); }
.stat-card.sc3::before { background: linear-gradient(90deg, var(--gold), transparent); }
.stat-card.sc4::before { background: linear-gradient(90deg, var(--green), transparent); }
.stat-label {
  font-size: 10px;
  color: var(--muted);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-family: var(--font-display);
  margin-bottom: 6px;
}
.stat-val {
  font-family: var(--font-display);
  font-size: 30px;
  font-weight: 900;
  color: var(--bright);
  line-height: 1;
}
.stat-val.sv-cyan  { color: var(--cyan); }
.stat-val.sv-red   { color: var(--red2); }
.stat-val.sv-gold  { color: var(--gold); }
.stat-val.sv-green { color: var(--green); }
.stat-sub { font-size: 11px; color: var(--muted); margin-top: 4px; font-style: italic; }

/* ── Team Grid ── */
.team-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
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
.team-card.classified { opacity: 0.5; }
.team-card.classified:hover { transform: none; }
.team-avatar {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--s2), var(--s3));
  border: 2px solid var(--border2);
  margin: 0 auto 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 900;
  color: var(--muted);
}
.team-avatar.av-red    { background: linear-gradient(135deg, var(--red), #7a0e1e); color: white; }
.team-avatar.av-blue   { background: linear-gradient(135deg, #1a4a7a, #0a2a5a); color: white; }
.team-avatar.av-green  { background: linear-gradient(135deg, #1a6a3a, #0a3a1a); color: white; }
.team-avatar.av-gold   { background: linear-gradient(135deg, #7a5a10, #5a3800); color: white; }
.team-avatar.av-purple { background: linear-gradient(135deg, #4a2a8a, #2a0a6a); color: white; }
.team-avatar.av-cyan   { background: linear-gradient(135deg, #0a5a6a, #003a4a); color: white; }
.team-name {
  font-family: var(--font-display);
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
  font-family: var(--font-display);
  margin-bottom: 8px;
}
.team-bio {
  font-size: 12px;
  color: rgba(255,255,255,0.3);
  line-height: 1.65;
  font-style: italic;
  font-family: var(--font-body);
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
  font-family: var(--font-display);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-top: 8px;
}

/* ── Badges ── */
.badge {
  display: inline-block;
  font-size: 9px;
  padding: 3px 9px;
  border-radius: 4px;
  font-weight: 700;
  letter-spacing: 0.07em;
  font-family: var(--font-display);
  text-transform: uppercase;
}
.badge-cyan   { background: rgba(0,184,208,0.1);   color: var(--cyan);  border: 1px solid rgba(0,184,208,0.2); }
.badge-red    { background: rgba(200,16,46,0.12);   color: var(--red2);  border: 1px solid rgba(200,16,46,0.22); }
.badge-gold   { background: rgba(216,152,32,0.1);   color: var(--gold);  border: 1px solid rgba(216,152,32,0.2); }
.badge-green  { background: rgba(40,184,96,0.1);    color: var(--green); border: 1px solid rgba(40,184,96,0.2); }
.badge-locked { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.2); border: 1px solid var(--border); }

/* ── Timeline ── */
.timeline { display: flex; flex-direction: column; gap: 0; }
.tl-item {
  display: flex;
  gap: 20px;
  padding-bottom: 28px;
  position: relative;
}
.tl-item:last-child { padding-bottom: 0; }
.tl-item:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 15px; top: 32px; bottom: 0;
  width: 1px;
  background: var(--border);
}
.tl-dot {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: var(--surface);
  border: 1px solid var(--border2);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}
.tl-content { flex: 1; padding-top: 4px; }
.tl-date {
  font-size: 10px;
  color: var(--muted);
  letter-spacing: 0.08em;
  font-family: var(--font-display);
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.tl-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 800;
  color: var(--bright);
  margin-bottom: 4px;
}
.tl-desc {
  font-size: 13px;
  color: rgba(255,255,255,0.3);
  line-height: 1.65;
  font-family: var(--font-body);
}

/* ── Values Grid ── */
.values-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.value-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
  transition: border-color 0.2s;
}
.value-card:hover { border-color: var(--border2); }
.value-icon { font-size: 24px; margin-bottom: 12px; }
.value-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 800;
  color: var(--bright);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 8px;
}
.value-desc {
  font-size: 13px;
  color: rgba(255,255,255,0.3);
  line-height: 1.7;
  font-family: var(--font-body);
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .stats-band { grid-template-columns: repeat(2, 1fr); }
  .team-grid  { grid-template-columns: repeat(2, 1fr); }
  .values-grid { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
  .stats-band { grid-template-columns: 1fr; }
  .team-grid  { grid-template-columns: 1fr; }
}
</style>
