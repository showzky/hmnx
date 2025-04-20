<template>
  <div class="exclusive-player">
    <!-- Main container -->
    <div class="player-container">
      <!-- Left panel - Playlist -->
      <div class="playlist-panel">
        <h2 class="vip-title">Exclusive Selection</h2>
        <div class="playlist-scroll">
          <!-- Upload Section for Testing -->
          <div class="upload-section" v-if="canManageSongs">
            <!-- Hidden native file input -->
            <input type="file" id="song-upload" @change="handleFileUpload" hidden />
            <!-- Custom styled button that triggers the file input -->
            <label for="song-upload" class="custom-upload-btn">
              Upload Song
            </label>
            <div v-if="isUploadingSong" class="upload-progress-container">
              <div class="upload-progress-bar" :style="{ width: uploadProgress + '%' }"></div>
              <span class="upload-progress-text">{{ uploadProgress.toFixed(0) }}%</span>
            </div>
          </div>
          

          <div 
            v-for="(song, index) in songs" 
            :key="index" 
            class="playlist-item" 
            :class="{ active: currentSongIndex === index }"
            @click="playSong(index)"
          >
            <div class="song-number">{{ index + 1 }}</div>
            <div class="song-info">
              <div class="song-title">{{ song.title }}</div>
              <div class="song-artist">{{ song.artist }}</div>
            </div>
            <div class="song-duration">{{ song.duration }}</div>
            <button  
            v-if="canManageSongs" 
            class="delete-song-btn" 
            @click.stop="deleteSong(song.id)">
          
            <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
  
      <!-- Right panel - Player -->
      <!-- Only render this part if currentSong is defined -->
      <div class="main-player" v-if="currentSong">
        <!-- Album Art Section -->
        <div class="album-art" :style="{ backgroundImage: `url(${currentSong.art})` }">
          <div class="vip-overlay"></div>
          
        </div>
  
        <!-- Song Info -->
        <div class="song-details">
          <h1 class="song-title">{{ currentSong.title }}</h1>
          <p class="song-artist">{{ currentSong.artist }}</p>
        </div>
  
        <!-- Progress Bar -->
        <div class="progress-container" @click="seekAudio($event)">
          <div class="progress" :style="{ width: progress + '%' }"></div>
        </div>
        <div class="time-container">
          <span class="current-time">{{ currentTimeDisplay }}</span> /
          <span class="total-duration">{{ durationDisplay }}</span>
        </div>
  
        <!-- Controls -->
        <div class="player-controls">
          <button class="control-btn" @click="toggleShuffle">
            <i class="fas" :class="shuffle ? 'fa-random active' : 'fa-random'"></i>
          </button>
          <button class="control-btn" @click="prevSong">
            <i class="fas fa-step-backward"></i>
          </button>
          <button class="play-btn" @click="togglePlay">
            <i class="fas" :class="isPlaying ? 'fa-pause' : 'fa-play'"></i>
          </button>
          <button class="control-btn" @click="nextSong">
            <i class="fas fa-step-forward"></i>
          </button>
          <button class="control-btn" @click="toggleRepeat">
            <i class="fas" :class="repeat ? 'fa-redo active' : 'fa-redo'"></i>
          </button>
        </div>
  
        <!-- Volume Control Section -->
        <div class="volume-control" @mouseover="handleVolumeMouseOver" @mouseleave="handleVolumeMouseLeave">
          <!-- Volume Button: no mouse events here because container handles them -->
          <button class="volume-btn">
            <i class="fas fa-volume-up"></i>
          </button>
          <!-- Volume Slider Container: Shown based on 'showVolume' state -->
          <div v-show="showVolume" class="volume-slider-container">
            <input 
              type="range" 
              min="0" 
              max="100" 
              v-model="volume" 
              class="volume-slider" 
              @input="setVolume"
            >
          </div>
        </div>
      </div>
      <!-- Simple loading state when songs aren't loaded -->
      <div class="main-player" v-else>
        <div v-if="isLoadingSongs" class="loading-spinner"></div> <p v-else>Loading song...</p>
    </div>
    </div>
    <SnackBar
    ref="snackBar"
    message="Song deleted successfully!"
    type="success"
    :duration="3000"
  />

  </div>
</template>
  
<script>
import axios from '@/axios';
import { ref, computed } from 'vue';
import SnackBar from '@/components/SnackBar.vue'; // <-- IMPORT SNACKBAR

