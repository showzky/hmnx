<template>
  <section class="music-tab">

    <!-- Header -->
    <div class="sec-head mb24">
      <div>
        <div class="sec-title">Music / <em>Bangerfabrikken</em></div>
        <div class="sec-subtitle">Administrer bangers via SoundCloud URL. Tittel og artwork hentes automatisk.</div>
      </div>
    </div>

    <div class="music-grid">

      <!-- ── LEFT: PLAYLIST ── -->
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Spilleliste</span>
          <span class="panel-meta">{{ tracks.length }} banger{{ tracks.length !== 1 ? 's' : '' }} · dra for å sortere</span>
        </div>

        <!-- Empty state -->
        <div v-if="tracks.length === 0" class="empty-state">
          <div class="empty-icon">SC</div>
          <div class="empty-title">Ingen bangers ennå</div>
          <div class="empty-sub">Legg til en SoundCloud-banger via skjemaet til høyre.</div>
        </div>

        <!-- Track list -->
        <div v-else class="track-list" ref="sortableRef">
          <div
            v-for="(track, index) in tracks"
            :key="track.id"
            class="track-row"
            :class="{ 'track-featured': track.featured }"
            :data-id="track.id"
          >
            <!-- Drag + index -->
            <div class="track-left">
              <div class="drag-handle">⠿</div>
              <div class="track-num">{{ String(index + 1).padStart(2, '0') }}</div>
            </div>

            <!-- Artwork -->
            <div class="track-art">
              <img v-if="track.thumbnail_url" :src="track.thumbnail_url" :alt="track.title" />
              <span v-else class="art-fallback">SC</span>
            </div>

            <!-- Info -->
            <div class="track-info">
              <div class="track-name">{{ track.title }}</div>
              <div class="track-meta-row">
                <span class="track-artist">{{ track.author_name }}</span>
                <span class="track-sep">·</span>
                <a :href="track.url" target="_blank" rel="noopener noreferrer" class="sc-badge">
                  <span class="sc-dot"></span>SoundCloud
                </a>
              </div>
            </div>

            <!-- Duration -->
            <div class="track-dur">{{ track.duration || '—' }}</div>

            <!-- Featured -->
            <div class="track-feat">
              <span v-if="track.featured" class="feat-badge">
                <span class="feat-star">★</span> Featured
              </span>
              <button
                v-else
                class="btn btn-ghost btn-xs"
                type="button"
                @click="$emit('setFeatured', track.id)"
                title="Sett som featured"
              >
                Pin
              </button>
            </div>

            <!-- Delete -->
            <button class="btn btn-danger btn-xs track-delete" type="button" @click="$emit('deleteTrack', track.id)">
              Slett
            </button>
          </div>
        </div>
      </div>

      <!-- ── RIGHT: ADD FORM ── -->
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Legg til banger</span>
          <span class="sc-label"><span class="sc-dot-sm"></span>SoundCloud</span>
        </div>

        <div class="add-form">

          <!-- Auto-fetch note -->
          <div class="info-note">
            <span class="info-icon">ℹ</span>
            Lim inn en SoundCloud URL. Tittel, artist og cover hentes automatisk via serveren.
          </div>

          <!-- URL input -->
          <div class="form-group">
            <label class="form-label">SoundCloud URL</label>
            <div class="url-row">
              <input
                v-model="form.url"
                class="form-input"
                placeholder="https://soundcloud.com/artist/track-name"
                @keyup.enter="handleFetch"
              />
              <button
                class="btn btn-sc btn-sm"
                type="button"
                :disabled="loading || !form.url"
                @click="handleFetch"
              >
                {{ loading ? '…' : 'Hent info' }}
              </button>
            </div>
            <div v-if="fetchError" class="field-error">{{ fetchError }}</div>
          </div>

          <!-- Track preview card -->
          <transition name="fade">
            <div v-if="trackInfo" class="preview-card">
              <div class="preview-art">
                <img v-if="trackInfo.thumbnail_url" :src="trackInfo.thumbnail_url" :alt="trackInfo.title" />
                <span v-else class="art-fallback">SC</span>
              </div>
              <div class="preview-info">
                <div class="preview-status">✓ Hentet fra SoundCloud</div>
                <div class="preview-title">{{ trackInfo.title }}</div>
                <div class="preview-artist">{{ trackInfo.author_name }}</div>
              </div>
            </div>
          </transition>

          <!-- Embed player -->
          <transition name="fade">
            <div v-if="embedSrc" class="embed-wrap">
              <iframe
                ref="scIframe"
                :src="embedSrc"
                height="120"
                scrolling="no"
                frameborder="no"
                allow="autoplay"
                @load="onIframeLoad"
              ></iframe>
            </div>
          </transition>

          <!-- Extra fields after fetch -->
          <template v-if="trackInfo">
            <div class="form-group">
              <label class="form-label">Tittel <span class="form-label-note">(overskriver auto-hentet)</span></label>
              <input
                v-model="form.titleOverride"
                class="form-input"
                placeholder="La stå tom for å bruke SoundCloud-tittel"
              />
            </div>

            <div class="form-row-2">
              <div class="form-group">
                <label class="form-label">Varighet</label>
                <input :value="form.duration || 'Henter...'" class="form-input form-input-ro" readonly />
              </div>
            </div>

            <div class="featured-toggle">
              <div class="ft-info">
                <div class="ft-label">★ Sett som featured</div>
                <div class="ft-sub">Vises øverst på Bangerfabrikken-siden</div>
              </div>
              <label class="toggle">
                <input v-model="form.featured" type="checkbox" />
                <span class="toggle-track"></span>
                <span class="toggle-thumb"></span>
              </label>
            </div>
          </template>

          <!-- Submit -->
          <button
            class="btn btn-red submit-btn"
            type="button"
            :disabled="!trackInfo || submitting"
            @click="handleAdd"
          >
            {{ submitting ? 'Legger til…' : 'Legg til banger' }}
          </button>

          <!-- Status message -->
          <div v-if="message" class="status-msg" :class="{ success: messageSuccess, error: !messageSuccess }">
            {{ message }}
          </div>

        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import Sortable from 'sortablejs';
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import { useSoundCloud } from '@/composables/useSoundCloud';

