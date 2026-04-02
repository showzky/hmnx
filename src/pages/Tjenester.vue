<template>
  <div class="services-page">
    <div class="page-hero">
      <div class="hmn-container page-hero-inner">
        <div class="page-eyebrow">
          <span class="page-eyebrow-dot"></span>
          <span class="page-eyebrow-text">REF: HMN-SVC-001 · Digital tjenestekatalog</span>
        </div>
        <h1 class="page-title">Tjen<em>ester</em></h1>
        <p class="page-desc">
          HMN samler gaming, interninfo, hendelser og personlig portalkaos i ett halvoffisielt system.
          Seriost nok til å se ekte ut. Ustabilt nok til å være oss.
        </p>
        <div class="hero-chips">
          <span class="hero-chip hc-cyan">Profil og journal</span>
          <span class="hero-chip hc-green">Gaming og achievements</span>
          <span class="hero-chip hc-gold">Hendelser og oppmøte</span>
          <span class="hero-chip hc-red">Intern HMN-drift</span>
        </div>
      </div>
    </div>

    <div class="services-body">
      <div class="hmn-container">
        <div class="status-band mb-lg">
          <div class="status-card st-cyan">
            <div class="status-label">Portalstatus</div>
            <div class="status-value">Operativ-ish</div>
            <div class="status-sub">Flesteparten av funksjonene svarer innen rimelig tid.</div>
          </div>
          <div class="status-card st-red">
            <div class="status-label">Byråkratisk nivå</div>
            <div class="status-value">Unødvendig høyt</div>
            <div class="status-sub">Som et ekte helseforetak, bare med bedre badges og dårligere impulskontroll.</div>
          </div>
          <div class="status-card st-gold">
            <div class="status-label">Primære plattformer</div>
            <div class="status-value">HMN · Steam · Xbox</div>
            <div class="status-sub">Halv pasientportal, halv gaming-hub, full identitetskrise.</div>
          </div>
        </div>

        <div class="sh mb-sm">
          <span class="sh-title">Portal<em>områder</em></span>
          <div class="sh-line"></div>
          <span class="sh-tag">det du faktisk finner her</span>
        </div>
        <div class="service-grid mb-lg">
          <article v-for="service in services" :key="service.title" class="service-card" :class="service.accentClass">
            <div class="service-top">
              <span class="service-kicker">{{ service.kicker }}</span>
              <span class="service-tag">{{ service.tag }}</span>
            </div>
            <div class="service-icon">{{ service.icon }}</div>
            <h2 class="service-title">{{ service.title }}</h2>
            <p class="service-desc">{{ service.description }}</p>
            <ul class="service-list">
              <li v-for="item in service.items" :key="item">{{ item }}</li>
            </ul>
            <router-link :to="service.to" class="service-link">{{ service.linkLabel }}</router-link>
          </article>
        </div>

        <div class="sh mb-sm">
          <span class="sh-title">Hvordan det <em>fungerer</em></span>
          <div class="sh-line"></div>
        </div>
        <div class="flow-grid mb-lg">
          <article v-for="step in steps" :key="step.step" class="flow-card">
            <div class="flow-step">{{ step.step }}</div>
            <div class="flow-title">{{ step.title }}</div>
            <div class="flow-desc">{{ step.description }}</div>
          </article>
        </div>

        <div class="service-note mb-lg">
          <div class="service-note-dot"></div>
          <div class="service-note-copy">
            <div class="service-note-title">Offisiell merknad</div>
            <div class="service-note-text">
              Tjenestene leveres digitalt via portalen og oppdateres fortløpende etter humør, prioriteringer og
              hvorvidt noen husket å deploye riktig branch.
            </div>
          </div>
        </div>

        <div class="cta-panel">
          <div class="cta-copy">
            <div class="cta-kicker">Neste steg</div>
            <div class="cta-title">Bruk portalen som et normalt menneske. Eller minst som et registrert medlem.</div>
            <div class="cta-text">
              Logg inn for å åpne dashboard, koble til plattformer og se hva HMN mener du bør bruke tiden din på.
            </div>
          </div>
          <div class="cta-actions">
            <router-link v-if="auth.isAuthenticated" to="/dashboard" class="btn btn-red">Åpne dashboard</router-link>
            <router-link v-if="auth.isAuthenticated" to="/settings" class="btn btn-ghost">Gå til innstillinger</router-link>
            <template v-else>
              <router-link to="/login" class="btn btn-red">Logg inn</router-link>
              <router-link to="/register" class="btn btn-ghost">Registrer deg</router-link>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/authStore';

