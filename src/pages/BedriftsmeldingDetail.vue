<!-- Design system: /HMN_DESIGN_SYSTEM_v2.md -->
<template>
  <!-- LOADING -->
  <div v-if="loading" class="detail-page">
    <div class="container-narrow">
      <div class="skel-breadcrumb"></div>
      <div class="skel-meta-row"></div>
      <div class="skel-title-big"></div>
      <div class="skel-author"></div>
      <div class="skel-line mb12"></div>
      <div class="skel-line mb12" style="width:85%"></div>
      <div class="skel-line mb12" style="width:70%"></div>
    </div>
  </div>

  <!-- 404 -->
  <div v-else-if="notFound" class="detail-page">
    <div class="container-narrow notfound-wrap">
      <div class="nf-code">404</div>
      <div class="nf-title">Melding ikke funnet</div>
      <div class="nf-sub">Denne meldingen eksisterer ikke eller er slettet.</div>
      <router-link to="/" class="btn btn-ghost btn-sm" style="margin-top:20px;">← Tilbake til forsiden</router-link>
    </div>
  </div>

  <!-- CONTENT -->
  <div v-else class="detail-page">

    <!-- BREADCRUMB -->
    <div class="breadcrumb">
      <div class="container-narrow">
        <div class="bc-inner">
          <router-link to="/" class="bc-link">Hjem</router-link>
          <span class="bc-sep">›</span>
          <router-link to="/bedriftsmeldinger" class="bc-link">Bedriftsmeldinger</router-link>
          <span class="bc-sep">›</span>
          <span class="bc-current">{{ melding.ref }}</span>
        </div>
      </div>
    </div>

    <!-- POST HERO -->
    <div class="post-hero">
      <div class="container-narrow">

        <div class="post-meta-row">
          <div class="post-live-dot"></div>
          <span class="post-tag" :class="tagClass(melding.category)">{{ categoryLabel(melding.category) }}</span>
          <span class="post-ref">{{ melding.ref }}</span>
          <span class="post-date">{{ formatDate(melding.created_at) }}</span>
        </div>

        <h1 class="post-title">{{ melding.title }}</h1>

        <div class="author-row">
          <div class="author-av">{{ authorInitial }}</div>
          <div class="author-info">
            <div class="author-name">{{ melding.author?.username || 'HMN Admin' }}</div>
            <div class="author-role">{{ topRole }} · publisert {{ formatDateFull(melding.created_at) }}</div>
          </div>
          <div class="author-badges">
            <span
              v-for="role in authorBadges"
              :key="role"
              class="abadge"
              :class="roleBadgeClass(role)"
            >{{ role }}</span>
          </div>
        </div>

        <div class="post-divider"></div>
      </div>
    </div>

    <!-- POST BODY -->
    <div class="post-content">
      <div class="container-narrow">
        <div class="post-body" v-html="renderedContent"></div>

        <!-- POST FOOTER -->
        <div class="post-footer">
          <div class="pf-left">
            <span class="pf-tag-label">Kategori:</span>
            <span class="post-tag" :class="tagClass(melding.category)">{{ categoryLabel(melding.category) }}</span>
            <span class="post-ref" style="margin-left:4px;">· {{ melding.ref }}</span>
          </div>
          <div class="pf-right">
            <router-link to="/bedriftsmeldinger" class="btn btn-ghost btn-sm">← Alle meldinger</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- OTHER MELDINGER -->
    <div v-if="others.length" class="others-section">
      <div class="others-inner">
        <div class="container">
          <div class="sh">
            <span class="sh-title">Andre <em>meldinger</em></span>
            <div class="sh-line"></div>
          </div>
          <div class="other-grid">
            <router-link
              v-for="o in others"
              :key="o.id"
              :to="`/bedriftsmeldinger/${o.id}`"
              class="other-card"
            >
              <span class="oc-tag" :class="tagClass(o.category)">{{ categoryLabel(o.category) }}</span>
              <div class="oc-title">{{ o.title }}</div>
              <div class="oc-preview">{{ stripHtml(o.content) }}</div>
              <div class="oc-meta">{{ o.ref }} · {{ formatDateShort(o.created_at) }}</div>
            </router-link>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/axios';

