<template>
  <section class="music-tab">
    <div class="page-header">
      <div>
        <div class="page-title">Music / <em>Bangerfabrikken</em></div>
        <div class="page-sub">Administrer bangers via SoundCloud URL. Tittel og artwork hentes automatisk.</div>
      </div>
    </div>

    <div class="music-grid">
      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Spilleliste</span>
          <span class="panel-meta">
            {{ tracks.length }} banger{{ tracks.length !== 1 ? 's' : '' }} · dra for a sortere
          </span>
        </div>

        <div v-if="tracks.length === 0" class="no-tracks">
          <span class="no-tracks-mark">SC</span>
          <p>Ingen bangers enna. Legg til en til hoyre.</p>
        </div>

        <table v-else class="track-table">
          <thead>
            <tr>
              <th style="width:28px;"></th>
              <th>Banger</th>
              <th>Kilde</th>
              <th>Varighet</th>
              <th style="width:86px;">Featured</th>
              <th style="width:96px;">Handlinger</th>
            </tr>
          </thead>
          <tbody ref="sortableRef">
            <tr
              v-for="track in tracks"
              :key="track.id"
              class="track-row"
              :data-id="track.id"
            >
              <td><div class="drag-handle">|||</div></td>
              <td>
                <div class="track-cell">
                  <div class="track-thumb">
                    <img v-if="track.thumbnail_url" :src="track.thumbnail_url" :alt="track.title" />
                    <span v-else>SC</span>
                  </div>
                  <div>
                    <div class="track-name">{{ track.title }}</div>
                    <div class="track-artist">{{ track.author_name }}</div>
                  </div>
                </div>
              </td>
              <td>
                <a :href="track.url" target="_blank" rel="noopener noreferrer" class="sc-link">
                  <span class="sc-dot"></span>SoundCloud
                </a>
              </td>
              <td class="track-dur">{{ track.duration || '-' }}</td>
              <td>
                <span v-if="track.featured" class="badge b-orange">Featured</span>
                <button
                  v-else
                  class="btn btn-ghost btn-xs"
                  type="button"
                  @click="$emit('setFeatured', track.id)"
                >
                  Pin
                </button>
              </td>
              <td>
                <button class="btn btn-danger btn-xs" type="button" @click="$emit('deleteTrack', track.id)">
                  Slett
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="panel">
        <div class="panel-head">
          <span class="panel-title">Legg til banger</span>
        </div>
        <div class="add-form">
          <div class="auto-note">
            <span class="auto-note-mark">SC</span>
            <span>Lim inn en SoundCloud URL. Tittel, artist og cover hentes automatisk via serveren.</span>
          </div>

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
                class="btn btn-ghost btn-sm"
                type="button"
                :disabled="loading || !form.url"
                @click="handleFetch"
              >
                {{ loading ? 'Henter...' : 'Hent info' }}
              </button>
            </div>
            <div v-if="fetchError" class="form-error">{{ fetchError }}</div>
          </div>

          <transition name="fade">
            <div v-if="trackInfo" class="track-preview">
              <div class="preview-art">
                <img v-if="trackInfo.thumbnail_url" :src="trackInfo.thumbnail_url" :alt="trackInfo.title" />
                <span v-else>SC</span>
              </div>
              <div class="preview-info">
                <div class="preview-status">Hentet fra SoundCloud</div>
                <div class="preview-title">{{ trackInfo.title }}</div>
                <div class="preview-artist">{{ trackInfo.author_name }}</div>
              </div>
            </div>
          </transition>

          <transition name="fade">
            <div v-if="embedSrc" class="embed-preview">
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

          <template v-if="trackInfo">
            <div class="form-group">
              <label class="form-label">Tittel (overstyrer auto-hentet)</label>
              <input
                v-model="form.titleOverride"
                class="form-input"
                placeholder="La sta tom for a bruke SoundCloud-tittel"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Varighet</label>
              <input :value="form.duration || 'Henter...'" class="form-input readonly-input" readonly />
            </div>

            <div class="featured-row">
              <div>
                <div class="feat-label">Sett som featured</div>
                <div class="feat-sub">Vises overst pa Bangerfabrikken-siden</div>
              </div>
              <label class="toggle">
                <input v-model="form.featured" type="checkbox" />
                <span class="toggle-track"></span>
                <span class="toggle-thumb"></span>
              </label>
            </div>
          </template>

          <button
            class="btn btn-red submit-btn"
            type="button"
            :disabled="!trackInfo || submitting"
            @click="handleAdd"
          >
            {{ submitting ? 'Legger til...' : 'Legg til banger' }}
          </button>

          <div v-if="message" class="form-message" :class="{ success: messageSuccess, error: !messageSuccess }">
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
  tracks: {
    type: Array,
    default: () => [],
  },
  message: {
    type: String,
    default: '',
  },
  messageSuccess: {
    type: Boolean,
    default: false,
  },
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
const scIframe = ref(null);
const submitting = ref(false);
let sortableInstance = null;