const auth = useAuthStore();

const services = [
  {
    icon: '🪪',
    kicker: 'Personlig område',
    tag: 'Portal',
    title: 'Profil og pasientjournal',
    description: 'Basen for alt annet. Her ligger identitet, bio, rang, tilstedeværelse og øvrig halvoffisiell dokumentasjon.',
    items: ['Profilkort, banner og bio', 'Rang, roller og personlig status', 'Oversikt over aktivitet og portalspor'],
    to: '/about',
    linkLabel: 'Se hvem vi later som vi er',
    accentClass: 'accent-cyan',
  },
  {
    icon: '🎮',
    kicker: 'Gaminglag',
    tag: 'Integrasjoner',
    title: 'Gaming og plattformkoblinger',
    description: 'Koble til Steam og Xbox for å få aktivitet, spilloversikt og achievements inn i samme system som resten av galskapen.',
    items: ['Steam- og Xbox-koblinger', 'Siste spill, nylige achievements og aktivitet', 'Én portal for flere plattformspor'],
    to: '/settings',
    linkLabel: 'Administrer koblinger',
    accentClass: 'accent-green',
  },
  {
    icon: '📅',
    kicker: 'Sosial logistikk',
    tag: 'Hendelser',
    title: 'Hendelser og oppmøte',
    description: 'Planlegg, overvåk og overtenk kommende happenings uten å miste oversikten over hvem som faktisk kommer.',
    items: ['Arrangementer med detaljer og tidspunkt', 'RSVP og deltakelsesoversikt', 'Synlighet i portalens aktivitetsflyt'],
    to: '/bedriftsmeldinger',
    linkLabel: 'Se kunngjøringer og oppdateringer',
    accentClass: 'accent-gold',
  },
  {
    icon: '📣',
    kicker: 'Internt apparat',
    tag: 'Informasjon',
    title: 'Bedriftsmeldinger og intern info',
    description: 'Offisielle meldinger, mindre offisielle oppdateringer og all nødvendig dramatikk presentert som strukturert informasjon.',
    items: ['Festede bedriftsmeldinger', 'Kategorisert internkommunikasjon', 'Referanser, datoer og arkivfølelse'],
    to: '/bedriftsmeldinger',
    linkLabel: 'Åpne bedriftsmeldinger',
    accentClass: 'accent-red',
  },
  {
    icon: '🧠',
    kicker: 'Fellesskap',
    tag: 'Samspill',
    title: 'Kommentarfelt, forum og sosial aktivitet',
    description: 'Portalen samler reaksjoner, diskusjoner og vennedynamikk i et system som er langt mer organisert enn selve gruppa.',
    items: ['Forum og tråder', 'Kommentarer og aktivitetsspor', 'Venner, profiler og intern tilstedeværelse'],
    to: '/dashboard',
    linkLabel: 'Gå til medlemsområdet',
    accentClass: 'accent-purple',
  },
  {
    icon: '🏆',
    kicker: 'Progresjon',
    tag: 'Belønning',
    title: 'Achievements, poeng og samlesystemer',
    description: 'Når portalen ikke bare observerer deg, men også begynner å måle deg. Et varselsignal og et motivasjonssystem samtidig.',
    items: ['Achievements og unlocks', 'Fitte Points og intern valuta', 'Shop, samlegreier og portalprogresjon'],
    to: '/shop',
    linkLabel: 'Se belønningssystemet',
    accentClass: 'accent-cyan',
  },
];

const steps = [
  {
    step: '01',
    title: 'Lag profil',
    description: 'Start med bruker, rang og de små detaljene som får siden til å se ut som et ekte system.',
  },
  {
    step: '02',
    title: 'Koble til plattformer',
    description: 'Legg til Steam og andre koblinger så portalen kan hente inn aktivitet, spill og tilhørende skryt.',
  },
  {
    step: '03',
    title: 'Bruk alt samtidig',
    description: 'Dashboard, meldinger, hendelser og samlesystemer er laget for å fungere som ett sammenhengende HMN-univers.',
  },
];
</script>