const route = useRoute();

const loading = ref(true);
const notFound = ref(false);
const melding = ref(null);
const others = ref([]);

// ── Helpers ──────────────────────────────────────────────────────────────────

function stripHtml(html) {
  if (!html) return '';
  const tmp = document.createElement('div');
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || '';
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('nb-NO', { day: 'numeric', month: 'long', year: 'numeric' });
}

function formatDateFull(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('nb-NO', {
    day: 'numeric', month: 'long', year: 'numeric',
  }) + ' kl. ' + new Date(dateStr).toLocaleTimeString('nb-NO', { hour: '2-digit', minute: '2-digit' });
}

function formatDateShort(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('nb-NO', { day: 'numeric', month: 'short', year: 'numeric' });
}

const CATEGORY_LABELS = {
  oppdatering: 'Oppdatering',
  kaos: 'Kaos',
  hendelse: 'Hendelse',
  viktig: 'Viktig',
  'thomas-relatert': 'Sporadisk',
};

function categoryLabel(cat) {
  return CATEGORY_LABELS[cat] || cat || 'Melding';
}

function tagClass(cat) {
  const map = {
    oppdatering: 'pt-oppdatering',
    kaos: 'pt-kaos',
    hendelse: 'pt-hendelse',
    viktig: 'pt-viktig',
    'thomas-relatert': 'pt-sporadisk',
  };
  return map[cat] || 'pt-oppdatering';
}

function roleBadgeClass(role) {
  const r = role.toLowerCase();
  if (['admin', 'superadmin', 'developer'].includes(r)) return 'ab-red';
  if (['staff', 'moderator', 'producer'].includes(r)) return 'ab-cyan';
  return 'ab-cyan';
}

// ── Computed ──────────────────────────────────────────────────────────────────

const authorInitial = computed(() => {
  const name = melding.value?.author?.username || 'H';
  return name[0].toUpperCase();
});

const ROLE_PRIORITY = ['superadmin', 'admin', 'developer', 'staff', 'moderator', 'producer'];

const topRole = computed(() => {
  const roles = melding.value?.author?.roles || [];
  for (const r of ROLE_PRIORITY) {
    if (roles.map(x => x.toLowerCase()).includes(r)) return r.charAt(0).toUpperCase() + r.slice(1);
  }
  return roles[0] || 'Member';
});

const authorBadges = computed(() => {
  return (melding.value?.author?.roles || []).slice(0, 3);
});

const renderedContent = computed(() => renderPostContent(melding.value?.content || ''));

function isBlankParagraph(node) {
  return node?.tagName === 'P' && (!node.textContent || !node.textContent.trim()) && /<br\s*\/?>/i.test(node.innerHTML);
}

function detectCalloutType(text) {
  const normalized = (text || '').trim();
  if (/^(⚠️|⚠)?\s*Viktig\s*:/i.test(normalized)) return 'warning';
  if (/^(ℹ️|ℹ)?\s*Info\s*:/i.test(normalized)) return 'info';
  return null;
}

function stripCalloutLead(html, label) {
  return (html || '').replace(
    new RegExp(`^(?:\\s*(?:⚠️|⚠|ℹ️|ℹ)\\s*)?(?:<strong>)?\\s*${label}\\s*:?\\s*(?:<\\/strong>)?\\s*`, 'i'),
    ''
  ).trim();
}

function buildCallout(type, bodyHtml) {
  const label = type === 'warning' ? 'Viktig' : 'Info';
  const icon = type === 'warning' ? '⚠️' : 'ℹ️';
  const wrapper = document.createElement('div');
  wrapper.className = `post-callout post-callout--${type}`;

  const iconEl = document.createElement('span');
  iconEl.className = 'callout-icon';
  iconEl.textContent = icon;

  const textEl = document.createElement('div');
  textEl.className = 'callout-text';
  textEl.innerHTML = `<strong>${label}:</strong> ${bodyHtml || ''}`;

  wrapper.appendChild(iconEl);
  wrapper.appendChild(textEl);
  return wrapper;
}