const props = defineProps({
  tracks:         { type: Array,   default: () => [] },
  message:        { type: String,  default: '' },
  messageSuccess: { type: Boolean, default: false },
});

const emit = defineEmits(['addTrack', 'deleteTrack', 'setFeatured', 'reorderTracks']);

const {
  fetchTrack,
  buildEmbedSrc,
  getDurationFromWidget,
  trackInfo,
  loading,
  error: fetchError,
} = useSoundCloud();

const sortableRef = ref(null);
const scIframe    = ref(null);
const submitting  = ref(false);
let sortableInstance = null;

const form = ref({ url: '', titleOverride: '', duration: '', featured: false });

const embedSrc = computed(() => (
  form.value.url && trackInfo.value ? buildEmbedSrc(form.value.url) : ''
));

function ensureWidgetScript() {
  if (window.SC?.Widget || document.getElementById('soundcloud-widget-api')) return;
  const script = document.createElement('script');
  script.id  = 'soundcloud-widget-api';
  script.src = 'https://w.soundcloud.com/player/api.js';
  script.async = true;
  document.head.appendChild(script);
}

function initSortable() {
  if (!sortableRef.value || sortableInstance) return;
  sortableInstance = new Sortable(sortableRef.value, {
    animation: 180,
    handle: '.drag-handle',
    ghostClass: 'sortable-ghost',
    dragClass:  'sortable-drag',
    onEnd() {
      const orderedIds = Array.from(sortableRef.value.querySelectorAll('[data-id]'))
        .map((el, index) => ({ id: Number(el.dataset.id), position: index }))
        .filter(item => Number.isFinite(item.id));
      emit('reorderTracks', orderedIds);
    },
  });
}

async function handleFetch() {
  if (!form.value.url) return;
  form.value.titleOverride = '';
  form.value.duration = '';
  form.value.featured = false;
  await fetchTrack(form.value.url);
}

async function onIframeLoad() {
  if (!trackInfo.value || !scIframe.value) return;
  form.value.duration = await getDurationFromWidget(scIframe.value);
}

