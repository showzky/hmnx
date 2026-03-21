<template>
  <div class="bangerfabrikken">
    <section class="bf-hero">
      <div class="bf-hero-grid"></div>
      <div class="container bf-hero-inner">
        <div class="bf-hero-left">
          <div class="bf-eyebrow">
            <span class="bf-eyebrow-dot"></span>
            <span class="bf-eyebrow-text">§ 2.1 - Klagemuligheter: ingen</span>
          </div>
          <h1 class="bf-title">Banger<em>fabrikken</em> 🔥</h1>
          <p class="bf-desc">
            Lager bangere pa bekostning av andre. Offisiell musikkanal. Godkjent av ingen.
          </p>
        </div>

        <div class="bf-stats">
          <div class="bfs">
            <div class="bfs-val">{{ tracks.length }}</div>
            <div class="bfs-label">Bangers</div>
          </div>
          <div class="bfs">
            <div class="bfs-val gold">∞</div>
            <div class="bfs-label">Kvalitet</div>
          </div>
          <div class="bfs">
            <div class="bfs-val cyan">0</div>
            <div class="bfs-label">Klager</div>
          </div>
        </div>
      </div>
    </section>

    <div v-if="tracks.length" class="ticker-bar">
      <div class="ticker-label">Spilleliste</div>
      <div class="ticker-scroll">
        <div class="ticker-inner">
          <template v-for="copyIndex in 2" :key="copyIndex">
            <span
              v-for="track in tracks"
              :key="`${copyIndex}-${track.id}`"
              class="ticker-item"
            >
              <em>{{ track.title }}</em> - {{ track.author_name }}
              <span class="ticker-sep">·</span>
            </span>
          </template>
        </div>
      </div>
    </div>

    <div v-if="featuredTrack" class="np-bar">
      <div class="container np-inner">
        <div class="np-art">
          <img
            v-if="featuredTrack.thumbnail_url"
            :src="featuredTrack.thumbnail_url"
            :alt="featuredTrack.title"
          />
          <span v-else class="np-art-placeholder">SC</span>
        </div>
        <div class="np-info">
          <div class="np-live-row">
            <div class="np-live-dot"></div>
            <span class="np-live-label">Spiller na</span>
          </div>
          <div class="np-track-name">{{ featuredTrack.title }}</div>
          <div class="np-track-artist">{{ featuredTrack.author_name }}</div>
        </div>
        <div class="np-sc-badge">
          <span class="np-sc-dot"></span>
          via SoundCloud
        </div>
      </div>
    </div>

    <main class="bf-main">
      <div class="container">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Laster bangere...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <p>{{ error }}</p>
        </div>

        <div v-else-if="tracks.length === 0" class="empty-state">
          <div class="empty-icon">SC</div>
          <div class="empty-title">Ingen bangers enna</div>
          <div class="empty-sub">Whiskey69 jobber med saken. Antagelig.</div>
        </div>

        <template v-else>
          <div class="sh">
            <span class="sh-title">Alle <em>bangers</em></span>
            <div class="sh-line"></div>
            <span class="sh-count">{{ tracks.length }} spor</span>
          </div>

          <div class="banger-grid">
            <article
              v-for="track in tracks"
              :key="track.id"
              class="banger-card"
              :class="{ featured: track.featured }"
            >
              <div class="bc-top">
                <div class="bc-art">
                  <img v-if="track.thumbnail_url" :src="track.thumbnail_url" :alt="track.title" />
                  <span v-else>SC</span>
                </div>
                <div class="bc-info">
                  <div class="bc-title">{{ track.title }}</div>
                  <div class="bc-artist">{{ track.author_name }}</div>
                  <div class="bc-badges">
                    <span v-if="track.featured" class="badge b-red">Featured</span>
                    <a
                      :href="track.url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="sc-badge-link"
                    >
                      SoundCloud
                    </a>
                  </div>
                </div>
              </div>

              <div class="bc-embed">
                <iframe
                  :src="buildEmbedSrc(track.url)"
                  height="120"
                  scrolling="no"
                  frameborder="no"
                  allow="autoplay"
                ></iframe>
              </div>
            </article>
          </div>

          <div class="sh tracklist-head">
            <span class="sh-title">Full <em>spilleliste</em></span>
            <div class="sh-line"></div>
          </div>

          <div class="tracklist">
            <div class="tl-head">
              <span class="tl-title">Alle spor</span>
              <span class="tl-count">{{ tracks.length }} spor</span>
            </div>
            <div
              v-for="(track, index) in tracks"
              :key="track.id"
              class="tl-row"
              :class="{ playing: track.featured }"
            >
              <div class="tl-num" :class="{ active: track.featured }">
                {{ track.featured ? '▶' : index + 1 }}
              </div>
              <div class="tl-art">
                <img v-if="track.thumbnail_url" :src="track.thumbnail_url" :alt="track.title" />
                <span v-else>SC</span>
              </div>
              <div class="tl-info">
                <div class="tl-name" :class="{ active: track.featured }">{{ track.title }}</div>
                <div class="tl-artist">{{ track.author_name }}</div>
              </div>
              <span v-if="track.featured" class="badge b-red tl-badge">Featured</span>
              <div class="tl-dur">{{ track.duration || '-' }}</div>
            </div>
          </div>
        </template>
      </div>
    </main>
  </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue';