<style scoped>
.services-page {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
}

.page-hero {
  position: relative;
  overflow: hidden;
  padding: 52px 0 42px;
  border-bottom: 1px solid var(--border);
  background: linear-gradient(180deg, #06090f, var(--bg));
}

.page-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 62% 120% at 18% 0%, rgba(0, 184, 208, 0.09), transparent 68%),
    radial-gradient(ellipse 55% 100% at 82% 0%, rgba(200, 16, 46, 0.08), transparent 70%);
  pointer-events: none;
}

.page-hero-inner {
  position: relative;
  z-index: 1;
}

.page-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  border-radius: 4px;
  border: 1px solid rgba(0, 184, 208, 0.16);
  background: rgba(0, 184, 208, 0.07);
  margin-bottom: 14px;
}

.page-eyebrow-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 8px var(--green);
  animation: blink 2.5s infinite;
}

.page-eyebrow-text {
  color: var(--cyan);
  font-size: 10px;
  letter-spacing: 0.1em;
  font-family: var(--font-display);
  font-weight: 700;
  text-transform: uppercase;
}

.page-title {
  margin: 0 0 12px;
  font-family: var(--font-display);
  font-size: clamp(2.8rem, 5vw, 4.8rem);
  line-height: 0.92;
  letter-spacing: -0.01em;
  text-transform: uppercase;
  color: var(--bright);
}

.page-title em {
  font-style: normal;
  color: transparent;
  background: linear-gradient(92deg, var(--cyan), var(--cyan2));
  -webkit-background-clip: text;
  background-clip: text;
}

.page-desc {
  max-width: 640px;
  margin: 0;
  color: rgba(255, 255, 255, 0.38);
  font-size: 15px;
  line-height: 1.8;
}

.hero-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}

.hero-chip {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.03);
  font-family: var(--font-display);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hc-cyan { color: var(--cyan); border-color: rgba(0, 184, 208, 0.22); background: rgba(0, 184, 208, 0.08); }
.hc-green { color: var(--green); border-color: rgba(40, 184, 96, 0.22); background: rgba(40, 184, 96, 0.08); }
.hc-gold { color: var(--gold); border-color: rgba(216, 152, 32, 0.22); background: rgba(216, 152, 32, 0.08); }
.hc-red { color: var(--red2); border-color: rgba(200, 16, 46, 0.22); background: rgba(200, 16, 46, 0.08); }

.services-body {
  padding: 40px 0 72px;
}

.status-band {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.status-card {
  position: relative;
  padding: 18px 18px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
}

.status-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
}

.st-cyan::before { background: linear-gradient(90deg, var(--cyan), transparent); }
.st-red::before { background: linear-gradient(90deg, var(--red2), transparent); }
.st-gold::before { background: linear-gradient(90deg, var(--gold), transparent); }

.status-label {
  color: var(--muted);
  font-family: var(--font-display);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.status-value {
  color: var(--bright);
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 800;
  margin-bottom: 6px;
}

.status-sub {
  color: rgba(255, 255, 255, 0.34);
  font-size: 12px;
  line-height: 1.65;
}

.sh {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sh-title {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--bright);
}

.sh-title em {
  color: var(--cyan);
  font-style: normal;
}

.sh-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, rgba(255,255,255,0.08), transparent);
}

.sh-tag {
  color: var(--muted);
  font-family: var(--font-display);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.service-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.service-card {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 100%;
  padding: 18px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.028);
  overflow: hidden;
  transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
}

.service-card::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.9;
  pointer-events: none;
}

.service-card:hover {
  transform: translateY(-2px);
  border-color: var(--border2);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.32);
}

.accent-cyan::before {
  background: radial-gradient(ellipse 80% 80% at 0% 0%, rgba(0, 184, 208, 0.08), transparent 72%);
}

.accent-green::before {
  background: radial-gradient(ellipse 80% 80% at 0% 0%, rgba(40, 184, 96, 0.08), transparent 72%);
}

.accent-gold::before {
  background: radial-gradient(ellipse 80% 80% at 0% 0%, rgba(216, 152, 32, 0.08), transparent 72%);
}

