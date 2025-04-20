<template>
  <div class="music-player">
    <h1>{{ currentSong.title }}</h1>
    <p>{{ currentSong.artist }}</p>
    
    <!-- Audio element for playback -->
    <audio
      ref="audio"
      @timeupdate="updateProgress"
      @ended="handleEnded"
      @loadedmetadata="setDuration"
    ></audio>
    
    <!-- Progress Bar -->
    <input
      type="range"
      class="hmn-progress"
      v-model="progress"
      @input="seekSong"
    />
    
    <!-- Time Info -->
    <div class="time-info">
      <span>{{ formatTime(currentTime) }}</span>
      <span>-{{ formatTime(duration - currentTime) }}</span>
    </div>
    
    <!-- Playback Controls -->
    <div class="controls">
      <button @click="previousSong">
        <i class="fa-solid fa-backward-step"></i>
      </button>
      <button @click="togglePlay">
        <i :class="isPlaying ? 'fa-solid fa-pause' : 'fa-solid fa-play'"></i>
      </button>
      <button @click="nextSong">
        <i class="fa-solid fa-forward-step"></i>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue';

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
}

export default {
  name: 'MusicPlayer',
  props: {
    songs: {
      type: Array,
      required: true,
    },
    currentSongIndex: {
      type: Number,
      default: 0,
    },
  },
  setup(props) {
    const audio = ref(null);
    const currentTime = ref(0);
    const duration = ref(0);
    const progress = ref(0);
    const isPlaying = ref(false);

    // computed current song based on currentSongIndex prop
    const currentSong = computed(() => {
      return props.songs[props.currentSongIndex] || {};
    });

    const loadSong = () => {
      if (audio.value && currentSong.value.source) {
        audio.value.src = currentSong.value.source;
        audio.value.load();
        currentTime.value = 0;
        progress.value = 0;
      }
    };

    const togglePlay = () => {
      if (!audio.value.src) {
        loadSong();
      }
      if (isPlaying.value) {
        audio.value.pause();
      } else {
        audio.value.play().catch((error) => console.error(error));
      }
      isPlaying.value = !isPlaying.value;
    };

    const updateProgress = () => {
      currentTime.value = audio.value.currentTime;
      progress.value =
        duration.value > 0 ? (currentTime.value / duration.value) * 100 : 0;
    };

    const seekSong = (event) => {
      audio.value.currentTime = (event.target.value / 100) * duration.value;
    };

    const setDuration = () => {
      duration.value = audio.value.duration;
    };

    const handleEnded = () => {
      // When a song ends, you may choose to pause or trigger nextSong.
      // Here, we simply set isPlaying to false.
      isPlaying.value = false;
    };

    const nextSong = () => {
      // Emit an event or rely on parent's change.
      // In this example, we simply do nothing—song change is handled by the carousel.
      // Optionally, you can also implement manual next button functionality here.
      // For now, we pause playback.
      isPlaying.value = false;
    };

    const previousSong = () => {
      isPlaying.value = false;
    };

    // Watch for changes in the currentSongIndex prop
    watch(() => props.currentSongIndex, (newVal, oldVal) => {
      console.log('MusicPlayer: currentSongIndex changed from', oldVal, 'to', newVal);
      loadSong();
      // Auto-play the new song
      audio.value.play().catch((error) => console.error(error));
      isPlaying.value = true;
    });

    onMounted(() => {
      loadSong();
    });

    return {
      currentSong,
      currentTime,
      duration,
      progress,
      isPlaying,
      audio,
      togglePlay,
      updateProgress,
      seekSong,
      setDuration,
      handleEnded,
      nextSong,
      previousSong,
      formatTime,
    };
  },
};


</script>

<style scoped>
.music-player {
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 20px;
  max-width: 600px;
  color: wheat;
  margin: 2rem auto;
  border: 2px solid #ff69b4;
  box-shadow: 0 0 25px rgba(255, 105, 180, 0.6);
}

.hmn-progress {
  width: 100%;
  height: 5px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 5px;
  appearance: none;
  transition: background 0.3s ease;
}

.hmn-progress::-webkit-slider-thumb {
  appearance: none;
  width: 15px;
  height: 15px;
  background: #ff69b4;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.3s ease, background 0.3s ease;
}

.hmn-progress::-webkit-slider-thumb:hover {
  transform: scale(1.2);
  background: #ff85c1;
}

.controls {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 1rem;
}

.controls button {
  background: none;
  border: 2px solid #ff69b4;
  color: white;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.controls button:hover {
  transform: scale(1.15);
}

.time-info {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 1rem;
  color: white;
}
</style>