import api from '@/axios';
import { useSoundCloud } from '@/composables/useSoundCloud';

export default {
  name: 'Bangerfabrikken',
  setup() {
    const { buildEmbedSrc } = useSoundCloud();

    const tracks = ref([]);
    const loading = ref(true);
    const error = ref('');

    const featuredTrack = computed(() => (
      tracks.value.find(track => track.featured) || tracks.value[0] || null
    ));

    async function fetchTracks() {
      loading.value = true;
      error.value = '';

      try {
        const response = await api.get('/music');
        tracks.value = Array.isArray(response.data)
          ? [...response.data].sort((a, b) => a.position - b.position)
          : [];
      } catch (err) {
        console.error('Failed to fetch Bangerfabrikken tracks:', err);
        error.value = 'Kunne ikke laste bangere. Thomas har skylda.';
      } finally {
        loading.value = false;
      }
    }

    onMounted(fetchTracks);

    return {
      tracks,
      loading,
      error,
      featuredTrack,
      buildEmbedSrc,
    };
  },
};
</script>

<style scoped>
.bangerfabrikken {
  min-height: 100vh;
  background:
    radial-gradient(circle at top, rgba(0, 184, 208, 0.06), transparent 28%),
    linear-gradient(180deg, #06090f 0%, #0b1018 36%, #0a0f16 100%);
}

.container {
  width: min(calc(100% - 2.5rem), 1120px);
  margin: 0 auto;
}

.bf-hero {
  position: relative;
  overflow: hidden;
  padding: 48px 0 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  background: linear-gradient(180deg, #06090f, #0b1018);
}

.bf-hero-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(0, 184, 208, 0.022) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 184, 208, 0.022) 1px, transparent 1px);
  background-size: 52px 52px;
  mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.5), transparent);
}

.bf-hero-inner {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
}

.bf-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  margin-bottom: 14px;
  border-radius: 4px;
  background: rgba(255, 85, 0, 0.08);
  border: 1px solid rgba(255, 85, 0, 0.2);
}

.bf-eyebrow-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ff5500;
  box-shadow: 0 0 8px #ff5500;
  animation: blink 2.5s infinite;
}

.bf-eyebrow-text {
  color: #ff7733;
  font-size: 10px;
  letter-spacing: 0.1em;
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 600;
  text-transform: uppercase;
}

.bf-title {
  margin-bottom: 10px;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: clamp(3rem, 5vw, 5rem);
  font-weight: 900;
  color: #eaf2ff;
  text-transform: uppercase;
  line-height: 0.9;
  letter-spacing: -0.01em;
}

.bf-title em {
  color: #ff5500;
  font-style: normal;
}

.bf-desc {
  max-width: 480px;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.35);
  line-height: 1.8;
  font-family: 'Barlow', sans-serif;
}

.bf-stats {
  display: flex;
  gap: 16px;
  flex-shrink: 0;
  padding-bottom: 4px;
}