const form = ref({
  url: '',
  titleOverride: '',
  duration: '',
  featured: false,
});

const embedSrc = computed(() => (
  form.value.url && trackInfo.value ? buildEmbedSrc(form.value.url) : ''
));

function ensureWidgetScript() {
  if (window.SC?.Widget || document.getElementById('soundcloud-widget-api')) {
    return;
  }

  const script = document.createElement('script');
  script.id = 'soundcloud-widget-api';
  script.src = 'https://w.soundcloud.com/player/api.js';
  script.async = true;
  document.head.appendChild(script);
}

function initSortable() {
  if (!sortableRef.value || sortableInstance) {
    return;
  }

  sortableInstance = new Sortable(sortableRef.value, {
    animation: 180,
    handle: '.drag-handle',
    ghostClass: 'sortable-ghost',
    dragClass: 'sortable-drag',
    onEnd() {
      const orderedIds = Array.from(sortableRef.value.querySelectorAll('tr'))
        .map((row, index) => ({
          id: Number(row.dataset.id),
          position: index,
        }))
        .filter((item) => Number.isFinite(item.id));

      emit('reorderTracks', orderedIds);
    },
  });
}

async function handleFetch() {
  if (!form.value.url) {
    return;
  }

  form.value.titleOverride = '';
  form.value.duration = '';
  form.value.featured = false;
  await fetchTrack(form.value.url);
}

async function onIframeLoad() {
  if (!trackInfo.value || !scIframe.value) {
    return;
  }

  const duration = await getDurationFromWidget(scIframe.value);
  form.value.duration = duration;
}

function resetForm() {
  form.value = {
    url: '',
    titleOverride: '',
    duration: '',
    featured: false,
  };
  trackInfo.value = null;
}