function normalizeExistingCallout(node) {
  const type = node.classList.contains('post-callout--warning') ? 'warning' : 'info';
  const label = type === 'warning' ? 'Viktig' : 'Info';
  const textNode = node.querySelector('.callout-text');
  const bodyHtml = stripCalloutLead(textNode?.innerHTML || node.innerHTML, label);
  return buildCallout(type, bodyHtml);
}

function renderPostContent(html) {
  if (!html || typeof document === 'undefined') return html;

  const root = document.createElement('div');
  root.innerHTML = html;
  const nodes = Array.from(root.children);

  for (let index = 0; index < nodes.length; index += 1) {
    const node = nodes[index];
    if (!(node instanceof HTMLElement)) continue;

    if (node.classList.contains('post-callout')) {
      node.replaceWith(normalizeExistingCallout(node));
      continue;
    }

    const text = (node.textContent || '').trim();
    const iconOnlyWarning = /^(⚠️|⚠)$/.test(text);
    const iconOnlyInfo = /^(ℹ️|ℹ)$/.test(text);

    if (iconOnlyWarning || iconOnlyInfo) {
      let next = node.nextElementSibling;
      while (next instanceof HTMLElement && isBlankParagraph(next)) {
        const blank = next;
        next = next.nextElementSibling;
        blank.remove();
      }
      if (next instanceof HTMLElement) {
        const type = detectCalloutType(next.textContent || '') || (iconOnlyWarning ? 'warning' : 'info');
        const label = type === 'warning' ? 'Viktig' : 'Info';
        const callout = buildCallout(type, stripCalloutLead(next.innerHTML, label));
        next.replaceWith(callout);
        node.remove();
      }
      continue;
    }

    const type = detectCalloutType(text);
    if (type) {
      const label = type === 'warning' ? 'Viktig' : 'Info';
      node.replaceWith(buildCallout(type, stripCalloutLead(node.innerHTML, label)));
    }
  }

  return root.innerHTML;
}

// ── Fetch ──────────────────────────────────────────────────────────────────

async function fetchMelding(id) {
  loading.value = true;
  notFound.value = false;
  try {
    const { data } = await api.get(`/bedriftsmeldinger/${id}`);
    melding.value = data.melding;
    others.value = data.others || [];
  } catch (err) {
    if (err.response?.status === 404) {
      notFound.value = true;
    } else {
      notFound.value = true;
    }
  } finally {
    loading.value = false;
  }
}

onMounted(() => fetchMelding(route.params.id));

// Refetch when navigating between detail pages
watch(() => route.params.id, (id) => {
  if (id) fetchMelding(id);
});
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
}

/* ── Layout containers ── */
.container {
  width: min(calc(100% - 2.5rem), 1120px);
  margin: 0 auto;
}
.container-narrow {
  width: min(calc(100% - 2.5rem), 720px);
  margin: 0 auto;
}

/* ── Skeletons ── */
.skel-breadcrumb { height: 14px; width: 240px; background: rgba(255,255,255,0.06); border-radius: 4px; margin: 28px 0 32px; }
.skel-meta-row   { height: 18px; width: 320px; background: rgba(255,255,255,0.06); border-radius: 4px; margin-bottom: 14px; }
.skel-title-big  { height: 72px; width: 80%; background: rgba(255,255,255,0.06); border-radius: 6px; margin-bottom: 20px; }
.skel-author     { height: 48px; width: 280px; background: rgba(255,255,255,0.06); border-radius: 6px; margin-bottom: 24px; }
.skel-line       { height: 14px; width: 100%; background: rgba(255,255,255,0.04); border-radius: 4px; }
.mb12 { margin-bottom: 12px; }

/* ── 404 ── */
.notfound-wrap { padding: 80px 0; text-align: center; }
.nf-code  { font-family: var(--font-display); font-size: 96px; font-weight: 900; color: rgba(255,255,255,0.06); line-height: 1; }
.nf-title { font-family: var(--font-display); font-size: 24px; font-weight: 800; color: var(--text-bright); text-transform: uppercase; margin-top: -20px; }
.nf-sub   { font-size: 14px; color: var(--text-muted); margin-top: 8px; }