.bfs {
  min-width: 80px;
  padding: 14px 18px;
  text-align: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.11);
  border-radius: 10px;
}

.bfs-val {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 26px;
  font-weight: 900;
  color: #eaf2ff;
  line-height: 1;
}

.bfs-val.gold {
  color: #d89820;
}

.bfs-val.cyan {
  color: #00b8d0;
}

.bfs-label {
  margin-top: 3px;
  font-size: 10px;
  color: #3d5668;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-family: 'Barlow Condensed', sans-serif;
}

.ticker-bar {
  display: flex;
  align-items: center;
  overflow: hidden;
  padding: 8px 0;
  background: rgba(0, 0, 0, 0.35);
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

.ticker-label {
  flex-shrink: 0;
  padding: 0 1.5rem;
  color: #ff5500;
  font-size: 10px;
  letter-spacing: 0.14em;
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 700;
  text-transform: uppercase;
  white-space: nowrap;
}

.ticker-scroll {
  overflow: hidden;
  flex: 1;
}

.ticker-inner {
  display: inline-flex;
  white-space: nowrap;
  animation: ticker 30s linear infinite;
}

.ticker-item {
  margin-right: 8px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
}

.ticker-item em {
  color: rgba(255, 255, 255, 0.55);
  font-style: normal;
}

.ticker-sep {
  margin: 0 6px;
  color: #3d5668;
}

.np-bar {
  position: relative;
  background: #0f1720;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

.np-bar::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: #28b860;
  box-shadow: 0 0 12px #28b860;
}

.np-inner {
  display: flex;
  align-items: center;
  gap: 0;
  min-height: 72px;
}

.np-art {
  width: 72px;
  height: 72px;
  flex-shrink: 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #131e28;
}

.np-art img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.np-art-placeholder {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 20px;
  color: #ff5500;
}

.np-info {
  flex: 1;
  padding: 0 20px;
}

.np-live-row {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 4px;
}

.np-live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #28b860;
  box-shadow: 0 0 7px #28b860;
  animation: blink 2s infinite;
}

.np-live-label {
  font-size: 10px;
  color: #28b860;
  letter-spacing: 0.1em;
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 700;
  text-transform: uppercase;
}

.np-track-name {
  font-size: 17px;
  font-weight: 600;
  color: #eaf2ff;
  font-family: 'Barlow', sans-serif;
}

.np-track-artist {
  margin-top: 2px;
  font-size: 12px;
  color: #3d5668;
}

.np-sc-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  padding: 0 20px;
  font-size: 11px;
  color: #ff5500;
  font-family: 'Barlow', sans-serif;
  opacity: 0.7;
}

.np-sc-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ff5500;
}

.bf-main {
  padding: 32px 0 72px;
  background: transparent;
}

.sh {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.sh-title {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 18px;
  font-weight: 800;
  color: #eaf2ff;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
}

.sh-title em {
  color: #00b8d0;
  font-style: normal;
}

.sh-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.11), transparent);
}

.sh-count {
  font-size: 10px;
  color: #3d5668;
  font-family: 'Barlow Condensed', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.banger-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 28px;
}

.banger-card {
  overflow: hidden;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 12px;
  transition: all 0.2s;
}

.banger-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.11);
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.4);
}

.banger-card.featured {
  border-color: rgba(255, 85, 0, 0.3);
  box-shadow: 0 0 18px rgba(255, 85, 0, 0.08);
}

.bc-top {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
}

.bc-art {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: #131e28;
  color: #ff5500;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 15px;
  font-weight: 800;
}

.bc-art img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.bc-info {
  flex: 1;
  min-width: 0;
}