export default {
  components: {
    SnackBar, // <-- REGISTER SNACKBAR COMPONENT
  },
  data() {
    return {
      songs: [],
      currentTimeDisplay: '0:00',
      durationDisplay: '0:00',
      currentSongIndex: 0,
      audio: null,
      isPlaying: false,
      progress: 0,
      volume: 80,
      showVolume: false,
      repeat: false,
      shuffle: false,
      isLoadingSongs: true,
      uploadProgress: 0,
      isUploadingSong: false,
    };
  },
  computed: {
  userRoles() {
    const userData = localStorage.getItem('user');
    if (userData) {
      try {
        const user = JSON.parse(userData);
        return user.roles?.map(role => role.name.toLowerCase()) || [];
      } catch (e) {
        console.error("Error parsing user data:", e);
      }
    }
    return [];
  },
  canManageSongs() {
    return this.userRoles.includes('developer') || 
           this.userRoles.includes('admin') || 
           this.userRoles.includes('producer');
  },
  currentSong() {
    if (!this.songs || this.songs.length === 0) return undefined;
    return this.songs[this.currentSongIndex];
  }
},

  methods: {
    initializeAudio() {
      if (!this.currentSong) return;
      if (this.audio) {
        this.audio.pause();
        this.audio = null;
      }
      this.audio = new Audio(this.currentSong.url);
      this.audio.volume = this.volume / 100;
      this.audio.addEventListener('loadedmetadata', () => {
        this.durationDisplay = this.formatTime(this.audio.duration);
      });
      this.audio.addEventListener('timeupdate', () => {
        if (this.audio.duration) {
          this.progress = (this.audio.currentTime / this.audio.duration) * 100;
          this.currentTimeDisplay = this.formatTime(this.audio.currentTime);
        }
      });
      this.audio.addEventListener('ended', () => {
        if (this.repeat) {
          this.playSong(this.currentSongIndex);
        } else {
          this.nextSong();
        }
      });
    },
    togglePlay() {
      if (!this.audio) {
        this.initializeAudio();
      }
      if (this.isPlaying) {
        this.audio.pause();
      } else {
        this.audio.play().catch(err => console.error("Play error:", err));
      }
      this.isPlaying = !this.isPlaying;
    },
    playSong(index) {
      if (this.currentSongIndex === index && this.isPlaying) return;
      if (this.audio) {
        this.audio.pause();
      }
      this.currentSongIndex = index;
      this.initializeAudio();
      this.audio.play().catch(err => console.error("Play error:", err));
      this.isPlaying = true;
    },
    nextSong() {
      if (this.shuffle) {
        let randomIndex;
        do {
          randomIndex = Math.floor(Math.random() * this.songs.length);
        } while (randomIndex === this.currentSongIndex && this.songs.length > 1);
        this.playSong(randomIndex);
      } else {
        let index = this.currentSongIndex + 1;
        if (index >= this.songs.length) index = 0;
        this.playSong(index);
      }
    },
    prevSong() {
      let index = this.currentSongIndex - 1;
      if (index < 0) index = this.songs.length - 1;
      this.playSong(index);
    },
    setVolume() {
      if (this.audio) {
        this.audio.volume = this.volume / 100;
      }
    },
    toggleRepeat() {
      this.repeat = !this.repeat;
    },
    toggleShuffle() {
      this.shuffle = !this.shuffle;
    },
    handleVolumeMouseOver() {
      this.showVolume = true;
    },
    handleVolumeMouseLeave() {
      this.showVolume = false;
    },
    seekAudio(event) {
      const progressBarWidth = event.currentTarget.offsetWidth;
      const clickPositionX = event.offsetX;
      const clickPercentage = (clickPositionX / progressBarWidth) * 100;
      const newTime = (clickPercentage / 100) * this.audio.duration;
      this.audio.currentTime = newTime;
    },
    formatTime(timeInSeconds) {
      if (isNaN(timeInSeconds) || timeInSeconds < 0) {
        return '0:00';
      }
      const minutes = Math.floor(timeInSeconds / 60);
      const seconds = Math.floor(timeInSeconds % 60);
      const formattedSeconds = seconds < 10 ? `0${seconds}` : `${seconds}`;
      return `${minutes}:${formattedSeconds}`;
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) {
        console.log("No file selected");
        return;
      }
      const accessToken = localStorage.getItem('access_token');
      if (!accessToken) {
        console.error("No access token found. User might not be logged in.");
        alert("You must be logged in to upload songs.");
        return;
      }
      const formData = new FormData();
      formData.append('audio_file', file);
      this.isUploadingSong = true;
      this.uploadProgress = 0;
      const xhr = new XMLHttpRequest();
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          this.uploadProgress = (event.loaded / event.total) * 100;
        }
      };
      xhr.onloadstart = () => {
        this.uploadProgress = 0;
      };
      xhr.onload = () => {
        this.isUploadingSong = false;
        if (xhr.status >= 200 && xhr.status < 300) {
          const data = JSON.parse(xhr.responseText);
          console.log('File uploaded successfully:', data);
          this.fetchSongs();
        } else {
          let errorMessage = `Upload failed: ${xhr.status} - ${xhr.statusText}`;
          try {
            const errorData = JSON.parse(xhr.responseText);
            if (errorData && errorData.msg) {
              errorMessage += ` - ${errorData.msg}`;
            }
          } catch (e) {}
          console.error('Error uploading file:', errorMessage);
          alert(errorMessage);
        }
      };
      xhr.onerror = () => {
        this.isUploadingSong = false;
        console.error('Network error during file upload.');
        alert('File upload failed due to a network error.');
      };
      xhr.open('POST', `${import.meta.env.VITE_API_BASE_URL}/api/upload-song`);
      xhr.setRequestHeader('Authorization', `Bearer ${accessToken}`);
      xhr.send(formData);
    },
    fetchSongs() {
      this.isLoadingSongs = true;
      fetch(`${import.meta.env.VITE_API_BASE_URL}/api/songs`)
        .then(response => response.json())
        .then(data => {
          this.songs = data.songs;
          this.isLoadingSongs = false;
          if (this.songs.length > 0) {
            this.initializeAudio();
          }
        })
        .catch(error => {
          this.isLoadingSongs = false;
          console.error('Error fetching songs:', error);
        });
    },
    async deleteSong(songId) {
      const accessToken = localStorage.getItem('access_token');
      if (!accessToken) {
        alert("You must be logged in to delete songs.");
        return;
      }
      try {
        const response = await axios.delete(`${import.meta.env.VITE_API_BASE_URL}/api/delete-song/${songId}`, {
  headers: { Authorization: `Bearer ${accessToken}` }
});
        console.log("Song deleted successfully:", response.data.msg);
        this.songs = this.songs.filter(song => song.id !== songId);

        // === TRIGGER SNACKBAR NOTIFICATION AFTER DELETE ===
        if (this.snackBar) { // Access snackBar using 'this' in methods
          this.snackBar.showSnackBar();
        }

      } catch (error) {
        console.error("Error deleting song:", error.response ? error.response.data : error);
        alert("Failed to delete the song. Please try again.");
      }
    },
    action(type) {
      console.log(`Action triggered: ${type}`);
    }
  },
  mounted() {
    this.fetchSongs();
  },
  beforeUnmount() {
    if (this.audio) {
      this.audio.pause();
      this.audio = null;
    }
  },
  setup() {
    const snackBar = ref(null); // CREATE SNACKBAR REF

    return {
      snackBar, // RETURN SNACKBAR REF SO TEMPLATE AND METHODS CAN ACCESS IT
    };
  },
};
</script>

  
<style lang="scss">
.exclusive-player {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #2a2a3a 0%, #1a1a2a 100%);
  color: white;
  font-family: 'Arial', sans-serif;
  
  .player-container {
    width: 90%;
    max-width: 1200px;
    height: 80vh;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    backdrop-filter: blur(10px);
    display: flex;
    box-shadow: 0 0 30px rgba(0, 0, 0, 0.3);
    overflow: hidden;
  }
  
  .playlist-panel {
    width: 30%;
    background: rgba(0, 0, 0, 0.2);
    padding: 30px;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
  
    .vip-title {
      font-size: 1.5em;
      margin-bottom: 20px;
      color: #fff;
      text-transform: uppercase;
      letter-spacing: 2px;
      text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
    }
  
    .playlist-scroll {
      height: calc(100% - 60px);
      overflow-y: auto;
      scrollbar-width: thin;
      scrollbar-color: rgba(255,255,255,0.2) transparent;
  
      &::-webkit-scrollbar {
        width: 6px;
      }
  
      &::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.2);
        border-radius: 3px;
      }
    }
  
    .playlist-item {
      display: flex;
      align-items: center;
      padding: 15px;
      margin-bottom: 10px;
      border-radius: 10px;
      transition: all 0.3s ease;
      cursor: pointer;
  
      &:hover {
        background: rgba(255, 255, 255, 0.1);
      }
  
      &.active {
        background: linear-gradient(90deg, #7f00ff 0%, #e100ff 100%);
        box-shadow: 0 0 15px rgba(127, 0, 255, 0.3);
      }
  
      .song-number {
        width: 30px;
        opacity: 0.7;
      }
  
      .song-info {
        flex: 1;
        .song-title {
          font-size: 0.9em;
          font-weight: bold;
        }
        .song-artist {
          font-size: 0.8em;
          opacity: 0.7;
        }
      }
  
      .song-duration {
        opacity: 0.7;
        font-size: 0.9em;
      }
    }
  }
  
  .main-player {
    flex: 1;
    padding: 40px;
    display: flex;
    flex-direction: column;
    align-items: center;
  
    .album-art {
      width: 300px;
      height: 300px;
      border-radius: 15px;
      background-size: cover;
      background-position: center;
      position: relative;
      margin-bottom: 30px;
      box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
  
      .vip-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, rgba(127, 0, 255, 0.1) 0%, rgba(225, 0, 255, 0.05) 100%);
        border-radius: 15px;
      }
    }
  
    .song-details {
      text-align: center;
      margin-bottom: 30px;
      .song-title {
        font-size: 2em;
        margin-bottom: 10px;
        letter-spacing: 1px;
      }
      .song-artist {
        font-size: 1.2em;
        opacity: 0.8;
      }
    }
  
    .progress-container {
      width: 100%;
      height: 4px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 2px;
      margin-bottom: 30px;
      cursor: pointer;
  
      .progress {
        height: 100%;
        background: linear-gradient(90deg, #7f00ff 0%, #e100ff 100%);
        border-radius: 2px;
        transition: width 0.1s linear;
      }
    }
  
    .time-container {
      text-align: center;
      margin-top: 8px;
      font-size: 0.85em;
      color: rgba(rgb(255, 255, 255), 0.7);
    }
  
    .player-controls {
      display: flex;
      align-items: center;
      gap: 25px;
  
      .control-btn {
        background: none;
        border: none;
        color: white;
        font-size: 1.5em;
        cursor: pointer;
        transition: all 0.3s ease;
        opacity: 0.8;
  
        &:hover {
          opacity: 1;
          transform: scale(1.1);
          color: #e100ff;
        }
  
        .active {
          color: #7f00ff;
        }
      }
  
      .play-btn {
        background: linear-gradient(135deg, #7f00ff 0%, #e100ff 100%);
        border: none;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5em;
        cursor: pointer;
        box-shadow: 0 0 20px rgba(127, 0, 255, 0.3);
        transition: transform 0.3s ease;
  
        &:hover {
          transform: scale(1.1);
        }
      }
    }
  
    .volume-control {
      position: relative;
      margin-top: 30px;
  
      .volume-btn {
        background: none;
        border: none;
        color: white;
        font-size: 1.2em;
        cursor: pointer;
      }
  
      .volume-slider-container {
        position: absolute;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        padding: 10px;
        background: rgba(0, 0, 0, 0.7);
        border-radius: 8px;
  
        .volume-slider {
          -webkit-appearance: none;
          width: 100px;
          height: 4px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 2px;
  
          &::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 12px;
            height: 12px;
            background: #fff;
            border-radius: 50%;
            cursor: pointer;
          }
        }
      }
    }
  }
}
  
