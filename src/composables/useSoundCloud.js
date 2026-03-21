import { ref } from 'vue';
import api from '@/axios';

export function useSoundCloud() {
  const trackInfo = ref(null);
  const loading = ref(false);
  const error = ref(null);

  async function fetchTrack(soundcloudUrl) {
    if (!soundcloudUrl || !soundcloudUrl.includes('soundcloud.com')) {
      error.value = 'Ikke en gyldig SoundCloud URL';
      trackInfo.value = null;
      return null;
    }

    loading.value = true;
    error.value = null;
    trackInfo.value = null;

    try {
      const response = await api.get('/soundcloud/oembed', {
        params: { url: soundcloudUrl },
      });
      trackInfo.value = response.data;
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.error || 'Kunne ikke hente info fra SoundCloud';
      trackInfo.value = null;
      return null;
    } finally {
      loading.value = false;
    }
  }

  function buildEmbedSrc(soundcloudUrl, options = {}) {
    const params = new URLSearchParams({
      url: soundcloudUrl,
      color: options.color ?? '%23ff5500',
      inverse: options.inverse ?? 'true',
      auto_play: options.autoPlay ?? 'false',
      show_user: options.showUser ?? 'true',
      show_reposts: 'false',
      show_teaser: 'false',
      visual: options.visual ?? 'false',
    });

    return `https://w.soundcloud.com/player/?${params.toString()}`;
  }

  function getDurationFromWidget(iframeEl) {
    return new Promise((resolve) => {
      try {
        if (!window.SC || !window.SC.Widget || !iframeEl) {
          resolve('');
          return;
        }

        const widget = window.SC.Widget(iframeEl);
        const timeout = window.setTimeout(() => resolve(''), 6000);

        widget.bind(window.SC.Widget.Events.READY, () => {
          widget.getCurrentSound((sound) => {
            window.clearTimeout(timeout);
            if (!sound?.duration) {
              resolve('');
              return;
            }

            const totalSeconds = Math.floor(sound.duration / 1000);
            const minutes = Math.floor(totalSeconds / 60);
            const seconds = String(totalSeconds % 60).padStart(2, '0');
            resolve(`${minutes}:${seconds}`);
          });
        });
      } catch {
        resolve('');
      }
    });
  }

  return {
    trackInfo,
    loading,
    error,
    fetchTrack,
    buildEmbedSrc,
    getDurationFromWidget,
  };
}