.accent-red::before {
  background: radial-gradient(ellipse 80% 80% at 0% 0%, rgba(200, 16, 46, 0.08), transparent 72%);
}

.accent-purple::before {
  background: radial-gradient(ellipse 80% 80% at 0% 0%, rgba(112, 80, 216, 0.08), transparent 72%);
}

.service-top,
.service-icon,
.service-title,
.service-desc,
.service-list,
.service-link {
  position: relative;
  z-index: 1;
}

.service-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 14px;
}

.service-kicker,
.service-tag {
  font-family: var(--font-display);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.service-kicker {
  color: var(--muted);
}

.service-tag {
  padding: 3px 8px;
  border-radius: 999px;
  color: var(--bright);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.service-icon {
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  margin-bottom: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 22px;
}

.service-title {
  margin: 0 0 10px;
  color: var(--bright);
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 800;
  line-height: 1;
}

.service-desc {
  margin: 0 0 14px;
  color: rgba(255, 255, 255, 0.36);
  font-size: 13px;
  line-height: 1.75;
}

.service-list {
  list-style: none;
  margin: 0 0 18px;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.service-list li {
  position: relative;
  padding-left: 14px;
  color: var(--text);
  font-size: 12px;
  line-height: 1.55;
}

.service-list li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 7px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--cyan);
}

.service-link {
  margin-top: auto;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--bright);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
}

.service-link:hover {
  color: var(--cyan2);
}

.flow-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.flow-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 18px;
}

.flow-step {
  color: var(--cyan);
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.flow-title {
  color: var(--bright);
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 800;
  margin-bottom: 8px;
}

.flow-desc {
  color: rgba(255, 255, 255, 0.34);
  font-size: 13px;
  line-height: 1.7;
}

.service-note {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(200, 16, 46, 0.05);
  border: 1px solid rgba(200, 16, 46, 0.16);
  border-radius: 10px;
}

.service-note-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--red2);
  box-shadow: 0 0 10px rgba(232, 48, 74, 0.45);
  margin-top: 5px;
  flex-shrink: 0;
}

.service-note-title {
  color: var(--red2);
  font-family: var(--font-display);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.service-note-text {
  color: rgba(255, 255, 255, 0.34);
  font-size: 12px;
  line-height: 1.7;
}

.cta-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 22px 24px;
  background: linear-gradient(145deg, rgba(255,255,255,0.035), rgba(255,255,255,0.02));
  border: 1px solid var(--border);
  border-radius: 12px;
}

.cta-copy {
  max-width: 720px;
}

.cta-kicker {
  color: var(--muted);
  font-family: var(--font-display);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 6px;
}

.cta-title {
  color: var(--bright);
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 800;
  line-height: 1.05;
  margin-bottom: 8px;
}

.cta-text {
  color: rgba(255, 255, 255, 0.36);
  font-size: 13px;
  line-height: 1.75;
}

.cta-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 10px 18px;
  border-radius: 6px;
  border: none;
  text-decoration: none;
  cursor: pointer;
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 600;
  transition: transform 0.18s, box-shadow 0.18s, background 0.18s;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn-red {
  color: #fff;
  background: linear-gradient(145deg, var(--red), #8a0e1e);
  box-shadow: 0 4px 16px rgba(200, 16, 46, 0.28);
}

.btn-ghost {
  color: var(--text);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border2);
}

.mb-sm { margin-bottom: 14px; }
.mb-lg { margin-bottom: 32px; }

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.25; }
}

@media (max-width: 1100px) {
  .service-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .status-band,
  .flow-grid,
  .service-grid,
  .cta-panel {
    grid-template-columns: 1fr;
  }

  .cta-panel {
    flex-direction: column;
    align-items: flex-start;
  }

  .cta-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .page-hero {
    padding: 42px 0 34px;
  }

  .page-desc {
    font-size: 14px;
  }

  .status-band,
  .flow-grid,
  .service-grid {
    grid-template-columns: 1fr;
  }

  .service-card,
  .flow-card,
  .status-card,
  .cta-panel {
    padding: 16px;
  }

  .cta-title {
    font-size: 20px;
  }
}
</style>
