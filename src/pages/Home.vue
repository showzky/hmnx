<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <HomeLoggedIn v-if="auth.isAuthenticated" :user="auth.user" />

  <div v-else class="homepage">
    <HomeHero :loading="loading" :stats="stats" :krenkethetLabel="krenkethetLabel" />
    <HomeTicker :tickerItems="tickerItems" />

    <div class="main">
      <div class="hmn-container">

        <!-- BEDRIFTSMELDINGER -->
        <div class="sh reveal mb32">
          <span class="sh-title">Bedrifts<em>meldinger</em></span>
          <div class="sh-line"></div>
          <span class="sh-tag">sanntid-ish</span>
        </div>
        <HomeMeldinger
          :loading="loading"
          :featuredMelding="featuredMelding"
          :displayMeldinger="displayMeldinger"
          :formatDate="formatDate"
        />

        <HomeWidgets :loading="loading" :displayHendelser="displayHendelser" />

        <!-- FRA GJENGEN -->
        <div class="sh reveal mb32">
          <span class="sh-title">Fra <em>gjengen</em></span>
          <div class="sh-line"></div>
        </div>
        <div class="g2 reveal mb48">
          <div class="born">
            <div class="born-emoji">🎉</div>
            <div class="born-title">Født i kaos</div>
            <div class="born-quote">"Vi møttes faktisk først i 2024 alle sammen face to face"</div>
            <div class="born-attr">— Anonym pasient · REF: HMN-001</div>
          </div>
          <div class="disc">
            <div class="born-emoji">🎮</div>
            <div class="disc-title">TimeCraft Discord</div>
            <div class="disc-sub">Memes, kaos, halvgode idéer og av og til seriøse samtaler. Velkommen skarru være 📣</div>
            <a
              class="disc-btn"
              href="https://discord.gg/z8XkcvtaRs"
              target="_blank"
              rel="noopener noreferrer"
            >
              Bli med i koret av kaos
            </a>
          </div>
        </div>

        <!-- HISTORISK ØYEBLIKK -->
        <div class="sh reveal mb32">
          <span class="sh-title">Historisk <em>øyeblikk</em></span>
          <div class="sh-line"></div>
          <span class="sh-tag">arkiv</span>
        </div>
        <div class="hist reveal mb48">
          <div class="hist-top">
            <div class="hist-dot"></div>
            <span class="hist-top-label">Klassifisert hendelse · REF: HMN-001</span>
          </div>
          <div class="hist-body">
            <div>
              <div class="hist-ref">August 2024</div>
              <div class="hist-title">Den store Sunndalsøra-konspirasjonen</div>
              <div class="hist-sub">Hva skjedde egentlig der oppe? Verden vil aldri vite. Etterforskning pågår. Journalen er forseglet.</div>
            </div>
            <div class="hist-badge">Klassifisert</div>
          </div>
        </div>

        <!-- LOGIN CTA -->
        <div class="cta reveal">
          <div class="cta-text">
            <h3>Logg inn for å se alt</h3>
            <p>Profil, Steam-stats, Xbox, Battle.net, achievements, hendelse-RSVP og vennenes aktivitet. Alt du går glipp av ved å stå utenfor.</p>
          </div>
          <div class="cta-actions">
            <button class="btn btn-red"   @click="$router.push('/login')">Logg inn</button>
            <button class="btn btn-ghost" @click="$router.push('/register')">Registrer deg</button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import HomeLoggedIn from '@/components/HomeLoggedIn.vue';
import HomeHero from '@/components/HomeHero.vue';
import HomeTicker from '@/components/HomeTicker.vue';
import HomeMeldinger from '@/components/HomeMeldinger.vue';
import HomeWidgets from '@/components/HomeWidgets.vue';
import api from '@/axios';

const auth   = useAuthStore();
const router = useRouter();

// ── State ──────────────────────────────────────────────────────────────────
const stats = ref({ pasienter_online: null, kommende_hendelser_count: null, krenkethet_index: 55 });
const featuredMelding  = ref(null);
const rawMeldinger     = ref([]);
const rawHendelser     = ref([]);

const loading = ref({ stats: true, featuredMelding: true, meldinger: true, hendelser: true });