.bc-title {
  margin-bottom: 3px;
  font-size: 15px;
  font-weight: 600;
  color: #eaf2ff;
  font-family: 'Barlow', sans-serif;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bc-artist {
  margin-bottom: 7px;
  font-size: 12px;
  color: #3d5668;
}

.bc-badges {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.sc-badge-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  font-size: 10px;
  color: #ff5500;
  text-decoration: none;
  font-family: 'Barlow Condensed', sans-serif;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  background: rgba(255, 85, 0, 0.1);
  border: 1px solid rgba(255, 85, 0, 0.2);
  border-radius: 3px;
}

.bc-embed {
  border-top: 1px solid rgba(255, 255, 255, 0.07);
  background: rgba(0, 0, 0, 0.15);
}

.bc-embed iframe {
  display: block;
  width: 100%;
  border: none;
}

.badge {
  display: inline-block;
  padding: 3px 9px;
  font-size: 9px;
  border-radius: 4px;
  font-weight: 700;
  letter-spacing: 0.07em;
  font-family: 'Barlow Condensed', sans-serif;
  text-transform: uppercase;
}

.b-red {
  background: rgba(200, 16, 46, 0.12);
  color: #e8304a;
  border: 1px solid rgba(200, 16, 46, 0.22);
}

.tracklist-head {
  margin-top: 32px;
}

.tracklist {
  overflow: hidden;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 12px;
}

.tl-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  background: rgba(255, 255, 255, 0.02);
}

.tl-title {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 13px;
  font-weight: 800;
  color: #eaf2ff;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.tl-count {
  font-size: 11px;
  color: #3d5668;
}

.tl-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 11px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  transition: background 0.15s;
}

.tl-row:last-child {
  border-bottom: none;
}

.tl-row:hover {
  background: rgba(255, 255, 255, 0.03);
}

.tl-row.playing {
  background: rgba(255, 85, 0, 0.04);
}

.tl-num {
  width: 20px;
  flex-shrink: 0;
  text-align: center;
  font-size: 12px;
  color: #3d5668;
  font-family: 'Barlow Condensed', sans-serif;
}

.tl-num.active {
  color: #ff5500;
}

.tl-art {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 5px;
  background: #131e28;
  color: #ff5500;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 12px;
  font-weight: 800;
}

.tl-art img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.tl-info {
  flex: 1;
  min-width: 0;
}

.tl-name {
  font-size: 13px;
  font-weight: 500;
  color: #b8ccd8;
  font-family: 'Barlow', sans-serif;
}

.tl-name.active {
  color: #ff7733;
}

.tl-artist {
  font-size: 11px;
  color: #3d5668;
}

.tl-badge {
  margin-right: 8px;
}

.tl-dur {
  flex-shrink: 0;
  font-size: 12px;
  color: #3d5668;
  font-family: 'Barlow Condensed', sans-serif;
}

.loading-state,
.error-state,
.empty-state {
  padding: 64px 0;
  text-align: center;
  color: #3d5668;
  font-family: 'Barlow', sans-serif;
  font-size: 14px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  margin: 0 auto 16px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.07);
  border-top-color: #00b8d0;
  animation: spin 0.8s linear infinite;
}

.empty-icon {
  margin-bottom: 12px;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 36px;
  color: #ff5500;
  letter-spacing: 0.08em;
}

.empty-title {
  margin-bottom: 6px;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 18px;
  font-weight: 800;
  color: rgba(255, 255, 255, 0.2);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.empty-sub {
  font-size: 13px;
  color: #3d5668;
  font-style: italic;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.2; }
}

@keyframes ticker {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 900px) {
  .bf-hero-inner {
    flex-direction: column;
    align-items: flex-start;
  }

  .bf-stats {
    width: 100%;
  }

  .banger-grid {
    grid-template-columns: 1fr;
  }

  .np-inner {
    align-items: flex-start;
    gap: 14px;
    padding: 14px 0;
  }

  .np-sc-badge {
    padding: 0;
  }
}

@media (max-width: 640px) {
  .container {
    width: min(calc(100% - 1.5rem), 1120px);
  }

  .ticker-label {
    padding: 0 1rem;
  }

  .bf-title {
    font-size: 2.75rem;
  }

  .bf-desc {
    font-size: 14px;
  }

  .bf-stats {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
  }

  .bfs {
    min-width: 0;
    padding: 12px 10px;
  }

  .tl-row {
    gap: 10px;
    padding: 11px 12px;
  }

  .tl-badge {
    display: none;
  }
}
</style>