function resetForm() {
  form.value = { url: '', titleOverride: '', duration: '', featured: false };
  trackInfo.value = null;
}

async function handleAdd() {
  if (!trackInfo.value) return;
  submitting.value = true;
  try {
    emit('addTrack', {
      url:           form.value.url,
      title:         form.value.titleOverride || trackInfo.value.title,
      author_name:   trackInfo.value.author_name,
      thumbnail_url: trackInfo.value.thumbnail_url,
      duration:      form.value.duration,
      featured:      form.value.featured,
    });
    resetForm();
  } finally {
    submitting.value = false;
  }
}

onMounted(() => {
  ensureWidgetScript();
  nextTick(initSortable);
});

watch(() => props.tracks.length, () => {
  nextTick(() => { if (props.tracks.length && !sortableInstance) initSortable(); });
});
</script>

<style scoped>
/* ── Layout ── */
.music-tab { padding: 0; }
.music-grid { display: grid; grid-template-columns: minmax(0, 1fr) 360px; gap: 18px; align-items: start; }

/* ── Header (uses admin.css globals) ── */
.sec-head { display: flex; align-items: flex-start; justify-content: space-between; }
.sec-title { font-family: 'Barlow Condensed', sans-serif; font-size: 26px; font-weight: 900; color: var(--bright, #eaf2ff); text-transform: uppercase; letter-spacing: 0.02em; line-height: 1; margin-bottom: 4px; }
.sec-title em { color: var(--cyan, #00b8d0); font-style: normal; }
.sec-subtitle { font-size: 13px; color: var(--muted, #3d5668); font-family: 'Barlow', sans-serif; }
.mb24 { margin-bottom: 24px; }

/* ── Panel ── */
.panel { background: linear-gradient(180deg, rgba(20,27,36,0.78), rgba(16,23,32,0.86)); border: 1px solid rgba(255,255,255,0.11); border-radius: 10px; overflow: hidden; }
.panel-head { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.07); background: rgba(255,255,255,0.02); display: flex; align-items: center; justify-content: space-between; }
.panel-title { font-family: 'Barlow Condensed', sans-serif; font-size: 13px; font-weight: 800; color: #eaf2ff; letter-spacing: 0.1em; text-transform: uppercase; }
.panel-meta { font-size: 11px; color: #3d5668; }

/* ── SoundCloud label in header ── */
.sc-label { display: inline-flex; align-items: center; gap: 5px; font-size: 10px; color: #ff5500; font-family: 'Barlow Condensed', sans-serif; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
.sc-dot-sm { width: 6px; height: 6px; border-radius: 50%; background: #ff5500; flex-shrink: 0; }

/* ── Empty state ── */
.empty-state { padding: 48px 24px; text-align: center; }
.empty-icon { display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px; border-radius: 12px; background: rgba(255,85,0,0.08); color: #ff5500; font-family: 'Barlow Condensed', sans-serif; font-weight: 900; font-size: 14px; letter-spacing: 0.05em; margin-bottom: 12px; }
.empty-title { font-size: 14px; color: #b8ccd8; font-family: 'Barlow', sans-serif; font-weight: 600; margin-bottom: 4px; }
.empty-sub { font-size: 12px; color: #3d5668; font-family: 'Barlow', sans-serif; font-style: italic; }

/* ── Track rows ── */
.track-list { display: flex; flex-direction: column; }

.track-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  transition: background 0.15s;
  position: relative;
}
.track-row:last-child { border-bottom: none; }
.track-row:hover { background: rgba(255,255,255,0.025); }
.track-row.track-featured { background: rgba(216,152,32,0.04); border-left: 2px solid rgba(216,152,32,0.5); }
.track-row.track-featured:hover { background: rgba(216,152,32,0.07); }

/* Drag + number */
.track-left { display: flex; flex-direction: column; align-items: center; gap: 3px; flex-shrink: 0; width: 22px; }
.drag-handle { color: #2a3d4d; cursor: grab; font-size: 16px; line-height: 1; user-select: none; transition: color 0.15s; }
.drag-handle:hover { color: #b8ccd8; }
.track-num { font-size: 10px; color: #2a3d4d; font-family: 'Barlow Condensed', sans-serif; font-weight: 700; letter-spacing: 0.04em; }

/* Artwork — strictly 48×48 */
.track-art {
  width: 48px;
  height: 48px;
  min-width: 48px;
  min-height: 48px;
  max-width: 48px;
  max-height: 48px;
  border-radius: 7px;
  overflow: hidden;
  background: #0f1720;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.track-art img { width: 48px; height: 48px; object-fit: cover; display: block; }
.art-fallback { font-family: 'Barlow Condensed', sans-serif; font-size: 11px; font-weight: 900; color: #ff5500; letter-spacing: 0.04em; }

/* Track info */
.track-info { flex: 1; min-width: 0; }
.track-name { font-size: 13px; font-weight: 600; color: #eaf2ff; font-family: 'Barlow', sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 3px; }
.track-meta-row { display: flex; align-items: center; gap: 6px; }
.track-artist { font-size: 11px; color: #3d5668; font-family: 'Barlow', sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 120px; }
.track-sep { font-size: 10px; color: #1e3040; flex-shrink: 0; }
.sc-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 10px; color: #ff5500; font-family: 'Barlow Condensed', sans-serif; font-weight: 700; letter-spacing: 0.05em; text-decoration: none; flex-shrink: 0; }
.sc-badge:hover { text-decoration: underline; }
.sc-dot { width: 5px; height: 5px; border-radius: 50%; background: #ff5500; flex-shrink: 0; }

/* Duration */
.track-dur { font-size: 11px; color: #3d5668; font-family: 'Barlow Condensed', sans-serif; letter-spacing: 0.05em; flex-shrink: 0; min-width: 36px; text-align: center; }

/* Featured */
.track-feat { flex-shrink: 0; }
.feat-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 9px; padding: 3px 8px; border-radius: 4px; font-weight: 700; letter-spacing: 0.07em; font-family: 'Barlow Condensed', sans-serif; text-transform: uppercase; background: rgba(216,152,32,0.12); color: #d89820; border: 1px solid rgba(216,152,32,0.25); white-space: nowrap; }
.feat-star { font-size: 10px; }

/* Delete */
.track-delete { flex-shrink: 0; }

/* Drag ghost/drag */
.sortable-ghost { opacity: 0.3; background: rgba(0,184,208,0.05) !important; }
.sortable-drag { background: rgba(255,255,255,0.04) !important; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }

/* ── Add form ── */
.add-form { padding: 18px; display: flex; flex-direction: column; gap: 14px; }

.info-note { display: flex; align-items: flex-start; gap: 8px; padding: 9px 12px; border-radius: 6px; background: rgba(0,184,208,0.05); border: 1px solid rgba(0,184,208,0.12); font-size: 12px; color: rgba(0,184,208,0.8); font-family: 'Barlow', sans-serif; line-height: 1.5; }
.info-icon { font-size: 13px; flex-shrink: 0; margin-top: 1px; }

.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-label { font-size: 10px; color: #3d5668; letter-spacing: 0.1em; text-transform: uppercase; font-family: 'Barlow Condensed', sans-serif; font-weight: 700; }
.form-label-note { font-size: 9px; color: #2a3d4d; text-transform: none; letter-spacing: 0; font-weight: 400; }
.url-row { display: flex; gap: 8px; }
.form-input { flex: 1; width: 100%; background: #0f1720; border: 1px solid rgba(255,255,255,0.09); border-radius: 7px; padding: 10px 13px; font-size: 13px; color: #eaf2ff; font-family: 'DM Sans', sans-serif; outline: none; transition: all 0.15s; }
.form-input:focus { border-color: #00b8d0; box-shadow: 0 0 0 2px rgba(0,184,208,0.1); }
.form-input::placeholder { color: #2a3d4d; }
.form-input-ro { opacity: 0.55; cursor: default; }
.field-error { font-size: 11px; color: #e8304a; margin-top: 3px; font-family: 'Barlow', sans-serif; }

/* Track preview card */
.preview-card { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 8px; background: rgba(255,85,0,0.05); border: 1px solid rgba(255,85,0,0.14); }
.preview-art { width: 52px; height: 52px; min-width: 52px; border-radius: 7px; overflow: hidden; background: #0f1720; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.preview-art img { width: 52px; height: 52px; object-fit: cover; display: block; }
.preview-info { min-width: 0; }
.preview-status { font-size: 10px; color: #28b860; letter-spacing: 0.08em; font-family: 'Barlow Condensed', sans-serif; text-transform: uppercase; margin-bottom: 3px; }
.preview-title { font-size: 13px; font-weight: 600; color: #eaf2ff; font-family: 'Barlow', sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 2px; }
.preview-artist { font-size: 11px; color: #3d5668; font-family: 'Barlow', sans-serif; }

/* Embed player */
.embed-wrap { border-radius: 8px; overflow: hidden; border: 1px solid rgba(255,255,255,0.07); }
.embed-wrap iframe { display: block; width: 100%; border: none; }

/* Featured toggle */
.featured-toggle { display: flex; align-items: center; justify-content: space-between; gap: 14px; padding: 11px 13px; background: rgba(216,152,32,0.04); border: 1px solid rgba(216,152,32,0.14); border-radius: 7px; }
.ft-info { flex: 1; }
.ft-label { font-size: 13px; color: #eaf2ff; font-family: 'Barlow', sans-serif; font-weight: 500; margin-bottom: 2px; }
.ft-sub { font-size: 11px; color: #3d5668; font-family: 'Barlow', sans-serif; }

/* Toggle switch */
.toggle { position: relative; width: 40px; height: 22px; cursor: pointer; flex-shrink: 0; }
.toggle input { opacity: 0; width: 0; height: 0; position: absolute; }
.toggle-track { position: absolute; inset: 0; border-radius: 11px; background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.1); transition: all 0.2s; }
.toggle input:checked + .toggle-track { background: rgba(216,152,32,0.25); border-color: rgba(216,152,32,0.45); }
.toggle-thumb { position: absolute; top: 3px; left: 3px; width: 14px; height: 14px; border-radius: 50%; background: #3d5668; transition: all 0.2s; pointer-events: none; }
.toggle input:checked ~ .toggle-thumb { left: 21px; background: #d89820; box-shadow: 0 0 6px rgba(216,152,32,0.5); }

/* Buttons */
.btn { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 6px; font-size: 12px; font-weight: 600; font-family: 'Barlow', sans-serif; cursor: pointer; border: none; transition: all 0.15s; white-space: nowrap; }
.btn:hover:not(:disabled) { transform: translateY(-1px); }
.btn:disabled { opacity: 0.45; cursor: not-allowed; }
.btn-red { background: linear-gradient(145deg, #c8102e, #8a0e1e); color: white; box-shadow: 0 3px 12px rgba(200,16,46,0.25); }
.btn-red:hover:not(:disabled) { box-shadow: 0 5px 18px rgba(200,16,46,0.35); }
.btn-ghost { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1); color: #b8ccd8; }
.btn-ghost:hover:not(:disabled) { background: rgba(255,255,255,0.08); }
.btn-danger { background: rgba(200,16,46,0.08); color: #e8304a; border: 1px solid rgba(200,16,46,0.18); }
.btn-danger:hover:not(:disabled) { background: rgba(200,16,46,0.15); }
.btn-sc { background: rgba(255,85,0,0.1); color: #ff5500; border: 1px solid rgba(255,85,0,0.22); }
.btn-sc:hover:not(:disabled) { background: rgba(255,85,0,0.18); }
.btn-sm { padding: 7px 13px; font-size: 12px; }
.btn-xs { padding: 4px 10px; font-size: 11px; }

.submit-btn { width: 100%; justify-content: center; padding: 10px 18px; font-size: 13px; }

/* Status message */
.status-msg { padding: 9px 12px; border-radius: 6px; font-size: 12px; font-family: 'Barlow', sans-serif; }
.status-msg.success { background: rgba(40,184,96,0.08); color: #28b860; border: 1px solid rgba(40,184,96,0.18); }
.status-msg.error { background: rgba(200,16,46,0.08); color: #e8304a; border: 1px solid rgba(200,16,46,0.18); }

/* Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* Responsive */
@media (max-width: 980px) {
  .music-grid { grid-template-columns: 1fr; }
}
</style>