@media (max-width: 768px) {
  .player-container {
    flex-direction: column;
    height: auto !important;
  }
  
  .playlist-panel {
    width: 100% !important;
    height: 40vh;
  }
  
  .main-player {
    padding: 20px !important;
  }
  
  .album-art {
    width: 200px !important;
    height: 200px !important;
  }
}


.delete-song-btn {
  background: none;
  border: none;
  color: var(--accent);
  cursor: pointer;
  font-size: 1em;
  padding: 0.3rem;
  transition: color 0.3s ease;
}
.delete-song-btn:hover {
  color: #ff3e80;
}

.loading-spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid #fff;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 20px auto; /* Center the spinner */
}

.upload-progress-container {
  width: 100%;
  height: 10px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  margin-top: 10px;
  position: relative; /* For positioning the text */
}

.custom-upload-btn {
  display: inline-block;
  padding: 0.8rem 1.5rem;
  background-color: var(--accent); /* Use your theme color */
  color: var(--text);
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  text-align: center;
}

.custom-upload-btn:hover {
  background-color: #ff3e80; /* Adjust hover color as needed */
}

.upload-progress-bar {
  height: 100%;
  background-color: #7f00ff; /* Or your theme color */
  border-radius: 5px;
  width: 0%; /* Initial width */
  transition: width 0.1s linear;
}

.upload-progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 0.8em;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