async function handleAdd() {
  if (!trackInfo.value) {
    return;
  }

  submitting.value = true;

  try {
    emit('addTrack', {
      url: form.value.url,
      title: form.value.titleOverride || trackInfo.value.title,
      author_name: trackInfo.value.author_name,
      thumbnail_url: trackInfo.value.thumbnail_url,
      duration: form.value.duration,
      featured: form.value.featured,
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
  nextTick(() => {
    if (props.tracks.length && !sortableInstance) {
      initSortable();
    }
  });
});
</script>

<style scoped>
.music-tab { padding: 0; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 24px; }
.page-title { font-family: 'Barlow Condensed', sans-serif; font-size: 28px; font-weight: 900; color: #eaf2ff; text-transform: uppercase; line-height: 1; margin-bottom: 5px; }
.page-title em { color: #00b8d0; font-style: normal; }
.page-sub { font-size: 13px; color: #3d5668; font-family: 'Barlow', sans-serif; }

.music-grid { display: grid; grid-template-columns: minmax(0, 1fr) 380px; gap: 18px; align-items: start; }
.panel { background: rgba(255,255,255,0.025); border: 1px solid rgba(255,255,255,0.11); border-radius: 12px; overflow: hidden; }
.panel-head { padding: 13px 18px; border-bottom: 1px solid rgba(255,255,255,0.07); background: rgba(255,255,255,0.02); display: flex; align-items: center; gap: 12px; }
.panel-title { font-family: 'Barlow Condensed', sans-serif; font-size: 13px; font-weight: 800; color: #eaf2ff; letter-spacing: 0.1em; text-transform: uppercase; flex: 1; }
.panel-meta { font-size: 11px; color: #3d5668; }

.no-tracks { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 40px; color: #3d5668; font-family: 'Barlow', sans-serif; font-size: 13px; font-style: italic; }
.no-tracks-mark { display: inline-flex; align-items: center; justify-content: center; width: 42px; height: 42px; border-radius: 10px; background: rgba(255,85,0,0.08); color: #ff5500; font-family: 'Barlow Condensed', sans-serif; font-weight: 900; letter-spacing: 0.08em; }

.track-table { width: 100%; border-collapse: collapse; }
.track-table th { padding: 9px 14px; text-align: left; font-size: 10px; color: #3d5668; letter-spacing: 0.1em; text-transform: uppercase; font-family: 'Barlow Condensed', sans-serif; border-bottom: 1px solid rgba(255,255,255,0.07); background: rgba(255,255,255,0.02); font-weight: 700; }
.track-table td { padding: 11px 14px; font-size: 13px; color: #b8ccd8; border-bottom: 1px solid rgba(255,255,255,0.07); font-family: 'Barlow', sans-serif; vertical-align: middle; }
.track-row:last-child td { border-bottom: none; }
.track-row:hover td { background: rgba(255,255,255,0.025); }
.drag-handle { color: #3d5668; cursor: grab; font-size: 14px; user-select: none; letter-spacing: -2px; }
.drag-handle:hover { color: #b8ccd8; }
.track-cell { display: flex; align-items: center; gap: 12px; }
.track-thumb { width: 40px; height: 40px; border-radius: 6px; background: #131e28; flex-shrink: 0; display: flex; align-items: center; justify-content: center; overflow: hidden; font-size: 11px; color: #ff5500; font-family: 'Barlow Condensed', sans-serif; font-weight: 800; }
.track-thumb img { width: 100%; height: 100%; object-fit: cover; }
.track-name { font-weight: 500; color: #eaf2ff; }
.track-artist { font-size: 11px; color: #3d5668; margin-top: 2px; }
.track-dur { font-size: 12px; color: #3d5668; font-family: 'Barlow Condensed', sans-serif; }
.sc-link { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; color: #ff5500; text-decoration: none; }
.sc-link:hover { text-decoration: underline; }
.sc-dot { width: 7px; height: 7px; border-radius: 50%; background: #ff5500; flex-shrink: 0; }

.add-form { padding: 18px; display: flex; flex-direction: column; gap: 14px; }
.auto-note { display: flex; align-items: flex-start; gap: 8px; padding: 9px 12px; border-radius: 6px; background: rgba(0,184,208,0.06); border: 1px solid rgba(0,184,208,0.14); font-size: 12px; color: #00b8d0; font-family: 'Barlow', sans-serif; line-height: 1.5; }
.auto-note-mark { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 6px; background: rgba(255,85,0,0.12); color: #ff5500; font-family: 'Barlow Condensed', sans-serif; font-size: 10px; font-weight: 900; }

.form-group { display: flex; flex-direction: column; }
.form-label { font-size: 10px; color: #3d5668; letter-spacing: 0.1em; text-transform: uppercase; font-family: 'Barlow Condensed', sans-serif; font-weight: 700; margin-bottom: 5px; }
.url-row { display: flex; gap: 8px; }
.form-input { flex: 1; width: 100%; background: #131e28; border: 1px solid rgba(255,255,255,0.11); border-radius: 7px; padding: 10px 13px; font-size: 13px; color: #eaf2ff; font-family: 'DM Sans', sans-serif; outline: none; transition: all 0.15s; }
.form-input:focus { border-color: #00b8d0; box-shadow: 0 0 0 3px rgba(0,184,208,0.1); }
.form-input::placeholder { color: #3d5668; }
.readonly-input { opacity: 0.65; }
.form-error { font-size: 12px; color: #e8304a; margin-top: 5px; }

.track-preview { display: flex; align-items: center; gap: 12px; padding: 12px 14px; border-radius: 8px; background: rgba(255,85,0,0.06); border: 1px solid rgba(255,85,0,0.15); }
.preview-art { width: 48px; height: 48px; border-radius: 7px; background: #131e28; flex-shrink: 0; display: flex; align-items: center; justify-content: center; overflow: hidden; font-size: 11px; color: #ff5500; font-family: 'Barlow Condensed', sans-serif; font-weight: 800; }
.preview-art img { width: 100%; height: 100%; object-fit: cover; }
.preview-status { font-size: 10px; color: #28b860; letter-spacing: 0.08em; font-family: 'Barlow Condensed', sans-serif; text-transform: uppercase; margin-bottom: 2px; }
.preview-title { font-size: 13px; font-weight: 600; color: #eaf2ff; font-family: 'Barlow', sans-serif; }
.preview-artist { font-size: 11px; color: #3d5668; }

.embed-preview { border-radius: 8px; overflow: hidden; border: 1px solid rgba(255,255,255,0.07); }
.embed-preview iframe { display: block; width: 100%; border: none; }

.featured-row { display: flex; align-items: center; justify-content: space-between; gap: 14px; padding: 11px 13px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.07); border-radius: 7px; }
.feat-label { font-size: 13px; color: #eaf2ff; font-family: 'Barlow', sans-serif; }
.feat-sub { font-size: 11px; color: #3d5668; margin-top: 2px; }

.toggle { position: relative; width: 40px; height: 22px; cursor: pointer; flex-shrink: 0; }
.toggle input { opacity: 0; width: 0; height: 0; position: absolute; }
.toggle-track { position: absolute; inset: 0; border-radius: 11px; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.11); transition: all 0.2s; }
.toggle input:checked + .toggle-track { background: rgba(0,184,208,0.25); border-color: rgba(0,184,208,0.45); }
.toggle-thumb { position: absolute; top: 3px; left: 3px; width: 14px; height: 14px; border-radius: 50%; background: #3d5668; transition: all 0.2s; pointer-events: none; }
.toggle input:checked ~ .toggle-thumb { left: 21px; background: #00b8d0; }

.submit-btn { width: 100%; justify-content: center; }
.submit-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; }

.badge { display: inline-block; font-size: 9px; padding: 3px 9px; border-radius: 4px; font-weight: 700; letter-spacing: 0.07em; font-family: 'Barlow Condensed', sans-serif; text-transform: uppercase; }
.b-orange { background: rgba(232,104,26,0.12); color: #e8681a; border: 1px solid rgba(232,104,26,0.22); }

.btn { display: inline-flex; align-items: center; gap: 7px; padding: 9px 18px; border-radius: 7px; font-size: 13px; font-weight: 600; font-family: 'Barlow', sans-serif; cursor: pointer; border: none; transition: all 0.18s; }
.btn:hover:not(:disabled) { transform: translateY(-1px); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-red { background: linear-gradient(145deg, #c8102e, #8a0e1e); color: white; }
.btn-ghost { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.11); color: #b8ccd8; }
.btn-ghost:hover:not(:disabled) { background: rgba(255,255,255,0.08); }
.btn-danger { background: rgba(200,16,46,0.1); color: #e8304a; border: 1px solid rgba(200,16,46,0.2); }
.btn-danger:hover:not(:disabled) { background: rgba(200,16,46,0.18); }
.btn-sm { padding: 6px 13px; font-size: 12px; }
.btn-xs { padding: 4px 10px; font-size: 11px; }

.form-message { padding: 10px 12px; border-radius: 7px; font-size: 12px; font-family: 'Barlow', sans-serif; }
.form-message.success { background: rgba(40,184,96,0.1); color: #28b860; border: 1px solid rgba(40,184,96,0.2); }
.form-message.error { background: rgba(200,16,46,0.1); color: #e8304a; border: 1px solid rgba(200,16,46,0.2); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 980px) {
  .music-grid { grid-template-columns: 1fr; }
}
</style>