const FALLBACK_FEATURED_MELDING = {
  ref: 'HMN-QUIET-001',
  date: '2026-03-22T09:00:00.000Z',
  title: 'Ingen aktiv melding.\nPasienten er stabil.',
  body: 'Ingen alarmer, ingen kriser og ingen tegn på Thomas-relatert aktivitet. Dette er enten veldig bra eller veldig mistenkelig. § 4.2 anbefaler å ikke tenke for mye på det.',
  image_url: '',
  image_alt: '',
  ctaLabel: 'Utforsk portalen',
  ctaRoute: '/about',
  secondaryLabel: 'Se alle meldinger',
  secondaryRoute: '/bedriftsmeldinger',
  fallback: true,
};

const CURATED_FALLBACK_MELDINGER = [
  {
    id: 'quiet-watch',
    title: 'Observasjonsrommet er rolig',
    meta: 'nå · HMN-QUIET-011 · lav puls',
    desc: 'Ingen ferske bedriftsmeldinger akkurat nå. Teamet har enten kontroll, eller er så overbevisende at det ser slik ut.',
  },
  {
    id: 'open-door',
    title: 'Døra står fortsatt åpen',
    meta: 'løpende · intern notis · sosial sone',
    desc: 'Discord, Bangerfabrikken og resten av galskapen lever videre mens oppslagstavla tar seg en velfortjent pause.',
  },
  {
    id: 'next-drop',
    title: 'Neste slipp havner her',
    meta: 'fremover · HMN-MSG-NESTE · venteliste',
    desc: 'Når admin publiserer neste melding, får denne kolonnen ekte innhold med én gang. Inntil da holder vi det rent, ryddig og litt mistenkelig fredelig.',
  },
];

// ── Computed: krenkethet label ─────────────────────────────────────────────
const krenkethetLabel = computed(() => {
  const v = stats.value.krenkethet_index;
  if (v <= 30) return 'Lav';
  if (v <= 60) return 'Moderat';
  if (v <= 80) return 'Forhøyet';
  return 'Kritisk';
});

// ── Computed: update list with hardcoded fallbacks ─────────────────────────
const FALLBACK_MELDINGER = [
  { title: 'Systemmelding: API i restitusjon',      meta: 'nå · HMN-SYS-503 · midlertidig',  desc: 'Bedriftsmeldinger lastes fra klinisk database. Serveren er i observasjon. Prognose: god.' },
  { title: 'Årsak til nedetid: ukjent',              meta: 'i dag · automatisk · § 2.1',       desc: 'Varselet ble utstedt uten forutgående symptomer. Journalen oppdateres. Etterforskingen pågår.' },
  { title: 'Discord sentralbord: operativt',        meta: 'løpende · REF: HMN-MSG-018',       desc: 'Koordinert kommunikasjon pågår. Bivirkninger inkluderer spontane meninger og uplanlagte planer.' },
];
const displayMeldinger = computed(() =>
  rawMeldinger.value.length
    ? rawMeldinger.value.map(m => ({
        id: m.id,
        title: m.title,
        meta: m.meta || m.date || '',
        desc: m.body || m.desc || '',
        image_url: m.image_url || '',
        image_alt: m.image_alt || '',
      }))
    : CURATED_FALLBACK_MELDINGER
);

// ── Computed: real upcoming hendelser ─────────────────────────────────────
const BADGE_MAP = {
  today:   { cls: 'evb-red',  label: 'I dag' },
  soon:    { cls: 'evb-gold', label: 'Snart' },
  planned: { cls: 'evb-cyan', label: 'Planlagt' },
};
const displayHendelser = computed(() =>
  rawHendelser.value.length
    ? rawHendelser.value.map(h => ({
        id:        h.id,
        title:     h.title,
        to:        `/events/${h.id}`,
        dateLabel: [formatDate(h.date), h.time?.slice?.(0, 5)].filter(Boolean).join(' · '),
        badge:     BADGE_MAP[h.badge_type] || BADGE_MAP.planned,
      }))
    : []
);