/* ── Breadcrumb ── */
.breadcrumb { padding: 20px 0 0; }
.bc-inner   { display: flex; align-items: center; gap: 8px; font-size: 12px; font-family: var(--font-body); color: var(--text-muted); }
.bc-link    { color: var(--text-muted); text-decoration: none; transition: color 0.15s; }
.bc-link:hover { color: var(--cyan); }
.bc-sep     { color: #1e3448; }
.bc-current { color: var(--text); }

/* ── Post hero ── */
.post-hero {
  padding: 28px 0 0;
  position: relative;
}
.post-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 60% 100% at 50% 0%, rgba(0,184,208,0.04), transparent 70%);
  pointer-events: none;
}

/* ── Meta row ── */
.post-meta-row {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 16px; flex-wrap: wrap;
}
.post-live-dot {
  width: 6px; height: 6px;
  background: var(--green); border-radius: 50%;
  box-shadow: 0 0 6px var(--green);
  animation: blink 2.5s infinite; flex-shrink: 0;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

.post-tag {
  display: inline-block; font-size: 10px; padding: 3px 10px;
  border-radius: 4px; font-weight: 700; letter-spacing: 0.08em;
  font-family: var(--font-display); text-transform: uppercase;
}
.pt-oppdatering { background: rgba(40,184,96,0.1);  color: var(--green); border: 1px solid rgba(40,184,96,0.2); }
.pt-kaos        { background: rgba(200,16,46,0.12); color: var(--red2);  border: 1px solid rgba(200,16,46,0.22); }
.pt-hendelse    { background: rgba(0,184,208,0.1);  color: var(--cyan);  border: 1px solid rgba(0,184,208,0.2); }
.pt-viktig      { background: rgba(216,152,32,0.1); color: var(--gold);  border: 1px solid rgba(216,152,32,0.2); }
.pt-sporadisk      { background: rgba(112,80,216,0.1); color: #9070f0;      border: 1px solid rgba(112,80,216,0.22); }

.post-ref  { font-size: 11px; color: var(--text-muted); font-family: var(--font-display); letter-spacing: 0.07em; }
.post-date { font-size: 11px; color: var(--text-muted); margin-left: auto; }

/* ── Post title ── */
.post-title {
  font-family: var(--font-display);
  font-size: clamp(2.4rem, 5vw, 4rem);
  font-weight: 900; color: var(--text-bright);
  text-transform: uppercase; line-height: 0.95;
  letter-spacing: -0.01em; margin-bottom: 20px;
}

/* ── Author row ── */
.author-row {
  display: flex; align-items: center; gap: 12px; margin-bottom: 28px; flex-wrap: wrap;
}
.author-av {
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, var(--red), #7a0e1e);
  border: 2px solid rgba(200,16,46,0.3);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display); font-size: 15px; font-weight: 900;
  color: white; flex-shrink: 0;
}
.author-info { flex: 1; }
.author-name { font-size: 14px; font-weight: 600; color: var(--text-bright); font-family: var(--font-body); }
.author-role { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.author-badges { display: flex; gap: 6px; flex-wrap: wrap; }
.abadge {
  font-size: 9px; padding: 2px 8px; border-radius: 3px;
  font-weight: 700; letter-spacing: 0.07em;
  font-family: var(--font-display); text-transform: uppercase;
}
.ab-red  { background: rgba(200,16,46,0.12); color: var(--red2); border: 1px solid rgba(200,16,46,0.2); }
.ab-cyan { background: rgba(0,184,208,0.1);  color: var(--cyan); border: 1px solid rgba(0,184,208,0.18); }

/* ── Divider ── */
.post-divider {
  height: 1px;
  background: linear-gradient(90deg, var(--border2), transparent);
  margin: 4px 0 0;
}

/* ── Post body ── */
.post-content { padding: 32px 0 0; }

.post-body {
  font-size: 16px; color: rgba(255,255,255,0.65);
  font-family: var(--font-body); line-height: 1.85;
  margin-bottom: 40px;
}
.post-body :deep(p)           { margin-bottom: 18px; }
.post-body :deep(p:last-child){ margin-bottom: 0; }
.post-body :deep(strong)      { color: var(--text-bright); font-weight: 600; }
.post-body :deep(em)          { color: var(--cyan); font-style: normal; }
.post-body :deep(a)           { color: var(--cyan); text-decoration: underline; }
.post-body :deep(h2)          {
  font-family: var(--font-display); font-size: 22px; font-weight: 800;
  color: var(--text-bright); text-transform: uppercase; letter-spacing: 0.04em;
  margin: 28px 0 12px;
}
.post-body :deep(ul),
.post-body :deep(ol)          { padding-left: 22px; margin-bottom: 18px; }
.post-body :deep(li)          { margin-bottom: 8px; line-height: 1.65; }
.post-body :deep(blockquote)  {
  border-left: 3px solid var(--cyan); padding: 12px 18px;
  background: rgba(0,184,208,0.05); border-radius: 0 7px 7px 0;
  margin: 20px 0; font-style: italic; color: rgba(255,255,255,0.5);
}

/* Callouts — rendered via v-html, requires :deep() */
:deep(.post-callout) {
  border-radius: 9px;
  padding: 14px 18px;
  margin: 20px 0;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}
:deep(.post-callout--warning) {
  background: rgba(200, 16, 46, 0.06);
  border: 1px solid rgba(200, 16, 46, 0.18);
}
:deep(.post-callout--warning .callout-text strong) {
  color: #e8304a;
}
:deep(.post-callout--info) {
  background: rgba(0, 184, 208, 0.06);
  border: 1px solid rgba(0, 184, 208, 0.18);
}
:deep(.post-callout--info .callout-text strong) {
  color: #00b8d0;
}
:deep(.callout-icon) {
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 1px;
}
:deep(.callout-text) {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  font-family: 'Barlow', sans-serif;
  line-height: 1.65;
}

/* ── Post footer ── */
.post-footer {
  border-top: 1px solid var(--border); padding: 24px 0; margin-bottom: 48px;
  display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap;
}
.pf-left { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.pf-tag-label { font-size: 11px; color: var(--text-muted); font-family: var(--font-body); }
.pf-right { display: flex; gap: 8px; }

/* ── Buttons ── */
.btn {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 9px 20px; border-radius: var(--r-md);
  font-size: 13px; font-weight: 600; font-family: var(--font-body);
  cursor: pointer; border: none; transition: all 0.18s;
  text-decoration: none; letter-spacing: 0.02em;
}
.btn:hover { transform: translateY(-1px); }
.btn-ghost { background: rgba(255,255,255,0.04); border: 1px solid var(--border2); color: var(--text); }
.btn-ghost:hover { background: rgba(255,255,255,0.08); }
.btn-sm { padding: 7px 16px; font-size: 12px; }

/* ── Others section ── */
.others-section {
  border-top: 1px solid var(--border);
  background: var(--bg2);
}
.others-inner { padding: 40px 0 64px; }

.sh { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; }
.sh-title {
  font-family: var(--font-display); font-size: 16px; font-weight: 800;
  color: var(--text-bright); letter-spacing: 0.08em; text-transform: uppercase; white-space: nowrap;
}
.sh-title em { color: var(--cyan); font-style: normal; }
.sh-line { flex: 1; height: 1px; background: linear-gradient(90deg, var(--border2), transparent); }

.other-grid {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px;
}
.other-card {
  background: rgba(255,255,255,0.025); border: 1px solid var(--border);
  border-radius: 10px; padding: 16px; cursor: pointer;
  transition: all 0.2s; text-decoration: none; display: block;
}
.other-card:hover {
  border-color: var(--border2);
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.3);
}
.oc-tag {
  display: inline-block; font-size: 9px; padding: 2px 7px; border-radius: 3px;
  font-weight: 700; letter-spacing: 0.07em;
  font-family: var(--font-display); text-transform: uppercase; margin-bottom: 10px;
}
.oc-title   { font-size: 14px; font-weight: 600; color: var(--text-bright); font-family: var(--font-body); margin-bottom: 6px; line-height: 1.4; }
.oc-preview {
  font-size: 12px; color: rgba(255,255,255,0.3); font-family: var(--font-body);
  line-height: 1.5; margin-bottom: 10px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.oc-meta { font-size: 10px; color: var(--text-muted); font-family: var(--font-display); letter-spacing: 0.06em; }

@media (max-width: 700px) {
  .other-grid { grid-template-columns: 1fr; }
  .author-badges { display: none; }
  .post-date { display: none; }
}
</style>
