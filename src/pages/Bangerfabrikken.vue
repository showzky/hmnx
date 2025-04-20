<template>
  <div>
    <!-- Page Header: Centered -->
    <header class="page-header">
      <div class="header-content">
        <h1>Bangerfabrikken 🔥</h1>
        <p class="slogan">Lager bangere på bekostning av andre</p>
      </div>
    </header>

    <!-- Music Section -->
    <div class="music-page">
      <!-- Swiper Carousel for Album Covers -->
      <div class="swiper-container" ref="swiperContainer">
        <div class="swiper">
          <div class="swiper-wrapper" id="swiper-wrapper">
            <!-- Render each song as a slide -->
            <div
              v-for="(song, index) in songs"
              :key="index"
              class="swiper-slide"
              @click="currentSongIndex = index"
            >
              <img
                :src="song.cover"
                :alt="song.title"
                class="album-cover"
                @error="onImageError"
              />
              <div class="overlay">
                <h3>{{ song.title }}</h3>
                <p>{{ song.artist }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- SoundCloud Embed Container -->
      <!-- This container shows the SoundCloud player for the currently active track -->
      <div class="soundcloud-container">
        <div v-if="currentSong" class="soundcloud-embed">
          <iframe
            width="100%"
            height="166"
            scrolling="no"
            frameborder="no"
            :src="`https://w.soundcloud.com/player/?url=${currentSong.soundcloudUrl}&color=%23ff69b4&auto_play=false&hide_related=true&show_comments=false&show_user=false&show_reposts=false&show_teaser=false`">
          </iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, computed } from 'vue';
import axios from 'axios'; // Import axios to fetch the playlist
import Swiper from 'swiper';
import 'swiper/css'; // Core Swiper CSS
import 'swiper/css/effect-coverflow'; // Coverflow effect CSS

export default {
  name: 'Bangerfabrikken',
  setup() {
    // -----------------------------------------------------
    // Reactive State Variables
    // -----------------------------------------------------
    // 'songs' will hold the playlist fetched from your backend.
    const songs = ref([]);
    // 'currentSongIndex' tracks the active slide (song) in the carousel.
    const currentSongIndex = ref(0);
    // 'currentSong' computed property returns the currently active song,
    // or null if the songs array is empty.
    const currentSong = computed(() => {
      return songs.value.length ? songs.value[currentSongIndex.value] : null;
    });
    // Reference for the Swiper container element.
    const swiperContainer = ref(null);

    // -----------------------------------------------------
    // Fallback Image Handler
    // -----------------------------------------------------
    // If a song cover fails to load, use a default cover.
    const onImageError = (event) => {
      console.warn('Image failed to load, using default:', event.target.src);
      event.target.src = new URL('@/assets/albumcoversbs/default.jpg', import.meta.url).href;
    };

    // -----------------------------------------------------
    // Fetch Playlist Function
    // -----------------------------------------------------
    // Fetches the playlist from the backend endpoint '/api/playlist'
    // Expected response format: { songs: [ { title, artist, cover, soundcloudUrl, ... }, ... ] }
    const fetchPlaylist = async () => {
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/playlist`);

        songs.value = response.data.songs;
        console.log('Fetched playlist:', songs.value);
      } catch (error) {
        console.error('Error fetching playlist:', error);
      }
    };

    // -----------------------------------------------------
    // Initialize Swiper Carousel Function
    // -----------------------------------------------------
    // Initializes the Swiper carousel with coverflow effect after the DOM updates.
    const initSwiper = () => {
      if (swiperContainer.value) {
        const swiperEl = swiperContainer.value.querySelector('.swiper');
        console.log('Initializing Swiper on element:', swiperEl);
        if (swiperEl) {
          new Swiper(swiperEl, {
            effect: 'coverflow',
            grabCursor: true,
            centeredSlides: true,
            slidesPerView: 'auto',
            coverflowEffect: {
              rotate: 80,        // Strong rotation for dramatic tilt.
              stretch: -50,      // Negative stretch pulls slides closer together.
              depth: 500,        // Deeper perspective for 3D effect.
              modifier: 3,       // Amplifies the effect on the center slide.
              slideShadows: true,
            },
            on: {
              slideChange: function () {
                // Update the currentSongIndex when the active slide changes.
                currentSongIndex.value = this.activeIndex;
                console.log('Active slide index changed to:', currentSongIndex.value);
              },
            },
          });
        } else {
          console.error('Could not find the .swiper element inside swiperContainer');
        }
      } else {
        console.error('swiperContainer is not defined');
      }
    };

    // -----------------------------------------------------
    // Lifecycle Hook: onMounted
    // -----------------------------------------------------
    // Fetch the playlist and initialize the carousel after the DOM updates.
    onMounted(async () => {
      await fetchPlaylist();
      // Only initialize Swiper if there is at least one song.
      if (songs.value.length) {
        nextTick(() => {
          initSwiper();
        });
      }
    });

    // Return reactive properties and functions for use in the template.
    return { songs, currentSongIndex, currentSong, swiperContainer, onImageError };
  },
};
</script>




<style scoped>
/* Header styles: Center the header content vertically and horizontally */
.page-header {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 30vh; /* Adjust as needed */
  background: #1a1a1a;
  color: white;
  text-align: center;
  padding: 20px;
  margin-bottom: 20px;
}

.header-content h1 {
  font-size: 3rem;
  margin-bottom: 10px;
}

.slogan {
  font-size: 1.5rem;
}

/* Ensure the Swiper container has a defined height and perspective for 3D effect */
.swiper-container {
  width: 100%;
  height: 320px;
  perspective: 1500px; /* Required for 3D transforms */
}

/* (Other global styles for the carousel and embed are in your global CSS) */
</style>