// ── Computed: ticker items ────────────────────────────────────────────────
const tickerItems = computed(() => {
  const meldinger = featuredMelding.value && !featuredMelding.value.fallback
    ? [featuredMelding.value, ...rawMeldinger.value]
    : rawMeldinger.value;

  return meldinger.flatMap(melding => {
    const items = [];

    if (melding.ref) {
      items.push({ text: melding.ref, highlight: true });
    }

    if (melding.title) {
      items.push({ text: melding.title, highlight: false });
    }

    const metaParts = [melding.date ? formatDate(melding.date) : '', melding.meta || '']
      .map(part => part && String(part).trim())
      .filter(Boolean);

    if (metaParts.length) {
      items.push({ text: metaParts.join(' · '), highlight: false });
    }

    return items;
  });
});

// ── Helpers ───────────────────────────────────────────────────────────────
function formatDate(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('nb-NO', { day: 'numeric', month: 'long', year: 'numeric' });
}

// ── API fetchers ──────────────────────────────────────────────────────────
async function fetchStats() {
  try {
    const { data } = await api.get('/stats');
    stats.value = { krenkethet_index: 55, ...data };
  } catch { /* keep defaults */ } finally {
    loading.value.stats = false;
  }
}

function stripHtml(html) {
  if (!html) return '';
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || '';
}

async function fetchMeldinger() {
  try {
    const { data } = await api.get('/bedriftsmeldinger');
    const items = Array.isArray(data) ? data : [];
    if (items.length) {
      const pinned = items.find(m => m.pinned) || items[0];
      featuredMelding.value = {
        id:    pinned.id,
        ref:   pinned.ref,
        date:  pinned.created_at,
        title: pinned.title,
        body:  stripHtml(pinned.content),
        image_url: pinned.image_url || '',
        image_alt: pinned.image_alt || '',
      };
      rawMeldinger.value = items
        .filter(m => m.id !== pinned.id)
        .slice(0, 3)
        .map(m => ({
          id:    m.id,
          title: m.title,
          meta:  [formatDate(m.created_at), m.ref].filter(Boolean).join(' · '),
          desc:  stripHtml(m.content),
          image_url: m.image_url || '',
          image_alt: m.image_alt || '',
        }));
    } else {
      featuredMelding.value = FALLBACK_FEATURED_MELDING;
      rawMeldinger.value = [];
    }
  } catch {
    featuredMelding.value = FALLBACK_FEATURED_MELDING;
    rawMeldinger.value = [];
  } finally {
    loading.value.featuredMelding = false;
    loading.value.meldinger       = false;
  }
}

async function fetchHendelser() {
  try {
    const { data } = await api.get('/hendelser', { params: { upcoming: true, limit: 3 } });
    rawHendelser.value = data || [];
  } catch {
    rawHendelser.value = [];
  } finally {
    loading.value.hendelser = false;
  }
}

// ── Scroll reveal ─────────────────────────────────────────────────────────
function initReveal() {
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in'); });
  }, { threshold: 0.08 });
  document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
}

// ── Mount ─────────────────────────────────────────────────────────────────
onMounted(async () => {
  await nextTick();
  await Promise.allSettled([fetchStats(), fetchMeldinger(), fetchHendelser()]);
  initReveal();
});
</script>

<style scoped>
/* ── Base ── */
.homepage {
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  font-family: var(--font-body);
  overflow-x: hidden;
}

/* ── MAIN ── */
.main {
  padding: 52px 0 72px;
  background: var(--bg);
}

/* ── Buttons (used by events + CTA) ── */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 20px;
  border-radius: var(--r-md);
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-body);
  cursor: pointer;
  border: none;
  transition: all 0.18s;
  letter-spacing: 0.02em;
}
.btn:hover { transform: translateY(-1px); }
.btn-red {
  background: linear-gradient(145deg, var(--red), #8a0e1e);
  color: white;
  box-shadow: 0 4px 16px rgba(200,16,46,0.28);
}
.btn-red:hover { box-shadow: 0 6px 24px rgba(200,16,46,0.42); }
.btn-ghost {
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border2);
  color: var(--text);
}
.btn-ghost:hover { background: rgba(255,255,255,0.08); }

/* ── FRA GJENGEN ── */
.born {
  background: rgba(255,255,255,0.025);
  border: 1px solid var(--border2);
  border-radius: var(--r-lg);
  padding: 22px;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s;
}
.born:hover { border-color: rgba(0,184,208,0.16); }
.born::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(0,184,208,0.03), transparent 60%);
  pointer-events: none;
}
.born-emoji  { font-size: 26px; margin-bottom: 2px; }
.born-title  { font-family: var(--font-display); font-size: 20px; font-weight: 900; color: var(--bright); letter-spacing: 0.06em; text-transform: uppercase; margin: 10px 0 8px; }
.born-quote  { font-size: 13px; color: rgba(255,255,255,0.28); line-height: 1.75; font-style: italic; font-family: var(--font-body); }
.born-attr   { font-size: 10px; color: var(--text-muted); margin-top: 8px; font-family: var(--font-ui); }

.disc {
  background: linear-gradient(140deg, rgba(64,78,237,0.2), rgba(64,78,237,0.08));
  border: 1px solid rgba(88,101,242,0.2);
  border-radius: var(--r-lg);
  padding: 22px;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s;
}
.disc:hover { border-color: rgba(88,101,242,0.35); }
.disc::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at top, rgba(88,101,242,0.07), transparent 60%);
  pointer-events: none;
}
.disc-title { font-family: var(--font-display); font-size: 20px; font-weight: 900; color: white; letter-spacing: 0.06em; text-transform: uppercase; margin: 8px 0 7px; }
.disc-sub   { font-size: 13px; color: rgba(180,190,255,0.5); line-height: 1.75; margin-bottom: 16px; font-family: var(--font-body); }
.disc-btn {
  background: rgba(88,101,242,0.22);
  color: white;
  border: 1px solid rgba(88,101,242,0.32);
  padding: 9px 22px;
  font-size: 12px;
  border-radius: var(--r-md);
  cursor: pointer;
  font-weight: 700;
  font-family: var(--font-display);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  transition: all 0.18s;
  position: relative;
  z-index: 1;
}
.disc-btn:hover { background: rgba(88,101,242,0.38); }

/* ── HISTORISK ── */
.hist {
  background: rgba(255,255,255,0.018);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  overflow: hidden;
}
.hist-top {
  padding: 11px 16px;
  border-bottom: 1px solid var(--border);
  background: rgba(200,16,46,0.05);
  display: flex;
  align-items: center;
  gap: 10px;
}
.hist-dot {
  width: 7px; height: 7px;
  background: var(--red2);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--red2);
  flex-shrink: 0;
}
.hist-top-label {
  font-size: 11px;
  color: var(--red2);
  letter-spacing: 0.07em;
  font-weight: 600;
  font-family: var(--font-display);
  text-transform: uppercase;
}
.hist-body {
  padding: 18px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.hist-ref   { font-size: 11px; color: var(--text-muted); font-family: var(--font-ui); margin-bottom: 4px; }
.hist-title { font-family: var(--font-display); font-size: 18px; font-weight: 800; color: var(--bright); text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 6px; }
.hist-sub   { font-size: 13px; color: rgba(255,255,255,0.25); line-height: 1.6; font-family: var(--font-body); }
.hist-badge {
  font-size: 9px; padding: 4px 10px;
  border-radius: var(--r-xs);
  background: rgba(200,16,46,0.12);
  color: var(--red2);
  border: 1px solid rgba(200,16,46,0.22);
  font-weight: 700;
  letter-spacing: 0.07em;
  font-family: var(--font-display);
  text-transform: uppercase;
  white-space: nowrap;
  flex-shrink: 0;
}

/* ── CTA ── */
.cta {
  background: rgba(255,255,255,0.025);
  border: 1px solid var(--border2);
  border-radius: var(--r-lg);
  padding: 36px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-top: 16px;
}
.cta h3 {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 900;
  color: var(--bright);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}
.cta p {
  font-size: 13px;
  color: rgba(255,255,255,0.3);
  line-height: 1.7;
  max-width: 500px;
  font-family: var(--font-body);
}
.cta-actions { display: flex; gap: 10px; flex-shrink: 0; }
</style>
